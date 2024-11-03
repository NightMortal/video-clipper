# Video Clipper

Batch processing of videos into clips.

## Table of Contents

- [Video Clipper](#video-clipper)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Running](#running)
  - [Input File Structure](#input-file-structure)
    - [Example JSON Input](#example-json-input)
  - [Examples](#examples)
    - [Example Command for JSON Input](#example-command-for-json-input)
    - [Example Command for Manual Input](#example-command-for-manual-input)

## Installation

```bash
git clone https://github.com/NightMortal/video-clipper
cd video-clipper
python -m venv venv
source venv/Scripts/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

`venv` steps aren't necessary but are recommended.

## Running

```bash
python main.py [-f|--file] "path/to/input.json"
python main.py [-m|--manual] "video_path,MM:SS,MM:SS - output_name; video_path,MM:SS,MM:SS - output_name"
```

## Input File Structure

Expecting a JSON object with the following structure:

- `input_directory`: Absolute path indicating where to look for files.
- `output_directory`: Absolute path indicating where to output files.
- `clips`: Array of objects consisting of the following:
  - `video`: Absolute or relative path to source video file. If relative, appended onto `input_directory`.
  - `start_time`: String in the format `"MM:SS"` indicating the start time.
  - `end_time`: String in the format `"MM:SS"` indicating the end time.
  - (Optional) `output`: Name of output file. Will output in `output_directory`.
    - Default: Outputs generated name to `output_directory`.
    - If relative, outputted to `output_directory`.
    - If no file extension, defaults to the extension of the input file.
  - (Optional) `codec`: Depends on container type of output. Not necessary for `.mp4`.
    - See [moviepy documentation](https://zulko.github.io/moviepy/) for defaults.
    - All codecs supported by `ffmpeg` are supported.
  - (Optional) `resolution`: String in the format `"widthxheight"`.
    - Default: Width and height of source video.

### Example JSON Input

```json
{
    "input_directory": "D:\\Videos",
    "output_directory": "D:\\Videos\\Clips",
    "clips": [
        {
            "video": "example1.mp4",
            "start_time": "00:44",
            "end_time": "00:54",
            "output": "clip1.avi",
            "codec": "rawvideo",
            "resolution": "1920x1080"
        },
        {
            "video": "example2.mp4",
            "start_time": "09:42",
            "end_time": "09:49",
            "output": "clip2.mp4"
        },
        {
            "video": "example3.mp4",
            "start_time": "06:06",
            "end_time": "06:36",
            "resolution": "1280x720"
        }
    ]
}
```

## Examples

### Example Command for JSON Input

```bash
python main.py -f clips.json
```

### Example Command for Manual Input

```bash
python main.py -m "video.mp4,00:00,00:10 - clip1; video2.mp4,00:05,00:15 - clip2" -i "C:\\Videos" -o "C:\\Clips" -c "libx264" -r "1920x1080"
```
