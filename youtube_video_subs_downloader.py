import sys
import csv
import subprocess
import os
import json
import re
import random
import string

def get_video_info(url):
    try:
        result = subprocess.run(["yt-dlp", "-J", url], capture_output=True, text=True, timeout=60)
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        print(f"Timeout while fetching info for {url}", file=sys.stderr)
    except json.JSONDecodeError:
        print(f"Error decoding JSON for {url}", file=sys.stderr)
    except Exception as e:
        print(f"Error fetching info for {url}: {e}", file=sys.stderr)
    return None

def get_random_suffix():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def convert_vtt_to_srt(vtt_file, srt_file):
    try:
        result = subprocess.run(["ffmpeg", "-i", vtt_file, srt_file], capture_output=True, text=True, timeout=60)
        os.remove(vtt_file)
    except subprocess.CalledProcessError as e:
        print(f"Error converting VTT to SRT: {e}", file=sys.stderr)

def get_subtitles(url, check_uploaded_subs=False):
    random_suffix = get_random_suffix()
    base_file_hi_vtt = f"/tmp/subtitle_hi_{random_suffix}"
    base_file_en_vtt = f"/tmp/subtitle_en_{random_suffix}"
    temp_file_hi_vtt = f"{base_file_hi_vtt}.hi.vtt"
    temp_file_hi_srt = f"{base_file_hi_vtt}.srt"
    temp_file_en_vtt = f"{base_file_en_vtt}.en.vtt"
    temp_file_en_srt = f"{base_file_en_vtt}.srt"
    
    subtitles = "No subtitles available"
    
    try:
        if check_uploaded_subs:
            # Try to download regular subtitles if user chose to check for them
            result = subprocess.run(["yt-dlp", "--skip-download", "--write-sub", "--sub-lang", "hi,en", 
                                     "--convert-subs", "vtt", "-o", f"/tmp/subtitle_%(ext)s_{random_suffix}.%(ext)s", url], 
                                     capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                # Check if the subtitles were actually downloaded
                if os.path.exists(temp_file_hi_vtt):
                    convert_vtt_to_srt(temp_file_hi_vtt, temp_file_hi_srt)
                    if os.path.exists(temp_file_hi_srt):
                        subtitles = convert_srt_to_custom(temp_file_hi_srt)
                        os.remove(temp_file_hi_srt)
                        return subtitles
                if os.path.exists(temp_file_en_vtt):
                    convert_vtt_to_srt(temp_file_en_vtt, temp_file_en_srt)
                    if os.path.exists(temp_file_en_srt):
                        subtitles = convert_srt_to_custom(temp_file_en_srt)
                        os.remove(temp_file_en_srt)
                        return subtitles
        
        # Check for auto-generated captions for Hindi
        result_hi = subprocess.run(["yt-dlp", "--skip-download", "--write-auto-sub", "--sub-lang", "hi", 
                                    "--convert-subs", "vtt", "-o", base_file_hi_vtt, url], 
                                    capture_output=True, text=True, timeout=60)
        if result_hi.returncode == 0 and os.path.exists(temp_file_hi_vtt):
            convert_vtt_to_srt(temp_file_hi_vtt, temp_file_hi_srt)
            if os.path.exists(temp_file_hi_srt):
                subtitles = convert_srt_to_custom(temp_file_hi_srt)
                os.remove(temp_file_hi_srt)
                return subtitles
        
        # Check for auto-generated captions for English
        result_en = subprocess.run(["yt-dlp", "--skip-download", "--write-auto-sub", "--sub-lang", "en", 
                                    "--convert-subs", "vtt", "-o", base_file_en_vtt, url], 
                                    capture_output=True, text=True, timeout=60)
        if result_en.returncode == 0 and os.path.exists(temp_file_en_vtt):
            convert_vtt_to_srt(temp_file_en_vtt, temp_file_en_srt)
            if os.path.exists(temp_file_en_srt):
                subtitles = convert_srt_to_custom(temp_file_en_srt)
                os.remove(temp_file_en_srt)
                return subtitles
        
    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp for subtitles: {e}", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print(f"Timeout while fetching subtitles for {url}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred while fetching subtitles for {url}: {e}", file=sys.stderr)
    
    return subtitles

def convert_srt_to_custom(srt_file):
    try:
        with open(srt_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        custom_format_lines = []
        timestamp_pattern = re.compile(r"(\d+:\d+:\d+,\d+)")
        subtitle_content = []
        
        current_timestamp = None
        current_text = []

        for line in lines:
            line = line.strip()
            if timestamp_pattern.match(line):  # Check if it's a timestamp line
                if current_timestamp and current_text:
                    custom_format_lines.append(f"{current_timestamp} {' '.join(current_text)}")
                current_timestamp = timestamp_pattern.match(line).group(1)
                current_text = []
            elif line and not line.isdigit():  # Add non-empty lines to current_text and exclude digit-only lines
                current_text.append(line)

        # Add the last subtitle group
        if current_timestamp and current_text:
            custom_format_lines.append(f"{current_timestamp} {' '.join(current_text)}")

        # Remove lines where content is a substring of the next line
        cleaned_lines = []
        for i in range(len(custom_format_lines) - 1):
            current_line = custom_format_lines[i]
            next_line = custom_format_lines[i + 1]
            current_text = " ".join(current_line.split()[1:])
            next_text = " ".join(next_line.split()[1:])
            if current_text not in next_text:
                cleaned_lines.append(current_line)
        if custom_format_lines:
            cleaned_lines.append(custom_format_lines[-1])  # Add the last line

        return "\n".join(cleaned_lines)

    except Exception as e:
        print(f"Error converting SRT to custom format: {e}", file=sys.stderr)
        return "Error converting subtitles"

def fetch_videos(url):
    try:
        result = subprocess.run(["yt-dlp", "-i", "--flat-playlist",
                                 "--print", "%(title)s\t%(webpage_url)s",
                                 "--playlist-items", "1-1000", url],
                                capture_output=True, text=True, check=True, timeout=60)
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp for playlist or channel: {e}", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print(f"Timeout while fetching playlist or channel info for {url}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred while fetching playlist or channel info for {url}: {e}", file=sys.stderr)
    return []

def validate_youtube_url(url):
    # Regex to match YouTube playlist or channel video URLs
    youtube_pattern = r"https://www\.youtube\.com/(?:playlist|@[^/]+/videos|@[^/]+/playlists).*"
    return re.match(youtube_pattern, url)

def video_url_exists(output_file, url):
    if not os.path.exists(output_file):
        return False
    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[1] == url:
                return True
    return False

def main():
    while True:
        playlist_url = input("Enter the YouTube playlist or channel video URL: ").strip()
        
        if not validate_youtube_url(playlist_url):
            print("Invalid YouTube URL. Please enter a valid playlist or channel video URL.")
            continue
        
        output_file_name = input("Enter the output CSV file name (should end with .csv): ").strip()
        
        if not output_file_name.endswith(".csv"):
            print("Output file should end with .csv. Please enter a valid file name.")
            continue
        
        check_uploaded_subs = input("Check for uploaded subtitles first? (yes/no, default: no): ").strip().lower() == "yes"

        output_file = os.path.join("out", output_file_name)
        os.makedirs("out", exist_ok=True)
        
        data = fetch_videos(playlist_url)
        
        if not data:
            print("No videos found in the playlist or channel. Please check the URL and try again.")
            continue
        
        with open(output_file, "a+", newline="", encoding="utf-8") as f:
            f.seek(0)
            reader = csv.reader(f)
            existing_urls = {row[1] for row in reader if row}
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if not existing_urls:
                writer.writerow(["title", "url", "description", "subtitles"])
                
            for index, line in enumerate(data):
                title, url = line.split("\t")
                if url in existing_urls:
                    print(f"Skipping video {index+1}/{len(data)}: {title} ({url}) - Already exists in the CSV file.")
                    continue
                
                try:
                    print(f"Processing video {index+1}/{len(data)}: {title} ({url})")
                    video_info = get_video_info(url)
                    description = video_info["description"] if video_info and "description" in video_info else "No description available"
                    subtitles = get_subtitles(url, check_uploaded_subs)
                    writer.writerow([title, url, description, subtitles])
                except Exception as e:
                    print(f"Error processing video {line}: {e}", file=sys.stderr)
                    writer.writerow([title, url, "Error fetching description", "Error fetching subtitles"])

        print(f"CSV file '{output_file}' updated with new entries.")
        break

if __name__ == "__main__":
    main()
