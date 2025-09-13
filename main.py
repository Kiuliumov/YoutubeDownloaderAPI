from flask import Flask, request, Response, stream_with_context
import yt_dlp
import re
import os

app = Flask(__name__)

QUALITY_MAP = {
    "1080": "bestvideo[height<=1080]+bestaudio/best",
    "720": "bestvideo[height<=720]+bestaudio/best",
    "480": "bestvideo[height<=480]+bestaudio/best",
    "360": "bestvideo[height<=360]+bestaudio/best",
    "best": "bestvideo+bestaudio/best",
    "audio": "bestaudio",
}

def sanitize_filename(name: str) -> str:
    """Remove characters invalid for filenames"""
    return re.sub(r'[\\/*?:"<>|]', "", name)

@app.route('/download', methods=['GET'])
def download():
    link = request.args.get("link")
    quality = request.args.get("quality", "best")

    if not link:
        return {"error": "Missing link"}, 400

    ydl_quality = QUALITY_MAP.get(quality, quality)

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            title = sanitize_filename(info.get('title', 'video'))
            filename = f"{title}.mp4"

        ydl_opts = {
            'format': ydl_quality,
            'quiet': True,
            'outtmpl': '-',  
        }

        def generate():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                process = ydl.urlopen(link)
                while True:
                    chunk = process.read(1024*1024)
                    if not chunk:
                        break
                    yield chunk

        return Response(
            stream_with_context(generate()),
            mimetype='video/mp4',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
