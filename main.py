import argparse
import json
from typing import Any

from clipping_thread import ClippingThread, VideoClipData


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
        help="Manual input for clips in the format: 'video_path,MM:SS,MM:SS - output_name' separated by ';'",
        required=False
    )
    return vars(parser.parse_args())


def parse_clip_data(file_path: str) -> list[VideoClipData]:
    input_json = None
    with open(file_path, mode="r") as input_file:
        input_json = json.load(input_file)

    all_clip_data: list[VideoClipData] = []
    for item in input_json:
        clip_data = VideoClipData(
            file_path=item['video'],
            start_time=tuple(item['start_time']),
            end_time=tuple(item['end_time']),
            resolution=None,  # Assuming resolution is optional and not provided in JSON
            output=item['output'],
            codec=item.get('codec', 'libx264')  # Default codec if not provided
        )
        all_clip_data.append(clip_data)
    return all_clip_data


def parse_time(time_str: str) -> tuple[int, int]:
    time_str = time_str.replace(',', '')  # Remove any trailing commas
    minutes, seconds = map(int, time_str.split(':'))
    return (minutes, seconds)

def parse_manual_input(manual_arg: str) -> list[VideoClipData]:
    clip_data_list = []
    clips = manual_arg.split(';')
    for clip in clips:
        parts = clip.strip().split(' - ')
        if len(parts) < 2:
            print(f"Error: Invalid format for clip: {clip}")
            continue
        video_info = parts[0].strip().split(' ')
        if len(video_info) < 3:
            print(f"Error: Invalid format for video info: {parts[0]}")
            continue
        video_path = video_info[0].strip().strip('"')
        start_time_str = video_info[1].strip()
        end_time_str = video_info[2].strip()
        output_name = parts[1].strip()
        codec = 'libx264'  # Default codec

        start_time = parse_time(start_time_str)
        end_time = parse_time(end_time_str)
        clip_data = VideoClipData(
            file_path=video_path,
            start_time=start_time,
            end_time=end_time,
            resolution=None,  # Assuming resolution is optional and not provided in manual input
            output=output_name,
            codec=codec
        )
        clip_data_list.append(clip_data)
    return clip_data_list


def main():
    args = parse_args()
    clip_data_list = []

    if args['file']:
        clip_data_list = parse_clip_data(args['file'])
    elif args['manual']:
        clip_data_list = parse_manual_input(args['manual'])
    else:
        print("Either --file or --manual option must be provided.")
        return

    threads = [ClippingThread(clip_data) for clip_data in clip_data_list]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()