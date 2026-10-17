#!/bin/bash

poetry run python human_evaluation_pipeline.py -r mermaid_js -l gpt -e false
poetry run python human_evaluation_pipeline.py -r mermaid_js -l gemini -e false
poetry run python human_evaluation_pipeline.py -r mermaid_js -l anthropic -e false

poetry run python human_evaluation_pipeline.py -r mermaid_js -l gpt -e true
poetry run python human_evaluation_pipeline.py -r mermaid_js -l gemini -e true
poetry run python human_evaluation_pipeline.py -r mermaid_js -l anthropic -e true

poetry run python human_evaluation_pipeline.py -r bpmn -l gpt -e false
poetry run python human_evaluation_pipeline.py -r bpmn -l gemini -e false
poetry run python human_evaluation_pipeline.py -r bpmn -l anthropic -e false

poetry run python human_evaluation_pipeline.py -r bpmn -l gpt -e true
poetry run python human_evaluation_pipeline.py -r bpmn -l gemini -e true
poetry run python human_evaluation_pipeline.py -r bpmn -l anthropic -e true

poetry run python human_evaluation_pipeline.py -r simple_json -l gpt -e false
poetry run python human_evaluation_pipeline.py -r simple_json -l gemini -e false
poetry run python human_evaluation_pipeline.py -r simple_json -l anthropic -e false

poetry run python human_evaluation_pipeline.py -r simple_json -l gpt -e true
poetry run python human_evaluation_pipeline.py -r simple_json -l gemini -e true
poetry run python human_evaluation_pipeline.py -r simple_json -l anthropic -e true
