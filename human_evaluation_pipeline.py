import os, sys
import json
import logging
import argparse
import re
import time
from functools import partial

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "src"))

from human_evaluation import EXAMPLES_DIR, format_input, generate_prompt_gemini, generate_prompt_gpt, read

from gen_ai_llm_call import (
    generate_gpt_with_timeout,
    generate_gemini_with_timeout,
    generate_anthropic_with_timeout,
)

REPRESENTATIONS = sorted(os.listdir(EXAMPLES_DIR))  # bpmn, mermaid_js, simple_json
DESCRIPTIONS_DIR = os.path.join(BASE, "process_descriptions")
GENERATION_DIR = os.path.join(BASE, "generation","human")

# gpt and anthropic take the same (system, user, assistant, prompt, temp, response_format) call shape,
# so they share one prompt-generation path; only gemini's shape differs.
GPT_STYLE_CALLS = {
    'gpt': generate_gpt_with_timeout,
    'anthropic': generate_anthropic_with_timeout,
}
SUPPORTED_LLMS = {'gemini', *GPT_STYLE_CALLS}


class Prompt:
    """Wraps an LLM's few-shot evaluation prompt behind a uniform call(prompt, temperature, response_format) interface."""

    def __init__(self, llm, representation, examples):
        if llm == 'gemini':
            system_prompt, example_strings = generate_prompt_gemini(representation, examples)
            self.call = partial(generate_gemini_with_timeout, system_prompt, example_strings)
        elif llm in GPT_STYLE_CALLS:
            system_prompt, user_prompts, assistant_prompts = generate_prompt_gpt(representation, examples)
            self.call = partial(GPT_STYLE_CALLS[llm], system_prompt, user_prompts, assistant_prompts)
        else:
            raise ValueError(f"Unsupported llm: {llm}")


def _write_json_atomic(path, data):
    tmp_path = path + '.tmp'
    with open(tmp_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    os.replace(tmp_path, path)


def parse_evaluation(response):
    """Parses the JSON evaluation of the llm ({"score": ..., "comments": {...}}), also if it is wrapped in ```json fences.
    Returns None if the response is not valid JSON."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def human_evaluation_pipeline(llm, representation, examples, temperature, iterations):
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger("{}Logger".format(llm.upper()))
    logger.setLevel(logging.INFO)

    prompt = Prompt(llm, representation, examples)
    models_path = os.path.join(BASE, representation)
    use_cases = sorted(d for d in os.listdir(models_path) if os.path.isdir(os.path.join(models_path, d)))

    os.makedirs(GENERATION_DIR, exist_ok=True)
    # runs without examples get their own file, so they don't overwrite the few-shot results
    suffix = '' if examples else '_no_examples'
    results_path = os.path.join(GENERATION_DIR, '{}_{}{}.json'.format(representation, llm, suffix))
    results = {}
    _write_json_atomic(results_path, results)

    logger.info('Starting the evaluation of models')

    for i, use_case in enumerate(use_cases):
        print('--------------------------{}/{} {}-----------------------------------'.format(i + 1, len(use_cases), use_case))
        try:
            description = read(os.path.join(DESCRIPTIONS_DIR, use_case + '.txt'))
            use_case_path = os.path.join(models_path, use_case)
            model_files = {f.split('.')[0]: f for f in os.listdir(use_case_path) if not f.endswith('.txt')}

            results[use_case] = {}
            for model in sorted(model_files, key=int):  # 0, 1, 2, ..., 10
                model_content = read(os.path.join(use_case_path, model_files[model]))
                quality_path = os.path.join(use_case_path, model + '.quality.txt')
                human_score = float(read(quality_path)) if os.path.exists(quality_path) else None

                results[use_case][model] = {'human_score': human_score, 'iterations': {}}
                for j in range(iterations):
                    logger.info(f'Iteration {j + 1}/{iterations}: evaluating model {model} of {use_case}')
                    start_time = time.perf_counter()
                    response = prompt.call(format_input(description, model_content), temperature, response_format=True)
                    running = time.perf_counter() - start_time
                    logger.info(f'TIME {running} for model {model} of {use_case}')

                    evaluation = parse_evaluation(response) if response else None
                    if response and evaluation is None:
                        logger.error(f'Could not parse the evaluation in iteration {j + 1} of model {model} of {use_case}')

                    result = {'evaluation': evaluation, 'time': running}
                    if evaluation is None:  # keep the raw llm answer only when it is not valid JSON (or missing)
                        result['response'] = response
                    results[use_case][model]['iterations'][j] = result

        except Exception as e:
            logger.error(f"An error occurred while processing use case {use_case}: {e}")

        _write_json_atomic(results_path, results)  # save after each use case

    logger.info('Completed evaluation of all models')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the quality of process models via an llm, with retries and timeout.")
    parser.add_argument('-l', '--llm', type=str, required=True, help='Select llm mode: {}'.format(', '.join(sorted(SUPPORTED_LLMS))))
    parser.add_argument('-r', '--representation', type=str, required=True,
                        help='Model representation = directory with the models, e.g. {}'.format(', '.join(REPRESENTATIONS)))
    parser.add_argument('-e', '--examples', type=str, required=False, default='true', choices=['true', 'false'],
                        help='true: few-shot with the examples of src/examples/<representation>, false: system prompt only (default true)')
    parser.add_argument('--temperature', type=float, required=False, default=0, help='Sampling temperature (default 0)')
    parser.add_argument('-i', '--iterations', type=int, required=False, default=5,
                        help='Number of evaluations per model (default 5)')

    args = parser.parse_args()
    llm = args.llm.lower()
    representation = args.representation.lower()

    examples = args.examples == 'true'
    models_dir = os.path.join(BASE, representation)
    examples_dir = os.path.join(EXAMPLES_DIR, representation)

    if llm not in SUPPORTED_LLMS:
        print('Please check selected llm model (only {} are acceptable)!!!'.format(', '.join(sorted(SUPPORTED_LLMS))))
    elif not os.path.isdir(models_dir):
        print('The model directory {} does not exist!!!'.format(models_dir))
    elif examples and not os.path.isdir(examples_dir):
        print('There are no examples for {} in {} (examples exist for: {}), use -e false or add them!!!'.format(
            representation, examples_dir, ', '.join(REPRESENTATIONS)))
    else:
        human_evaluation_pipeline(llm, representation, examples, args.temperature, args.iterations)
