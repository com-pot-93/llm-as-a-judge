import json
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "src"))  # the converters live in src/

from bpmn_json import bpmn_to_json

SOURCE = os.path.join(BASE, "bpmn")
TARGET = os.path.join(BASE, "simple_json")


def main():
    tasks = sorted(d for d in os.listdir(SOURCE) if os.path.isdir(os.path.join(SOURCE, d)))
    for task in tasks:
        source_dir = os.path.join(SOURCE, task)
        target_dir = os.path.join(TARGET, task)
        os.makedirs(target_dir, exist_ok=True)

        files = sorted(os.listdir(source_dir))
        for file in files:
            if file.endswith(".xml"):
                json_file = os.path.join(target_dir, file.split(".")[0] + ".json")  # 0.bpmn2.xml -> 0.json
                with open(json_file, "w") as f:
                    json.dump(bpmn_to_json(os.path.join(source_dir, file)), f, indent=2)
            elif file.endswith(".quality.txt"):
                shutil.copy2(os.path.join(source_dir, file), os.path.join(target_dir, file))

        print(f"{task}: {sum(f.endswith('.xml') for f in files)} models")


if __name__ == "__main__":
    main()
