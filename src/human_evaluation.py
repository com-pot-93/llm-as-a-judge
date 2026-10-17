# from llm_connect.ask_models import ask_gpt
import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLES_DIR = os.path.join(SRC_DIR, "examples")
# each example is a model file <name>.<ext>, its text description <name>_text.txt and its quality <name>.txt
EXAMPLE_NAMES = ["good", "middle", "bad"]


def read(path):
    with open(path, "r") as file:
        return file.read().strip()


SYSTEM_PROMPT = read(os.path.join(SRC_DIR, "prompts", "human_evaluation.txt"))
# appended to the system prompt only when the examples are used
EXAMPLES_PROMPT = read(os.path.join(SRC_DIR, "prompts", "human_evaluation_examples.txt"))


def system_prompt(examples):
    return f"{SYSTEM_PROMPT}\n\n{EXAMPLES_PROMPT}" if examples else SYSTEM_PROMPT


def format_input(text, model):
    """Input of the judge: the text description and the process model. Use it for the examples and the actual query."""
    return f"Process description:\n{text}\n\nProcess model:\n{model}"


def load_examples(representation):
    """Loads the (input, quality) pairs from examples/<representation>/, e.g. representation = "bpmn", "simple_json" or "mermaid_js".
    The input combines the text description and the process model (see format_input)."""
    directory = os.path.join(EXAMPLES_DIR, representation)
    if not os.path.isdir(directory):
        raise ValueError(f"unknown representation {representation!r}, expected one of {sorted(os.listdir(EXAMPLES_DIR))}")

    examples = []
    for name in EXAMPLE_NAMES:
        model_file = next(f for f in os.listdir(directory) if f.startswith(name + ".") and not f.endswith(".txt"))
        model = read(os.path.join(directory, model_file))
        text = read(os.path.join(directory, name + "_text.txt"))
        quality = read(os.path.join(directory, name + ".txt"))
        examples.append((format_input(text, model), quality))
    return examples


def generate_prompt_gemini(representation, examples=True):
    """System prompt and example strings; with examples=False only the system prompt (and no examples)."""
    if not examples:
        return system_prompt(False), []
    example_strings = [f"input: {example_input}, output: {quality}" for example_input, quality in load_examples(representation)]
    return system_prompt(True), example_strings


def generate_prompt_gpt(representation, examples=True):
    """System prompt and example user/assistant turns; with examples=False only the system prompt (and no turns)."""
    if not examples:
        return system_prompt(False), [], []
    loaded = load_examples(representation)
    user_prompts = [example_input for example_input, _ in loaded]
    assistant_prompts = [quality for _, quality in loaded]
    return system_prompt(True), user_prompts, assistant_prompts
