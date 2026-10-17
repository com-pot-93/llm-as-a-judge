### prints the few-shot prompt produced by generate_prompt_gpt (src/human_evaluation.py) for one representation,
### as the list of system / user / assistant messages. No LLM is called.
###
###   python show_few_shot_prompt.py --representation mermaid_js      (or: -r mermaid_js)
###   python show_few_shot_prompt.py -r bpmn --max-chars 0             (0 = print the messages in full)


import argparse
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "src"))  # human_evaluation lives in src/

from human_evaluation import EXAMPLES_DIR, generate_prompt_gpt


def main():
    parser = argparse.ArgumentParser(description="Show the GPT few-shot prompt for a representation.")
    parser.add_argument("-r", "--representation", required=True, choices=sorted(os.listdir(EXAMPLES_DIR)))
    parser.add_argument("--max-chars", type=int, default=500,
                        help="truncate each message to this many characters (default 500, 0 = no truncation)")
    args = parser.parse_args()

    system_prompt, user_prompts, assistant_prompts = generate_prompt_gpt(args.representation)
    messages = [("system", system_prompt)]
    for user_prompt, assistant_prompt in zip(user_prompts, assistant_prompts):
        messages += [("user", user_prompt), ("assistant", assistant_prompt)]

    for role, content in messages:
        shown = content if not args.max_chars or len(content) <= args.max_chars else (
            content[: args.max_chars] + f"\n... [{len(content) - args.max_chars} more characters]")
        print(f"===== {role} ({len(content)} characters) =====")
        print(shown)
        print()


if __name__ == "__main__":
    main()
