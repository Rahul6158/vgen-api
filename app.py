import asyncio
import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
import edge_tts

app = Flask(__name__)

# Ensure output directory exists
OUTPUT_DIR = os.path.join(app.static_folder, 'output')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voices')
def get_voices():
    async def fetch():
        voices = await edge_tts.VoicesManager.create()
        return voices.find()
    
    voice_list = asyncio.run(fetch())
    return jsonify([{
        'ShortName': v['ShortName'],
        'FriendlyName': v['FriendlyName'],
        'Locale': v['Locale'],
        'Gender': v['Gender']
    } for v in voice_list])

@app.route('/generate', methods=['POST'])
def generate_tts():
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 'en-US-GuyNeural')
    rate = data.get('rate', '+0%')
    pitch = data.get('pitch', '+0Hz')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)

    async def speak():
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(filepath)
    
    asyncio.run(speak())
    
    return jsonify({'audio_url': f'/static/output/{filename}'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
