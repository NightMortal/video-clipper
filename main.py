import argparse
import logging
import json
from typing import Any, List
from os import path

from clipping_thread import VideoClipData, ClippingThread

logging.basicConfig(level=logging.INFO)

def parse_args() -> dict[str, Any]:
    parser = argparse.ArgumentParser(
        prog="Video Clipper",
        description="Custom video clipper"
    )
    parser.add_argument(
        "-f", "--file",
        help="JSON file containing clips to produce",
        required=False
    )
    parser.add_argument(
        "-m", "--manual",
        help="Manual input for clips in the format: video_path,MM:SS,MM:SS - output_name separated by ';'.",
        required=False
    )
    parser.add_argument(
        "-i", "--input_directory",
        help="Input directory for manual clips",
        required=False
    )
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory for manual clips",
        required=False
    )
    parser.add_argument(
        "-c", "--codec",
        help="Codec for manual clips",
        required=False
    )
    parser.add_argument(
        "-r", "--resolution",
        help="Resolution for manual clips in the format 'widthxheight'",
        required=False
    )
    parser.add_argument(
        "-e", "--examples",
        action="store_true",
        help="Show examples of how to use the command"
    )
    args = vars(parser.parse_args())
    return args

def show_examples():
    examples = """
    Examples:
    1. Using a JSON file:
       python main.py -f clips.json

    2. Manual input:
       python main.py -m "video.mp4,00:00,00:10 - clip1.mp4;video2.mp4,00:05,00:15 - clip2.mp4" \\
                       -i "C:\\Videos" \\
                       -o "C:\\Clips" \\
                       -c "libx264" \\
                       -r "1920x1080"
    """
    print(examples)

def parse_clip_data(file_path: str) -> List[VideoClipData]:
    with open(file_path, mode="r") as input_file:
        input_json = json.load(input_file)

    input_directory = input_json.get('input_directory', '')
    output_directory = input_json.get('output_directory', '')

    all_clip_data: List[VideoClipData] = []
    for item in input_json['clips']:
        file_path = path.join(input_directory, item['video'])
        start_time = parse_time(item['start_time'])
        end_time = parse_time(item['end_time'])
        output = path.join(output_directory, item['output'])
        codec = item.get('codec', '')
        resolution = tuple(map(int, item['resolution'].split('x'))) if 'resolution' in item else None

        clip_data = VideoClipData(
            file_path=file_path,
            start_time=start_time,
            end_time=end_time,
            resolution=resolution,
            output=output,
            codec=codec
        )
        all_clip_data.append(clip_data)
    return all_clip_data

def parse_time(time_str: str) -> tuple[int, int]:
    try:
        time_str = time_str.replace(',', '')
        minutes, seconds = map(int, time_str.split(':'))
        if minutes < 0 or seconds < 0 or seconds >= 60:
            raise ValueError("Invalid time format")
        return (minutes, seconds)
    except ValueError as e:
        logging.error(f"Error parsing time '{time_str}': {e}")
        raise

def parse_manual_input(manual_arg: str, input_directory: str = '', output_directory: str = '', codec: str = '', resolution: str = '') -> List[VideoClipData]:
    clip_data_list = []
    clips = manual_arg.split(';')
    for clip in clips:
        try:
            logging.info(f"Parsing clip: {clip}")
            video_path, times_output = clip.split(' - ')
            video_path, start_time_str, end_time_str = video_path.split(',')
            start_time = parse_time(start_time_str)
            end_time = parse_time(end_time_str)
            output = path.join(output_directory or '', times_output.strip())
            resolution_tuple = tuple(map(int, resolution.split('x'))) if resolution else None

            clip_data = VideoClipData(
                file_path=path.join(input_directory or '', video_path),
                start_time=start_time,
                end_time=end_time,
                resolution=resolution_tuple,
                output=output,
                codec=codec
            )
            clip_data_list.append(clip_data)
        except ValueError as e:
            logging.error(f"Error parsing clip: {clip}. Error: {e}")
    return clip_data_list

def main():
    args = parse_args()

    if args['examples']:
        show_examples()
        return

    clip_data_list = []

    if args['file']:
        clip_data_list = parse_clip_data(args['file'])
    elif args['manual']:
        clip_data_list = parse_manual_input(
            args['manual'],
            args.get('input_directory', ''),
            args.get('output_directory', ''),
            args.get('codec', ''),
            args.get('resolution', '')
        )
    else:
        logging.error("Either --file or --manual option must be provided.")
        return

    threads = [ClippingThread(clip_data) for clip_data in clip_data_list]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()