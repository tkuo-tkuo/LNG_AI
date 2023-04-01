"""Python script for common utilities"""
import csv
import os
import math
import logging
import random
import json
from collections import Counter

from datetime import datetime
from mutagen.mp3 import MP3
import openai

from LNG_AI import constants


class InteractionUtils():
    """ Interaction utils """
    @staticmethod
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
            InteractionUtils.request_continue_permission()


class FileUtils():
    """Class for common file utilities"""
    @staticmethod
    def get_audio_file_directories() -> list:
        """Get file directories for each episode"""
        audio_file_root = constants.RootDirectory.AUDIO_FILE_ROOT.value
        audio_ids = os.listdir(audio_file_root)
        return [f"{audio_file_root}/{audio_id}" for audio_id in audio_ids]

    @staticmethod
    def get_one_hour_chuck_audio_paths(audio_file_dir: str) -> list:
        """Get five minutes chuck audios"""
        return FileUtils.get_five_minutes_chuck_paths(audio_file_dir,
                                                      chuck_keyword=constants.AudioFileKeyword.HOUR_CHUCK,
                                                      ext_type="audio")

    @staticmethod
    def get_five_minutes_chuck_audio_paths(audio_file_dir: str) -> list:
        """Get five minutes chuck audios"""
        return FileUtils.get_five_minutes_chuck_paths(audio_file_dir,
                                                      chuck_keyword=constants.AudioFileKeyword.FIVE_MINUTES_CHUCK,
                                                      ext_type="audio")

    @staticmethod
    def get_five_minutes_chuck_transcript_paths(audio_file_dir: str) -> list:
        """Get five minutes chuck transcripts"""
        return FileUtils.get_five_minutes_chuck_paths(audio_file_dir,
                                                      chuck_keyword=constants.AudioFileKeyword.FIVE_MINUTES_CHUCK,
                                                      ext_type="transcript")

    @staticmethod
    def get_five_minutes_chuck_paths(
            audio_file_dir: str, chuck_keyword: constants.AudioFileKeyword, ext_type: str) -> list:
        """Get five minutes chuck"""
        # only five-minutes and 1-hour chuck are supported
        if chuck_keyword not in [
                constants.AudioFileKeyword.FIVE_MINUTES_CHUCK, constants.AudioFileKeyword.HOUR_CHUCK]:
            raise ValueError(f"Invalid chuck_keyword: {chuck_keyword}")

        # Get the total length of the audio file
        total_length_in_milliseconds = AudioUtils.get_audio_length_in_milliseconds(
            f"{audio_file_dir}/{constants.AudioFileKeyword.FULL.value}.mp3")

        # Get the upper bound index
        chuck_in_milliseconds = 5 * constants.ONE_MINUTE_IN_MILLISECONDS if chuck_keyword == constants.AudioFileKeyword.FIVE_MINUTES_CHUCK else 60 * \
            constants.ONE_MINUTE_IN_MILLISECONDS
        upper_bound_index = math.ceil(
            total_length_in_milliseconds / chuck_in_milliseconds)

        # Return list
        paths = []
        for idx in range(1, upper_bound_index + 1):
            if ext_type == "audio":
                path = f"{audio_file_dir}/{idx}{chuck_keyword.value}.mp3"
            elif ext_type == "transcript":
                path = f"{audio_file_dir}/whisper/{idx}{chuck_keyword.value}.txt"
            else:
                raise ValueError(f"Invalid ext_type: {ext_type}")
            paths.append(path)
        return paths

    @staticmethod
    def store_as_html(video_infos, store_file_path):
        '''helper function to store latest video infos in md file'''
        with open(store_file_path, "w", encoding="utf-8") as html_file:
            html_file.write(
                '| Title | Audio Dir | Published at | ID | Source URL |\n')
            html_file.write('| ------ | ------ | --- | --- | ------ |\n')
            # TODO: add relative links for audio files
            # https://github.com/tkuo-tkuo/LNG_AI/issues/6
            for video_info in video_infos:
                html_file.write(
                    f'| {video_info["title"]} | {video_info["audio_file_dir"]} '
                    f'| {video_info["publishedAt"]} | {video_info["id"]} '
                    f'| {video_info["audio_source_url"]} |\n')

    @staticmethod
    def store_as_csv(video_infos, store_file_path):
        '''helper function to store latest video infos in csv file'''
        with open(store_file_path, "w", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Title", "Audio Dir",
                                "Published at", "ID", "Source URL"])

            rows = [[video_info["title"], video_info["audio_file_dir"], video_info["publishedAt"],
                    video_info["id"], video_info["audio_source_url"]] for video_info in video_infos]
            csv_writer.writerows(rows)


class AudioUtils():
    """Class for common audio utilities"""
    @staticmethod
    def get_audio_length_in_milliseconds(file_path: str) -> int:
        """
        Note: use mutagen.mp3 instead of AudioSegment, which has much lower loading time
        """
        audio = MP3(file_path)
        return audio.info.length * 1000


class TranscriptUtils():
    """Class for common transcript utilities"""
    @staticmethod
    def check_transcript_repetitive_word_occurance(
            transcript_path: str, threshold: float, log_error: bool) -> bool:
        """Check if there is any repetitive word in the transcript"""
        assert threshold >= 0 and threshold <= 1, "threshold should be between 0 and 1"

        with open(transcript_path, "r") as file:
            transcript = file.read()
            words = transcript.split(" ")
            words_occurance = Counter(words)

            # check if any word has more than 10% occurance
            # make this part of logic as a util function in utils.py
            total_word_cnt = len(words)
            for word in words_occurance:
                num_of_occurance = words_occurance[word]
                occurance_percentage = round(
                    100 * num_of_occurance / total_word_cnt, 2)
                if occurance_percentage > (threshold * 100):
                    if log_error:
                        error_str = f"{transcript_path} has repetitive word occurance: {word} ({occurance_percentage}%))"
                        logging.error(error_str)
                    return False

        return True


class JsonlUtils():
    """Class for common jsonl utilities"""
    @staticmethod
    def store_portion_jsonl(jsonls: list[dict], portion: float):
        """Store a portion of the jsonls"""
        assert portion > 0 and portion <= 1, "portion should be between 0 and 1"

        # Get the number of jsonls to store
        num_of_jsonls_to_store = math.ceil(len(jsonls) * portion)

        # Sort the jsonls randomly
        random.shuffle(jsonls)

        # Save the jsonls to export_jsonl_path
        os.makedirs(
            constants.RootDirectory.JSONL_DATASET_ROOT.value,
            exist_ok=True)
        export_json_file = f"jsonl_dataset_{int(portion * 100)}_percent_{num_of_jsonls_to_store}.jsonl"
        export_jsonl_path = os.path.join(
            constants.RootDirectory.JSONL_DATASET_ROOT.value, export_json_file)
        with open(export_jsonl_path, "w") as file:
            for idx in range(num_of_jsonls_to_store):
                jsonl = jsonls[idx]
                json.dump(jsonl, file)
                file.write('\n')

            # Log
            print(f"JSONL dataset successfully created with size (portion={portion}): "
                  f"{num_of_jsonls_to_store} records")

    @staticmethod
    def create_jsonl_database(repetitive_word_threshold: float, debug: bool):
        """Create jsonl database"""
        jsonl_dataset_list = []

        # Get list of jsonl
        audio_file_dirs = FileUtils.get_audio_file_directories()
        for audio_file_dir in audio_file_dirs:
            for five_minutes_transcript_path in FileUtils.get_five_minutes_chuck_transcript_paths(
                    audio_file_dir):
                # True means okay (not repetitive)
                if TranscriptUtils.check_transcript_repetitive_word_occurance(
                        five_minutes_transcript_path, repetitive_word_threshold, debug):
                    with open(five_minutes_transcript_path, "r") as file:
                        words = file.read().split(" ")
                        num_of_sentences_to_consider = 3
                        assert len(words) >= num_of_sentences_to_consider + \
                            1, "Not enough words to create jsonl"

                        for idx in range(0, len(words) -
                                         num_of_sentences_to_consider):
                            # Reference:
                            # https://platform.openai.com/docs/guides/fine-tuning
                            separator = constants.SEPARRATOR
                            jsonl = {"prompt": separator.join(words[idx:idx + num_of_sentences_to_consider]),
                                     "completion": words[idx + num_of_sentences_to_consider]}
                            jsonl_dataset_list.append(jsonl)

        # Store a portion of the jsonl_dataset_list
        portions = [0.005, 0.01, 0.1, 0.2, 0.3,
                    0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        for portion in portions:
            JsonlUtils.store_portion_jsonl(
                jsonl_dataset_list, portion)

    @staticmethod
    def get_jsonls(jsonl_path: str) -> list[dict]:
        """Read jsonl file"""
        jsonls = []
        with open(jsonl_path, "r") as file:
            for line in file:
                jsonls.append(json.loads(line))
        return jsonls


class OpenaiUtils():
    """Class for common openai utilities"""
    @staticmethod
    def test_fine_tune_model(model_name: str, num_of_sentences_generated: int):
        """Test fine-tune model"""
        assert model_name is not None, "model_name cannot be None"
        assert num_of_sentences_generated > 0, "num_of_sentences_generated must be > 0"

        print(f"Testing fine-tune model: {model_name}")
        print(f"Number of sentences generated: {num_of_sentences_generated}")

        # Estimate cost
        estimated_cost = OpenaiUtils.estimate_cost_estimation(
            num_of_sentences_generated=num_of_sentences_generated, mode="usage")
        print(f"Estimated cost: ${estimated_cost}")
        if not InteractionUtils.request_continue_permission():
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

    @staticmethod
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

    @staticmethod
    def fine_tune(jsonl_dataset_path: str):
        """
        Note: currently it is NOT supported to fine-tune from a previous fine-tune model
        """
        estimated_cost = OpenaiUtils.estimate_cost_estimation(
            jsonl_dataset_path=jsonl_dataset_path, mode="train")
        print(f"Estimated cost: ${estimated_cost}")

        if not InteractionUtils.request_continue_permission():
            exit()

        with open(jsonl_dataset_path) as jsonl_file:
            file_create_response = openai.File.create(
                file=jsonl_file, purpose='fine-tune')
        file_id = file_create_response["id"]

        print("Start fine-tuning...")
        response = openai.FineTune.create(
            training_file=file_id, model='babbage')
        print(response)

    @staticmethod
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

    @staticmethod
    def estimate_cost_estimation(num_of_sentences_generated: int = 0,
                                 jsonl_dataset_path: str = "", mode: str = "") -> float:
        """Estimate cost estimation for a given jsonl dataset"""

        if mode == "train":
            jsonls = JsonlUtils.get_jsonls(jsonl_dataset_path)
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
