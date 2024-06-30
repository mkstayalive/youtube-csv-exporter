`youtube_video_subs_downloader.py` and `youtube_playlists_meta.py` scripts.

# YouTube Video Subtitles Downloader and Playlist Metadata Fetcher

This repository contains two Python scripts for interacting with YouTube:

1. `youtube_video_subs_downloader.py`: Downloads subtitles from YouTube videos in a playlist or channel, converts them to a custom format, and saves the details in a CSV file.
2. `youtube_playlists_meta.py`: Fetches metadata of all videos in each playlist of a YouTube channel and saves the details in a CSV file.

## Prerequisites

- Python 3.6 or later
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/)

## Installation

1. **Install Python**: Ensure you have Python 3.6 or later installed on your machine. You can download it from the [official website](https://www.python.org/downloads/).

2. **Install yt-dlp**: You can install yt-dlp using pip.

   ```sh
   pip install yt-dlp
   ```

3. **Install ffmpeg**: Follow the instructions on the [ffmpeg website](https://ffmpeg.org/download.html) to install it on your system.

## Usage

### youtube_video_subs_downloader.py

1. **Run the script**:

   ```sh
   python3 youtube_video_subs_downloader.py
   ```

2. **Follow the prompts**:
   - Enter the YouTube playlist or channel video URL.
   - Enter the output CSV file name (should end with .csv).
   - Indicate whether you want to check for uploaded subtitles first (yes/no, default: no).

#### Example

```sh
python3 youtube_video_subs_downloader.py
Enter the YouTube playlist or channel video URL: https://www.youtube.com/@Tcv941/videos
Enter the output CSV file name (should end with .csv): tcv_videos.csv
Check for uploaded subtitles first? (yes/no, default: no): no
Processing video 1/126: Basic Lesson For All Tabla Beginners| Best Practice Bol | Clear Your Sound & Laya | (https://www.youtube.com/watch?v=maOzQ-sCK2o)
...
CSV file 'out/tcv_videos.csv' updated with new entries.
```

### youtube_playlists_meta.py

1. **Run the script**:

   ```sh
   python3 youtube_playlists_meta.py
   ```

2. **Follow the prompts**:
   - Enter the YouTube channel playlists URL.
   - Enter the output CSV file name (should end with .csv).

#### Example

```sh
python3 youtube_playlists_meta.py
Enter the YouTube channel playlists URL: https://www.youtube.com/@channelname/playlists
Enter the output CSV file name (should end with .csv): channel_playlists.csv
Processing playlist: Playlist 1
Processing playlist: Playlist 2
...
CSV file 'channel_playlists.csv' created.
```

## CSV Output

### youtube_video_subs_downloader.py

The output CSV file will contain the following columns:

- `title`: The title of the video.
- `url`: The URL of the video.
- `description`: The description of the video.
- `subtitles`: The cleaned subtitles in the custom format.

### youtube_playlists_meta.py

The output CSV file will contain the following columns:

- `Video Title`: The title of the video.
- `Video URL`: The URL of the video.
- `Playlist URL`: The URL of the playlist.
- `Playlist Name`: The name of the playlist.

## Contributing

If you'd like to contribute to this project, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
