"""Python script for creating jsonl database"""
import os
import argparse
from dotenv import load_dotenv
import openai

from LNG_AI import utils
from LNG_AI import constants

# Currently, fine-tune only supports on completion but not chat
# reference: https://platform.openai.com/docs/guides/fine-tuning


def main():
    """
    Available modes:
    1. fine-tuning from scratch (fine-tune-scratch)
    2. fine-tuning from previous fine-tune model (fine-tune-continue)
    3. view current available fine-tune models (view-fine-tune-models)
    4. test fine-tune models (test-fine-tune-models)
    5. view training process (view-training-process)
    """

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        type=int,
        help="mode (e.g., 0: fine-tune, 1: view-fine-tune-models, 2: test-fine-tune-model, 3: view-training-process)",
        default=-
        1)
    parser.add_argument(
        "--jsonl_dataset_path",
        type=str,
        help="jsonl dataset path (e.g., jsonl_dataset/jsonl_dataset_0_percent_297.jsonl)",
        default=None)
    parser.add_argument(
        "--model_id",
        type=str,
        help="model id (e.g., ft-KmDSzIzE92iea4FWRgc9Ya5o)",
        default=None)
    parser.add_argument(
        "--model_name",
        type=str,
        help="model name (e.g., babbage:ft-personal-2023-03-31-16-53-00)",
        default=None)
    parser.add_argument(
        "--num_of_sentences_generated",
        type=int,
        help="number of sentences generated",
        default=-1)
    args = parser.parse_args()

    # Check if mode is valid
    assert args.mode in [
        enum.value for enum in constants.OpenaiBabbageModelInteractionMode], "Invalid mode"

    # Load environment variables
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if args.mode == constants.OpenaiBabbageModelInteractionMode.FINE_TUNE.value:
        utils.OpenaiUtils.fine_tune(jsonl_dataset_path=args.jsonl_dataset_path)
    elif args.mode == constants.OpenaiBabbageModelInteractionMode.VIEW_FINE_TUNE_MODELS.value:
        utils.OpenaiUtils.view_fine_tune_models()
    elif args.mode == constants.OpenaiBabbageModelInteractionMode.TEST_FINE_TUNE_MODEL.value:
        utils.OpenaiUtils.test_fine_tune_model(model_name=args.model_name,
                                               num_of_sentences_generated=args.num_of_sentences_generated)
    elif args.mode == constants.OpenaiBabbageModelInteractionMode.VIEW_TRAINING_PROCESS.value:
        utils.OpenaiUtils.view_training_process(model_id=args.model_id)
    else:
        raise ValueError("Invalid mode")
    return 0


if __name__ == "__main__":
    main()
