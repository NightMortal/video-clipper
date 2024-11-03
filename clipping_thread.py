from dataclasses import dataclass
from os import path
import threading
import logging
from moviepy.editor import VideoFileClip

logging.basicConfig(level=logging.INFO)

@dataclass
class VideoClipData:
    file_path: str
    start_time: tuple[int, int]
    end_time: tuple[int, int]
    resolution: tuple[int, int] = None
    output: str = ""
    codec: str = ""

    def get_output_name(self):
        file_path, extension = path.splitext(self.file_path)
        name = self.output
        if name:
            output_file_path, output_extension = path.splitext(name)
            if not output_extension:
                return f"{name}{extension}"
            return name

        start_timestamp = ','.join(map(str, self.start_time))
        end_timestamp = ','.join(map(str, self.end_time))
        return f"{file_path}_Clip_{start_timestamp}-{end_timestamp}{extension}"


class ClippingThread(threading.Thread):
    SUPPORTED_CODECS = {
        '.mp4': ['libx264', 'mpeg4'],
        '.ogv': ['libtheora'],
        '.webm': ['libvpx'],
        '.avi': ['rawvideo'],
        '.mov': ['libx264', 'mpeg4']  # Try 'libx264' first, then 'mpeg4' for .mov files
    }
    DEFAULT_CODEC = 'libx264'

    def __init__(self, clip_data: VideoClipData):
        super().__init__(daemon=False)
        self.clip_data = clip_data

    def run(self):
        clip_data = self.clip_data
        output_name = clip_data.get_output_name().replace('"', '')  # Remove double quotes from output name
        resolution = clip_data.resolution
        codec = clip_data.codec

        file_extension = path.splitext(output_name)[1].lower()

        if file_extension not in self.SUPPORTED_CODECS:
            logging.warning(f"File extension '{file_extension}' is not supported. Using default codec '{self.DEFAULT_CODEC}'.")
            codec = self.DEFAULT_CODEC
        elif not codec or codec not in self.SUPPORTED_CODECS[file_extension]:
            logging.warning(f"Codec '{codec}' is not supported for '{file_extension}'. Falling back to a valid codec.")
            codec = self.SUPPORTED_CODECS[file_extension][0]

        if resolution:
            resolution = (resolution[1], resolution[0])

        try:
            with VideoFileClip(clip_data.file_path, target_resolution=resolution) as video:
                video.subclip(clip_data.start_time, clip_data.end_time).write_videofile(output_name, codec=codec)
        except OSError as e:
            if "Invalid argument" in str(e):
                logging.error(f"Invalid argument error: {e}")
            else:
                logging.error(f"OS error: {e}")
        except Exception as e:
            logging.exception("An unexpected error occurred.")
            raise e