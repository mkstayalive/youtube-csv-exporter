import sys
import csv
import subprocess
import os
import re

def get_playlist_urls(channel_playlists_url):
    try:
        result = subprocess.run(["yt-dlp", "--flat-playlist", "--print", "%(title)s\t%(url)s", channel_playlists_url],
                                capture_output=True, text=True, check=True, timeout=60)
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp for channel: {e}", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print(f"Timeout while fetching playlists for {channel_playlists_url}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred while fetching playlists for {channel_playlists_url}: {e}", file=sys.stderr)
    return []

def fetch_videos(playlist_url):
    try:
        result = subprocess.run(["yt-dlp", "-i", "--flat-playlist", "--print", "%(title)s\t%(webpage_url)s", playlist_url],
                                capture_output=True, text=True, check=True, timeout=60)
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp for playlist: {e}", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print(f"Timeout while fetching videos for {playlist_url}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred while fetching videos for {playlist_url}: {e}", file=sys.stderr)
    return []

def validate_youtube_playlists_url(url):
    # Regex to match YouTube channel playlists URLs
    youtube_pattern = r"https://www\.youtube\.com/@[^/]+/playlists"
    return re.match(youtube_pattern, url)

def main():
    while True:
        channel_playlists_url = input("Enter the YouTube channel playlists URL: ").strip()
        
        if not validate_youtube_playlists_url(channel_playlists_url):
            print("Invalid YouTube URL. Please enter a valid channel playlists URL.")
            continue
        
        output_file_name = input("Enter the output CSV file name (should end with .csv): ").strip()
        
        if not output_file_name.endswith(".csv"):
            print("Output file should end with .csv. Please enter a valid file name.")
            continue
        
        output_file = os.path.join("out", output_file_name)
        os.makedirs("out", exist_ok=True)
        
        playlists = get_playlist_urls(channel_playlists_url)
        
        if not playlists:
            print("No playlists found in the channel. Please check the URL and try again.")
            continue
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["Video Title", "Video URL", "Playlist URL", "Playlist Name"])
            
            for playlist in playlists:
                try:
                    playlist_name, playlist_url = playlist.split("\t")
                    print(f"Processing playlist: {playlist_name}", file=sys.stderr)
                    videos = fetch_videos(playlist_url)
                    
                    for video in videos:
                        try:
                            video_title, video_url = video.split("\t")
                            writer.writerow([video_title, video_url, playlist_url, playlist_name])
                        except ValueError:
                            print(f"Skipping malformed line: {video}", file=sys.stderr)
                
                except ValueError:
                    print(f"Skipping malformed playlist: {playlist}", file=sys.stderr)
        
        print(f"CSV file '{output_file}' created.")
        break

if __name__ == "__main__":
    main()
