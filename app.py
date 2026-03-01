import asyncio
import uuid
from flask import Flask, request, jsonify, send_file
import edge_tts
import os

app = Flask(__name__)

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)


@app.route("/generate", methods=["POST"])
def generate_tts():
    data = request.json
    text = data.get("text")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(TEMP_DIR, filename)

    async def speak():
        communicate = edge_tts.Communicate(
            text,
            voice="te-IN-ShrutiNeural",  # 🔥 Locked voice
            rate="-3%",
            pitch="+2Hz"
        )
        await communicate.save(filepath)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(speak())
    loop.close()

    return send_file(
        filepath,
        mimetype="audio/mpeg",
        as_attachment=False
    )


@app.route("/")
def health():
    return jsonify({"status": "API is running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
