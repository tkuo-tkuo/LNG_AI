"""Python script for creating jsonl database"""
import os
import random

import argparse
from datetime import datetime
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
        fine_tune(jsonl_dataset_path=args.jsonl_dataset_path)
    elif args.mode == constants.OpenaiBabbageModelInteractionMode.VIEW_FINE_TUNE_MODELS.value:
        view_fine_tune_models()
    elif args.mode == constants.OpenaiBabbageModelInteractionMode.TEST_FINE_TUNE_MODEL.value:
        test_fine_tune_model(model_name=args.model_name,
                             num_of_sentences_generated=args.num_of_sentences_generated)
    elif args.mode == constants.OpenaiBabbageModelInteractionMode.VIEW_TRAINING_PROCESS.value:
        view_training_process(model_id=args.model_id)
    else:
        raise ValueError("Invalid mode")
    return 0


def test_fine_tune_model(model_name: str, num_of_sentences_generated: int):
    """Test fine-tune model"""
    assert model_name is not None, "model_name cannot be None"
    assert num_of_sentences_generated > 0, "num_of_sentences_generated must be > 0"

    print(f"Testing fine-tune model: {model_name}")
    print(f"Number of sentences generated: {num_of_sentences_generated}")

    # Estimate cost
    estimated_cost = estimate_cost_estimation(
        num_of_sentences_generated=num_of_sentences_generated, mode="usage")
    print(f"Estimated cost: ${estimated_cost}")
    if not request_continue_permission():
        exit()

    os.makedirs(
        constants.RootDirectory.GENERATED_FILE_ROOT.value,
        exist_ok=True)

    # API reference:
    # https://platform.openai.com/docs/api-reference/completions/create
    sentences = constants.PROMPT_SENTENCES.copy()
    chat_history = constants.PROMPT_SENTENCES.copy()
    for _ in range(num_of_sentences_generated):
        assert len(sentences) == len(
            constants.PROMPT_SENTENCES), f"length of prompt sentences must be {len(constants.PROMPT_SENTENCES)}"

        prompt = constants.SEPARRATOR.join(sentences)
        print(f"Prompt: {prompt}")
        encoded_prompt = prompt.encode("unicode_escape").decode("utf-8")
        print(f"Encoded prompt: {encoded_prompt}")

        num_tokens = random.randint(int(constants.AVG_NUM_OF_TOKENS_PER_GENERATED_SENTENCE * 0.8),
                                    int(constants.AVG_NUM_OF_TOKENS_PER_GENERATED_SENTENCE * 1.2))
        response = openai.Completion.create(
            model=model_name,
            prompt=prompt,
            max_tokens=num_tokens,
            presence_penalty=0.2,
            frequency_penalty=0.2)

        new_sentence = response["choices"][0]["text"]
        sentences.pop(0)
        sentences.append(new_sentence)
        chat_history.append(new_sentence)

    print("Chat history: ", chat_history)
    generated_chat_history_file_path = os.path.join(
        constants.RootDirectory.GENERATED_FILE_ROOT.value,
        f"generated_chat_history_{model_name}_{num_of_sentences_generated}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
    with open(generated_chat_history_file_path, "w") as chat_history_file:
        for sentence in chat_history:
            chat_history_file.write(sentence + "\n")


def view_training_process(model_id: str):
    """View training process for a given model_id"""
    assert model_id is not None, "model_id cannot be None"

    print(f"Viewing training process for model_id: {model_id}")
    fine_tune_job_retrieve_response = openai.FineTune.retrieve(model_id)

    overall_status = fine_tune_job_retrieve_response["status"]
    print("==> Overall status: ", overall_status)
    for event in fine_tune_job_retrieve_response["events"]:
        eight_hours_in_seconds = 8 * 60 * 60
        print("==>", datetime.utcfromtimestamp(
            event["created_at"] + eight_hours_in_seconds), "Event message: ", event["message"])


def fine_tune(jsonl_dataset_path: str):
    """
    Note: currently it is NOT supported to fine-tune from a previous fine-tune model
    """
    estimated_cost = estimate_cost_estimation(
        jsonl_dataset_path=jsonl_dataset_path, mode="train")
    print(f"Estimated cost: ${estimated_cost}")

    if not request_continue_permission():
        exit()

    with open(jsonl_dataset_path) as jsonl_file:
        file_create_response = openai.File.create(
            file=jsonl_file, purpose='fine-tune')
    file_id = file_create_response["id"]

    print("Start fine-tuning...")
    response = openai.FineTune.create(training_file=file_id, model='babbage')
    print(response)


def view_fine_tune_models():
    """View all fine-tune models"""
    fine_tune_models_list = openai.FineTune.list()
    for fine_tune_model in fine_tune_models_list["data"]:
        model_name = fine_tune_model["fine_tuned_model"]
        model_id = fine_tune_model["id"]
        model_training_file_size_history = [
            training_file["bytes"] for training_file in fine_tune_model["training_files"]]
        print(model_name)
        print(f"==> ID: {model_id}")
        print(
            f"==> Training file size history (bytes) {model_training_file_size_history}")


def request_continue_permission():
    """Request permission to continue"""
    answer = input("Continue? please type 'yes/y' or 'no/n'")
    if answer.lower() in ["y", "yes"]:
        return True
    elif answer.lower() in ["n", "no"]:
        print("ok, bye")
        return False  # exit
    else:
        print("Invalid input, please type 'yes/y' or 'no/n'")
        request_continue_permission()


def estimate_cost_estimation(num_of_sentences_generated: int = 0,
                             jsonl_dataset_path: str = "", mode: str = "") -> float:
    """Estimate cost estimation for a given jsonl dataset"""

    if mode == "train":
        jsonls = utils.JsonlUtils.get_jsonls(jsonl_dataset_path)
        estimated_word_count = sum(
            [len(jsonl["prompt"]) + len(jsonl["completion"]) for jsonl in jsonls])
        estimated_token_count = estimated_word_count * 2
        print(f"Estimated token count: {estimated_token_count}")
        estimated_1k_token_count = estimated_token_count / 1000
        estimated_cost = estimated_1k_token_count * \
            constants.OpenaiBabbageCost.TRAINING_PER_1K_TOKENS.value
        estimated_cost *= 4  # 4 epochs for fine-tuning as default
        return round(estimated_cost, 4)
    elif mode == "usage":
        estimated_token_count = num_of_sentences_generated * \
            constants.AVG_NUM_OF_TOKENS_PER_GENERATED_SENTENCE
        estimated_1k_token_count = estimated_token_count / 1000
        estimated_cost = estimated_1k_token_count * \
            constants.OpenaiBabbageCost.USAGE_PER_1K_TOKENS.value
        return estimated_cost
    else:
        raise ValueError("Invalid mode")


if __name__ == "__main__":
    main()
