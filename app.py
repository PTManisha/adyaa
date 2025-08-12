# import os
# import re
# import subprocess
# import textwrap
# from datetime import datetime
# from flask import Flask, request, jsonify, send_from_directory, abort
# import requests
# from gtts import gTTS

# app = Flask(__name__)

# # ===== CONFIG =====
# GEMINI_API_KEY = "AIzaSyAG1I7dA-p57W93mO8GXa_OAT_ZO6Ddjwg"  # Replace with your key
# PEXELS_API_KEY = "Pomy8i7f1a2K4sMC54l4ExbSxXWK0cYKKsoJsi7djP9ApMSp4qtDKP7U"  # Replace with your key
# MODEL = "gemini-2.0-flash"

# VIDEOS_DIR = "videos"
# os.makedirs(VIDEOS_DIR, exist_ok=True)

# # Style config for subtitles
# SUB_STYLE = {
#     "font": "Verdana",
#     "fontsize": 20,
#     "primary_color": "&H00FFFFFF&",
#     "outline_color": "&H00000000&",
#     "back_color": "&H00000000&",
#     "shadow": 0,
#     "position_y": 60,
#     "spacing": 1.2,
# }

# # -------- Utilities --------
# def clean_text(text):
#     return re.sub(r'[*#_\[\]"]', '', text).strip()

# def extract_spoken_text(full_script):
#     lines = full_script.split('\n')
#     spoken_lines = []
#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue
#         if line.startswith('(') or line.lower().startswith(('visual:', 'audio:', 'me:')):
#             continue
#         spoken_lines.append(line)
#     return " ".join(spoken_lines)

# def generate_script(topic):
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"
#     prompt = f"""
#     Create a luxury-style Instagram Reel script about: {topic}

#     Requirements:
#     - First line: Intriguing hook (question/statement)
#     - 3 key insights (concise, valuable)
#     - Powerful closing CTA
#     - Use 2-3 premium emojis (✨🔥💎)
#     - Sophisticated but conversational tone
#     - No hashtags/brackets
#     - 90-110 words
#     - Sound like an expert sharing exclusive knowledge
#     """
#     payload = {
#         "contents": [{"parts": [{"text": prompt}]}],
#         "generationConfig": {
#             "temperature": 0.7,
#             "topP": 0.9,
#             "maxOutputTokens": 350
#         }
#     }
#     try:
#         r = requests.post(url, json=payload)
#         r.raise_for_status()
#         text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
#         return clean_text(text)
#     except Exception as e:
#         print(f"Error generating script: {e}")
#         return ("Want exclusive insights on " + topic + "? ✨ "
#                 "1. Elite tip one. "
#                 "2. Premium strategy two. "
#                 "3. Luxury secret three. "
#                 "Apply now! 💎")

# def generate_voiceover(text, base_path):
#     path = base_path + "_voiceover.mp3"
#     try:
#         tts = gTTS(text=text, lang='en', slow=False)
#         tts.save(path)

#         mastered_path = base_path + "_voiceover_mastered.mp3"
#         subprocess.run([
#             "ffmpeg", "-y", "-i", path,
#             "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
#             "-ar", "48000",
#             "-ac", "2",
#             "-b:a", "256k",
#             mastered_path
#         ], check=True)
#         return mastered_path
#     except Exception as e:
#         print(f"Voiceover error: {e}")
#         return path

# def download_video(topic, base_path):
#     try:
#         url = f"https://api.pexels.com/videos/search?query={topic}+aesthetic&per_page=5&orientation=portrait&size=medium"
#         headers = {"Authorization": PEXELS_API_KEY}
#         r = requests.get(url, headers=headers)
#         r.raise_for_status()
#         videos = [v for v in r.json()["videos"] if v["height"] > v["width"]]
#         if not videos:
#             raise Exception("No vertical videos found")
#         video_url = sorted(videos, key=lambda v: (-v["width"], v["duration"]))[0]["video_files"][0]["link"]

#         path = base_path + "_video.mp4"
#         with requests.get(video_url, stream=True) as vid:
#             vid.raise_for_status()
#             with open(path, "wb") as f:
#                 for chunk in vid.iter_content(8192):
#                     f.write(chunk)
#         return path
#     except Exception as e:
#         print(f"Video download error: {e}")
#         return None

# def create_captions(text, base_path):
#     path = base_path + "_captions.srt"
#     sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
#     srt = ""
#     start = 0.0
#     for i, sentence in enumerate(sentences, 1):
#         duration = min(max(len(sentence.split()) * 0.4, 2), 4)
#         end = start + duration
#         wrapped = textwrap.wrap(sentence, width=25)
#         wrapped = [line.center(25) for line in wrapped][:2]

#         srt += f"{i}\n"
#         srt += f"00:00:{start:05.2f} --> 00:00:{end:05.2f}\n"
#         joined = "\n".join(wrapped)
#         srt += f"{joined}\n\n"

#         start = end
#     with open(path, "w", encoding="utf-8") as f:
#         f.write(srt)
#     return path

# def merge_video_audio_captions(video_path, audio_path, captions_path, output_path):
#     captions_path_escaped = captions_path.replace('\\', '\\\\').replace(':', '\\:')
#     vf = (
#         f"scale=1080:1920:force_original_aspect_ratio=decrease,"
#         f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
#         f"subtitles='{captions_path_escaped}':"
#         f"force_style='FontName={SUB_STYLE['font']},"
#         f"Fontsize={SUB_STYLE['fontsize']},"
#         f"PrimaryColour={SUB_STYLE['primary_color']},"
#         f"BackColour={SUB_STYLE['back_color']},"
#         f"OutlineColour={SUB_STYLE['outline_color']},"
#         f"BorderStyle=3,"
#         f"Outline={SUB_STYLE['shadow']},"
#         f"Alignment=2,"
#         f"MarginV={SUB_STYLE['position_y']},"
#         f"Spacing={SUB_STYLE['spacing']}'"
#     )

#     cmd = [
#         "ffmpeg", "-y",
#         "-i", video_path,
#         "-i", audio_path,
#         "-map", "0:v",
#         "-map", "1:a",
#         "-vf", vf,
#         "-c:v", "libx264",
#         "-preset", "slow",
#         "-crf", "18",
#         "-c:a", "aac",
#         "-b:a", "192k",
#         "-shortest",
#         output_path
#     ]

#     try:
#         completed_process = subprocess.run(cmd, check=True, capture_output=True, text=True)
#         print("FFmpeg output:", completed_process.stdout)
#     except subprocess.CalledProcessError as e:
#         print("FFmpeg failed:")
#         print("stdout:", e.stdout)
#         print("stderr:", e.stderr)
#         raise Exception(f"FFmpeg merge failed: {e}")

# @app.route('/videos/<filename>')
# def serve_video(filename):
#     if '..' in filename or filename.startswith('/'):
#         abort(400)  # prevent path traversal
#     return send_from_directory(VIDEOS_DIR, filename)

# @app.route('/generate_reel', methods=['POST'])
# def generate_reel():
#     data = request.get_json(force=True)
#     topic = data.get('topic')
#     if not topic:
#         return jsonify({"error": "Missing 'topic' parameter"}), 400

#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     base_path = os.path.join(VIDEOS_DIR, f"{timestamp}")

#     # 1. Generate script
#     full_script = generate_script(topic)
#     spoken_text = extract_spoken_text(full_script)

#     # 2. Generate voiceover
#     voice_path = generate_voiceover(spoken_text, base_path)

#     # 3. Download video
#     video_path = download_video(topic, base_path)
#     if not video_path:
#         return jsonify({"error": "Failed to download video"}), 500

#     # 4. Create captions
#     captions_path = create_captions(spoken_text, base_path)

#     # 5. Merge all
#     output_path = base_path + "_final_reel.mp4"
#     try:
#         merge_video_audio_captions(video_path, voice_path, captions_path, output_path)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     video_url = request.host_url + "videos/" + os.path.basename(output_path)
#     return jsonify({"video_url": video_url})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')


import os
import re
import subprocess
import textwrap
import threading
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, abort
import requests
from gtts import gTTS

app = Flask(__name__)

# ===== CONFIG =====
GEMINI_API_KEY = "AIzaSyAG1I7dA-p57W93mO8GXa_OAT_ZO6Ddjwg"
PEXELS_API_KEY = "Pomy8i7f1a2K4sMC54l4ExbSxXWK0cYKKsoJsi7djP9ApMSp4qtDKP7U"
MODEL = "gemini-2.0-flash"

VIDEOS_DIR = "videos"
os.makedirs(VIDEOS_DIR, exist_ok=True)

jobs = {}  # job_id → {"status": "processing"/"done"/"error", "video_url": None or str}

# Style config for subtitles
SUB_STYLE = {
    "font": "Verdana",
    "fontsize": 20,
    "primary_color": "&H00FFFFFF&",
    "outline_color": "&H00000000&",
    "back_color": "&H00000000&",
    "shadow": 0,
    "position_y": 60,
    "spacing": 1.2,
}

# -------- Utilities --------
def clean_text(text):
    return re.sub(r'[*#_\[\]"]', '', text).strip()

def extract_spoken_text(full_script):
    lines = full_script.split('\n')
    spoken_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('(') or line.lower().startswith(('visual:', 'audio:', 'me:')):
            continue
        spoken_lines.append(line)
    return " ".join(spoken_lines)

def generate_script(topic):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""
    Create a luxury-style Instagram Reel script about: {topic}

    Requirements:
    - First line: Intriguing hook (question/statement)
    - 3 key insights (concise, valuable)
    - Powerful closing CTA
    - Use 2-3 premium emojis (✨🔥💎)
    - Sophisticated but conversational tone
    - No hashtags/brackets
    - 90-110 words
    - Sound like an expert sharing exclusive knowledge
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9,
            "maxOutputTokens": 350
        }
    }
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return clean_text(text)
    except Exception as e:
        print(f"Error generating script: {e}")
        return ("Want exclusive insights on " + topic + "? ✨ "
                "1. Elite tip one. "
                "2. Premium strategy two. "
                "3. Luxury secret three. "
                "Apply now! 💎")

def generate_voiceover(text, base_path):
    path = base_path + "_voiceover.mp3"
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(path)

        mastered_path = base_path + "_voiceover_mastered.mp3"
        subprocess.run([
            "ffmpeg", "-y", "-i", path,
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-ar", "48000",
            "-ac", "2",
            "-b:a", "256k",
            mastered_path
        ], check=True)
        return mastered_path
    except Exception as e:
        print(f"Voiceover error: {e}")
        return path

def download_video(topic, base_path):
    try:
        url = f"https://api.pexels.com/videos/search?query={topic}+aesthetic&per_page=5&orientation=portrait&size=medium"
        headers = {"Authorization": PEXELS_API_KEY}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        videos = [v for v in r.json()["videos"] if v["height"] > v["width"]]
        if not videos:
            raise Exception("No vertical videos found")
        video_url = sorted(videos, key=lambda v: (-v["width"], v["duration"]))[0]["video_files"][0]["link"]

        path = base_path + "_video.mp4"
        with requests.get(video_url, stream=True) as vid:
            vid.raise_for_status()
            with open(path, "wb") as f:
                for chunk in vid.iter_content(8192):
                    f.write(chunk)
        return path
    except Exception as e:
        print(f"Video download error: {e}")
        return None

def create_captions(text, base_path):
    path = base_path + "_captions.srt"
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    srt = ""
    start = 0.0
    for i, sentence in enumerate(sentences, 1):
        duration = min(max(len(sentence.split()) * 0.4, 2), 4)
        end = start + duration
        wrapped = textwrap.wrap(sentence, width=25)
        wrapped = [line.center(25) for line in wrapped][:2]

        srt += f"{i}\n"
        srt += f"00:00:{start:05.2f} --> 00:00:{end:05.2f}\n"
        joined = "\n".join(wrapped)
        srt += f"{joined}\n\n"

        start = end
    with open(path, "w", encoding="utf-8") as f:
        f.write(srt)
    return path

def merge_video_audio_captions(video_path, audio_path, captions_path, output_path):
    captions_path_escaped = captions_path.replace('\\', '\\\\').replace(':', '\\:')
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
        f"subtitles='{captions_path_escaped}':"
        f"force_style='FontName={SUB_STYLE['font']},"
        f"Fontsize={SUB_STYLE['fontsize']},"
        f"PrimaryColour={SUB_STYLE['primary_color']},"
        f"BackColour={SUB_STYLE['back_color']},"
        f"OutlineColour={SUB_STYLE['outline_color']},"
        f"BorderStyle=3,"
        f"Outline={SUB_STYLE['shadow']},"
        f"Alignment=2,"
        f"MarginV={SUB_STYLE['position_y']},"
        f"Spacing={SUB_STYLE['spacing']}'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-map", "0:v",
        "-map", "1:a",
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed:", e.stderr)
        raise Exception(f"FFmpeg merge failed: {e}")

# -------- Background Worker --------
def process_reel(job_id, topic, host_url):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = os.path.join(VIDEOS_DIR, f"{timestamp}")

        full_script = generate_script(topic)
        spoken_text = extract_spoken_text(full_script)
        voice_path = generate_voiceover(spoken_text, base_path)
        video_path = download_video(topic, base_path)
        if not video_path:
            jobs[job_id]["status"] = "error"
            return
        captions_path = create_captions(spoken_text, base_path)
        output_path = base_path + "_final_reel.mp4"
        merge_video_audio_captions(video_path, voice_path, captions_path, output_path)

        video_url = host_url + "videos/" + os.path.basename(output_path)  # ✅ now safe
        jobs[job_id]["status"] = "done"
        jobs[job_id]["video_url"] = video_url
    except Exception as e:
        jobs[job_id]["status"] = "error"
        print(f"Error processing job {job_id}:", e)

@app.route('/generate_reel', methods=['POST'])
def generate_reel():
    data = request.get_json(force=True)
    topic = data.get('topic')
    if not topic:
        return jsonify({"error": "Missing 'topic' parameter"}), 400

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing", "video_url": None}

    host_url = request.host_url  # ✅ capture here

    threading.Thread(target=process_reel, args=(job_id, topic, host_url), daemon=True).start()

    return jsonify({"job_id": job_id, "status": "processing"})


@app.route('/check_status/<job_id>', methods=['GET'])
def check_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Invalid job_id"}), 404
    return jsonify(job)

@app.route('/videos/<filename>')
def serve_video(filename):
    if '..' in filename or filename.startswith('/'):
        abort(400)
    return send_from_directory(VIDEOS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
