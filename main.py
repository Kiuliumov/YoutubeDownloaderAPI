from flask import Flask, request, Response
from pytube import YouTube
import io

app = Flask(__name__)

@app.route('/download/<path:link>/<quality>', methods=['GET'])
def download(link, quality):
    try:
        yt = YouTube(link)
        stream = yt.streams.filter(res=quality, file_extension='mp4').first()
        if not stream:
            return {"error": "Quality not available"}, 404

        buffer = io.BytesIO()
        stream.stream_to_buffer(buffer)
        buffer.seek(0)

        return Response(
            buffer,
            mimetype='video/mp4',
            headers={
                "Content-Disposition": f"attachment; filename={yt.title}.mp4"
            }
        )
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)
