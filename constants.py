import enum

ONE_MINUTE_IN_MILLISECONDS = 1 * 60 * 1000
AUDIO_FILE_ROOT = "audio_files"
RAW_3GG_FILE_ROOT = "raw_3gg_files"


class AudioFileKeyword(enum.Enum):
    """Enum for audio files keyword (substr)"""
    PREVIEW = "one_minute_preview"
    HOUR_CHUCK = "_hour_chuck"
    FIVE_MINUTES_CHUCK = "_5_mins_chuck"


class TranscribeMode(enum.Enum):
    """Enum for available AI transcribing"""
    WHISPER = "whisper"
