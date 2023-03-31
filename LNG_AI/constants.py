import enum

ONE_MINUTE_IN_MILLISECONDS = 1 * 60 * 1000


class OpenaiBabbageModelInteractionMode(enum.Enum):
    """Enum for OpenAI Babbage model interaction mode"""
    FINE_TUNE_SCRATCH = 0
    FINE_TUNE_CONTINUE = 1
    VIEW_FINE_TUNE_MODELS = 2
    TEST_FINE_TUNE_MODELS = 3
    VIEW_TRAINING_PROCESS = 4


class OpenaiBabbageCost(enum.Enum):
    """Enum for OpenAI Babbage cost"""
    TRAINING_PER_1K_TOKENS = 0.0006
    USAGE_PER_1K_TOKENS = 0.0024


class RootDirectory(enum.Enum):
    """Enum for root directories"""
    AUDIO_FILE_ROOT = "audio_files"
    RAW_3GG_FILE_ROOT = "raw_3gg_files"
    JSONL_DATASET_ROOT = "jsonl_dataset"


class AudioFileKeyword(enum.Enum):
    """Enum for audio files keyword (substr)"""
    FULL = "full"
    PREVIEW = "one_minute_preview"
    HOUR_CHUCK = "_hour_chuck"
    FIVE_MINUTES_CHUCK = "_5_mins_chuck"


class TranscribeMode(enum.Enum):
    """Enum for available AI transcribing"""
    WHISPER = "whisper"
