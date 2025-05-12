# Main entry point for script
import json
import argparse
from modules.DataChecker import DataChecker
from modules.ExtractionTask import ExtractionTask
from modules.ExtractionTask import EmbedModel



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--number_of_runs', type=int, default=5, help='Number of runs to execute')
    args = parser.parse_args()
    number_of_runs = args.number_of_runs

    data_checker = DataChecker()

    result_set = {}
    embeb_models = [
        EmbedModel(name="BAAI/bge-base-en-v1.5", source="huggingface"),
        EmbedModel(name="bge-m3", source="local"),
        EmbedModel(name="nomic-embed-text", source="local"),
    ]

    models = ["mistral", "gemma2", "gemma3", "llama3.2", "llama3.3", "qwen2.5", "phi4", "qwen3:0.6b", "qwen3:1.7b", "qwen3:4b", "qwen3:8b", "qwen3:14b", "qwen3:32b"]

    for run in range(number_of_runs):
        for embed_model in embeb_models:
            for model in models:

                print("\n" + 80*"*")
                print(f"Run: {run:d}, Model: {model:s}, Embed: {embed_model.name:s}")
                print("\n")

                # Create and run extraction task with current models
                extraction_task = ExtractionTask(model, embed_model)
                try:
                    result = extraction_task.run_extraction()
                    score = data_checker.score_resume_data(result)
                except Exception as e:
                    print("\n" + 80 * "!")
                    print(f"Error during extraction: {str(e)}")
                    print("\n" + 80 * "!")
                    score = -10000

                score_set = {
                    "model": model,
                    "embed_model": embed_model,
                    "score": score
                }

                if embed_model.name not in result_set:
                    result_set[embed_model.name] = {}
                if model not in result_set[embed_model.name]:
                    result_set[embed_model.name][model] = []
                result_set[embed_model.name][model].append(score)

                SCORE_PREFIX = ">>> Score:"
                print(f"{SCORE_PREFIX} model={model:s}, embed_model={embed_model.name:s}, score={score:d}")
            
    print("Final Scores:")
    print("\n\n" + 80*"=")
    print(json.dumps(result_set, indent=2))
