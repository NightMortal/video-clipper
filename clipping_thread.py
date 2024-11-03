from dataclasses import dataclass
from os import path
import threading

from moviepy.editor import VideoFileClip


@dataclass
class VideoClipData:
    # required
    file_path: str
    start_time: tuple[int, int]
    end_time: tuple[int, int]
    # optional
    resolution: tuple[int, int] = None  # actually a list, bite me.
    output: str = ""
    codec: str = "libx264"  # Default codec


    def get_output_name(self):
        file_path, extension = path.splitext(self.file_path)
        name = self.output
        if len(name) != 0:
            return f"{name}{extension}"

        start_timestamp = ','.join(map(str, self.start_time))
        end_timestamp = ','.join(map(str, self.end_time))
        return f"{file_path} Clip {start_timestamp}-{end_timestamp}{extension}"


class ClippingThread(threading.Thread):
    '''
    Thread to clip videos using moviepy.
    '''
    def __init__(self, clip_data: VideoClipData):
        super().__init__(daemon=False)
        self.clip_data = clip_data

    def run(self):
        clip_data = self.clip_data
        output_name = clip_data.get_output_name()
        resolution = clip_data.resolution
        codec = clip_data.codec

        with VideoFileClip(clip_data.file_path, target_resolution=resolution) as video:
            video = video.subclip(clip_data.start_time, clip_data.end_time)
            video.write_videofile(output_name, codec=codec)