### prints the number of BPMN models (.xml files) for each example (subdirectory of bpmn/)
### with -m full, also prints the quality values of the models, ordered by model number:  E_j01: 11 [5, 0, 3.5, ...]


import argparse
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(BASE, "bpmn")


def quality(example_dir, model):
    """Quality value of a model (e.g. 5 or 3.5), or None if its quality file is missing."""
    path = os.path.join(example_dir, model + ".quality.txt")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        value = float(f.read().strip())
    return int(value) if value.is_integer() else value


def main():
    parser = argparse.ArgumentParser(description="Count the BPMN models for each example in bpmn/.")
    parser.add_argument("-m", "--mode", choices=["count", "full"], default="count",
                        help="count: number of models only, full: also the list of quality values")
    args = parser.parse_args()

    examples = sorted(d for d in os.listdir(SOURCE) if os.path.isdir(os.path.join(SOURCE, d)))
    total = 0
    for example in examples:
        example_dir = os.path.join(SOURCE, example)
        # model numbers from the file names (0.bpmn2.xml -> 0), in the order 0, 1, 2, ..., 10
        models = sorted((f.split(".")[0] for f in os.listdir(example_dir) if f.endswith(".xml")), key=int)
        total += len(models)
        line = f"{example}: {len(models)}"
        if args.mode == "full":
            line += f" {[quality(example_dir, m) for m in models]}"
        print(line)
    print(f"total: {total} models in {len(examples)} examples")


if __name__ == "__main__":
    main()
