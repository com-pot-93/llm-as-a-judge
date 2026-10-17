import sys
import xml.etree.ElementTree as ET

from bpmn_json import bpmn_to_json, tag

GATEWAY_MARKERS = {
    "exclusiveGateway": "x",
    "parallelGateway": "+",
    "inclusiveGateway": "o",
    "complexGateway": "*",
    "eventBasedGateway": "e",
}


def containers(path, model):
    """Maps each flow node id to the "pool - lane" it belongs to (innermost lane for nested lanes).
    Also returns the ids of the pools that contain flow nodes, i.e. that are not empty."""
    root = ET.parse(path).getroot()
    pool_of_process = {
        p.get("processRef"): p.get("id") for c in root if tag(c) == "collaboration" for p in c if tag(p) == "participant"
    }
    pool_names = {pool["id"]: pool["name"] for pool in model["pools"]}
    node_ids = {n["id"] for n in model["tasks"] + model["events"] + model["gateways"]}

    names, filled = {}, set()
    for process in (p for p in root if tag(p) == "process"):
        pool_id = pool_of_process.get(process.get("id"), process.get("id"))
        for node in process.iter():
            if node.get("id") in node_ids:
                names[node.get("id")] = [pool_names.get(pool_id, "")]
                filled.add(pool_id)
    for pool in model["pools"]:
        for lane in pool["lanes"]:  # child lanes come after their parent lane, so the innermost one wins
            for ref in lane["elemRefs"]:
                if ref in names:
                    names[ref] = names[ref][:1] + [lane["name"]]
    return {node_id: " - ".join(filter(None, n)) for node_id, n in names.items()}, filled


def shape(node, container=""):
    """Mermaid shape of a node: ("task"), (("event")), ((("endEvent"))), {"gateway"}, ["pool"].
    The pool and lane of the node are appended to its label in [], e.g. ("Write job application [Applicant - Lane]").
    Labels are quoted, so that the [] are valid mermaid.js."""
    label = node.get("name") or node["type"]
    if node["type"] in GATEWAY_MARKERS:
        label = " ".join([GATEWAY_MARKERS[node["type"]], node.get("name", "")]).strip()
    if container:
        label = f"{label} [{container}]"
    if node["type"] in GATEWAY_MARKERS:
        return f'{{"{label}"}}'
    if node["type"] == "endEvent":
        return f'((("{label}")))'
    if node["type"].endswith("Event"):
        return f'(("{label}"))'
    if node["type"] in ("pool", "collapsedPool"):
        return f'["{label}"]'
    return f'("{label}")'


def flow_order(nodes, flows):
    """Orders node ids so that each node comes before its successors (loops are cut at the back edge)."""
    successors = {node_id: [] for node_id in nodes}
    has_incoming = set()
    for flow in flows:
        successors[flow["sourceRef"]].append(flow["targetRef"])
        has_incoming.add(flow["targetRef"])

    visited, postorder = set(), []

    def visit(node_id):
        visited.add(node_id)
        for successor in reversed(successors[node_id]):
            if successor not in visited:
                visit(successor)
        postorder.append(node_id)

    roots = [n for n in nodes if n not in has_incoming] + list(nodes)  # all others in case of unreachable cycles
    for node_id in reversed(roots):
        if node_id not in visited:
            visit(node_id)
    return list(reversed(postorder))


def bpmn_to_mermaid(path):
    """Converts a BPMN XML file into the mermaid flowchart text."""
    model = bpmn_to_json(path)
    container, filled = containers(path, model)

    nodes = {n["id"]: n for n in model["tasks"] + model["events"] + model["gateways"]}
    for pool in model["pools"]:  # a pool without any flow nodes is drawn as a collapsed pool
        nodes[pool["id"]] = {**pool, "type": "pool" if pool["id"] in filled else "collapsedPool"}

    flows = [(f, "-->", f.get("condition", "")) for f in model["sequenceFlows"]]
    flows += [(f, "-.->", f.get("label", "")) for f in model["messageFlows"]]
    flows = [flow for flow in flows if flow[0]["sourceRef"] in nodes and flow[0]["targetRef"] in nodes]

    number = {node_id: i for i, node_id in enumerate(flow_order(nodes, [f for f, _, _ in flows]))}

    def text(node_id):
        node = nodes[node_id]
        return f"{number[node_id]}:{node['type']}:{shape(node, container.get(node_id, ''))}"

    lines = ["graph LR"]
    for flow, arrow, label in sorted(flows, key=lambda f: (number[f[0]["sourceRef"]], number[f[0]["targetRef"]])):
        label = f' |"{label}"|' if label else ""
        lines.append(f"  {text(flow['sourceRef'])} {arrow}{label} {text(flow['targetRef'])}")
    return "\n".join(lines)


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print(bpmn_to_mermaid(path))
