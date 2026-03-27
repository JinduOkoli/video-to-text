# video-to-text

A command-line tool to download YouTube videos as audio (`.mp3`) and transcribe them into text using [faster-whisper](https://github.com/guillaumekln/faster-whisper)  .

---

## ✨ Features

- 🎥 Download videos from YouTube channels or playlists  
- 🎧 Convert audio to `.mp3`  
- 📝 Transcribe audio into text automatically using YouTube’s built-in captions first and falling back to high-speed [faster-whisper](https://github.com/guillaumekln/faster-whisper)  
- 📂 Save results in a structured folder
- 🛠 Easy-to-use CLI interface with [Click](https://click.palletsprojects.com/)  

---

## 📦 Installation

Clone the repo and install:

```
git clone https://github.com/your-username/video-to-text.git
cd video-to-text
pip install .
```

## 🔑 Usage
Run the CLI with:
```
video-to-text --video-id "VIDEO_ID"
```

### Options

| Option         | Short | Default                                                       | Description                     |
|----------------|-------|---------------------------------------------------------------|---------------------------------|
| `--video-id`   | `-v`  | **Required**                                                  | ID of the video to be retrieved |
| `--output-dir` | `-o`  | `User system data directory (user_data_dir("video_to_text"))` | Directory to save transcripts   |


```
video-to-text --channel-name "CHANNEL_NAME"
```

### Options

| Option           | Short | Default                                                       | Description                                                  |
|------------------|-------|---------------------------------------------------------------|--------------------------------------------------------------|
| `--channel-name` | `-c`  | **Required**                                                  | YouTube channel name to fetch videos from                    |
| `--output-dir`   | `-o`  | `User system data directory (user_data_dir("video_to_text"))` | Directory to save transcripts                                |
| `--max-videos`   | `-m`  | `10`                                                          | Max number of videos to download                             |
| `--min-duration` | '-n'  | 'None'                                                        | Minimum duration of video to be retrieved from channel       |
| `--max-duration` | '-x'  | 'None'                                                        | Minimum duration of video to be retrieved from channel       |
| `--start-date`   | '-s'  | 'None'                                                        | Include videos published on or after this date (YYYY-MM-DD)  |
| `--end-date`     | '-e'  | 'None'                                                        | Include videos published on or before this date (YYYY-MM-DD) |


#### Get video based on video_id
```
video-to-text --video-id "LqFc0z-pQTg"
```
#### Get 10 latest videos
```
video-to-text -c "NASA"
```
#### Get all videos
```
video-to-text -c "NASA" --max-videos all
```
#### Specify output directory
```
video-to-text -c "NASA" -o ./output
```
## 🛠 Development
Install in editable mode:
```
pip install -e .
```
Run with Python directly:

```
python src/video_to_text/entrypoint.py --channel-name "NASA"
```

## 📜 License
This project is licensed under the MIT License.
