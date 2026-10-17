import json
import re
import sys
import xml.etree.ElementTree as ET

ACTIVITIES = {"task", "subProcess", "callActivity", "transaction", "adHocSubProcess"}


def tag(node):
    """Local tag name without the XML namespace."""
    return node.tag.rsplit("}", 1)[-1]


def clean(label):
    """Removes special characters from a label, e.g. "Start job (probation phase)" -> "Start job probation phase"."""
    return " ".join(re.sub(r"[^\w\s]|_", " ", label).split())


def name(node):
    return clean(node.get("name", ""))


def add_flow_elements(container, model, lanes):
    """Adds tasks, events, gateways, sequence flows and lanes of a process (or subprocess)."""
    for node in container:
        kind = tag(node)
        children = [tag(c) for c in node]
        if kind in ACTIVITIES or kind.endswith("Task"):
            task = {"id": node.get("id"), "name": name(node), "type": kind}
            loop = next((c for c in children if c.endswith("LoopCharacteristics")), None)
            if loop:
                task["loopCharacteristics"] = loop
            model["tasks"].append(task)
            add_flow_elements(node, model, lanes)  # expanded subprocesses contain their own elements
        elif kind.endswith("Event"):
            event = {"id": node.get("id"), "name": name(node), "type": kind}
            definitions = [c for c in children if c.endswith("EventDefinition")]
            if definitions:
                event["eventDefinitions"] = definitions
            if node.get("attachedToRef"):
                event["attachedToRef"] = node.get("attachedToRef")
            model["events"].append(event)
        elif kind.endswith("Gateway"):
            gateway = {"id": node.get("id"), "type": kind}
            if name(node):
                gateway["name"] = name(node)
            model["gateways"].append(gateway)
        elif kind == "sequenceFlow":
            flow = {"id": node.get("id"), "sourceRef": node.get("sourceRef"), "targetRef": node.get("targetRef")}
            if name(node):
                flow["condition"] = name(node)
            model["sequenceFlows"].append(flow)
        elif kind == "laneSet":
            add_lanes(node, lanes)


def add_lanes(lane_set, lanes):
    """Adds the lanes of a (possibly nested) laneSet with the elements they contain."""
    for lane in lane_set:
        if tag(lane) == "lane":
            refs = [ref.text.strip() for ref in lane if tag(ref) == "flowNodeRef" and ref.text]
            lanes.append({"id": lane.get("id"), "name": name(lane), "elemRefs": refs})
            for child in lane:
                if tag(child) == "childLaneSet":
                    add_lanes(child, lanes)


def bpmn_to_json(path):
    """Converts a BPMN XML file into the simplified JSON model."""
    root = ET.parse(path).getroot()
    model = {"tasks": [], "events": [], "gateways": [], "pools": [], "sequenceFlows": [], "messageFlows": []}

    pool_of_process = {}
    for collaboration in (c for c in root if tag(c) == "collaboration"):
        for node in collaboration:
            if tag(node) == "participant":
                pool = {"id": node.get("id"), "name": name(node), "lanes": []}
                model["pools"].append(pool)
                pool_of_process[node.get("processRef")] = pool
            elif tag(node) == "messageFlow":
                flow = {"id": node.get("id"), "sourceRef": node.get("sourceRef"), "targetRef": node.get("targetRef")}
                if name(node):
                    flow["label"] = name(node)
                model["messageFlows"].append(flow)

    for process in (p for p in root if tag(p) == "process"):
        lanes = []
        add_flow_elements(process, model, lanes)
        if lanes:
            pool = pool_of_process.get(process.get("id"))
            if pool is None:  # lanes without a collaboration: the process itself is the pool
                pool = {"id": process.get("id"), "name": name(process), "lanes": []}
                model["pools"].append(pool)
            pool["lanes"].extend(lanes)

    return model


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print(json.dumps(bpmn_to_json(path), indent=2))
