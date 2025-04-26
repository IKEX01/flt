from flask import Flask, request, jsonify
import os
import yt_dlp
import re
import logging
import validators
from flask_cors import CORS

from logger import setup_logging
from config import PROXY, FLASK_RUN_HOST, FLASK_RUN_PORT

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def extract_video_id(link: str) -> str:
    patterns = [
        r'youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=)([0-9A-Za-z_-]{11})',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'youtube\.com\/(?:playlist\?list=[^&]+&v=|v\/)([0-9A-Za-z_-]{11})',
        r'youtube\.com\/(?:.*\?v=|.*\/)([0-9A-Za-z_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)

    logger.error("Invalid YouTube link provided.")
    raise ValueError("Invalid YouTube link provided.")

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')
    if not video_url:
        logger.warning("No URL provided in the request.")
        return jsonify({'error': 'No URL provided'}), 400

    if not validators.url(video_url):
        logger.error("Invalid URL format.")
        return jsonify({'error': 'Invalid URL format'}), 400

    try:
        video_id = extract_video_id(video_url)
    except ValueError as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 400

    output_path = f'downloads/{video_id}.mp3'

    if os.path.exists(output_path):
        logger.info(f"File already exists: {output_path}")
        return jsonify({'message': 'File already exists', 'file_path': output_path})

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': output_path,
        'proxy': PROXY,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': False,
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        logger.info(f"Download complete: {output_path}")
        return jsonify({'message': 'Download complete', 'file_path': output_path})
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(host=FLASK_RUN_HOST, port=FLASK_RUN_PORT)
