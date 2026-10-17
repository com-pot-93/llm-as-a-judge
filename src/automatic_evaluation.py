### evaluation types:  m2m - similarity of two process models (model_A, model_B)
###                    m2t - relevance and truthfulness of a generated model w.r.t. a process description
### modes:             simple   - prompts/autoeval_<type>.txt
###                    detailed - prompts/autoeval_<type>_det.txt
import os
import re

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(SRC_DIR, "prompts")

EVALUATION_TYPES = ["m2m", "m2t"]
MODES = ["simple", "detailed"]
# placeholders in the prompt files that are filled with the inputs of the evaluation
PLACEHOLDERS = {
    "m2m": ["model_A", "model_B"],
    "m2t": ["process_description", "generated_model"],
}


def read(path):
    with open(path, "r") as file:
        return file.read().strip()


def load_prompt(evaluation_type, mode):
    """Returns (system prompt, user prompt template) of prompts/autoeval_<type>[_det].txt."""
    if evaluation_type not in EVALUATION_TYPES:
        raise ValueError(f"unknown evaluation type {evaluation_type!r}, expected one of {EVALUATION_TYPES}")
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}, expected one of {MODES}")

    suffix = "_det" if mode == "detailed" else ""
    prompt = read(os.path.join(PROMPTS_DIR, f"autoeval_{evaluation_type}{suffix}.txt"))
    system_prompt, template = prompt.split("\n\n", 1)
    return system_prompt, template


def format_input(evaluation_type, mode, **inputs):
    """User prompt: the prompt template with its placeholders filled, e.g.
    format_input("m2m", "simple", model_A=..., model_B=...) or
    format_input("m2t", "detailed", process_description=..., generated_model=...)."""
    expected = PLACEHOLDERS[evaluation_type]
    if sorted(inputs) != sorted(expected):
        raise ValueError(f"{evaluation_type} expects the inputs {expected}, got {sorted(inputs)}")

    _, template = load_prompt(evaluation_type, mode)
    # one pass over the template, so braces inside the inputs (e.g. JSON models) or the JSON output example are kept as they are
    pattern = r"\{(" + "|".join(expected) + r")\}"
    return re.sub(pattern, lambda match: str(inputs[match.group(1)]), template)


def generate_prompt_gemini(evaluation_type, mode):
    """System prompt and examples (there are none for the automatic evaluation)."""
    system_prompt, _ = load_prompt(evaluation_type, mode)
    return system_prompt, []


def generate_prompt_gpt(evaluation_type, mode):
    """System prompt and example user/assistant turns (there are none for the automatic evaluation)."""
    system_prompt, _ = load_prompt(evaluation_type, mode)
    return system_prompt, [], []
