import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "src"))  # the converters live in src/

from bpmn_mermaid import bpmn_to_mermaid

SOURCE = os.path.join(BASE, "bpmn")
TARGET = os.path.join(BASE, "mermaid_js")


def main():
    tasks = sorted(d for d in os.listdir(SOURCE) if os.path.isdir(os.path.join(SOURCE, d)))
    for task in tasks:
        source_dir = os.path.join(SOURCE, task)
        target_dir = os.path.join(TARGET, task)
        os.makedirs(target_dir, exist_ok=True)

        files = sorted(os.listdir(source_dir))
        for file in files:
            if file.endswith(".xml"):
                mermaid_file = os.path.join(target_dir, file.split(".")[0] + ".md")  # 0.bpmn2.xml -> 0.md
                with open(mermaid_file, "w") as f:
                    f.write(bpmn_to_mermaid(os.path.join(source_dir, file)))
            elif file.endswith(".quality.txt"):
                shutil.copy2(os.path.join(source_dir, file), os.path.join(target_dir, file))

        print(f"{task}: {sum(f.endswith('.xml') for f in files)} models")


if __name__ == "__main__":
    main()
