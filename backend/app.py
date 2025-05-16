from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
import io
from PIL import Image
import base64
import re

# Környezeti változók betöltése
load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# OpenAI API kulcs beállítása
openai.api_key = os.getenv('OPENAI_API_KEY')

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

ASSISTANT_ID = "asst_yRIchgQ8Z56ZYRZuqG8xeydd"

@app.route('/api/roast', methods=['POST'])
def generate_roast():
    try:
        data = request.json
        image_description = data.get('description', '')
        user_input = f"{image_description}"

        # 1. Thread létrehozása
        thread = client.beta.threads.create(
            messages=[{"role": "user", "content": user_input}]
        )
        # 2. Run indítása az assistant-tel
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )
        # 3. Megvárjuk, amíg kész a run
        import time
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == "completed":
                break
            time.sleep(1)
        # 4. Lekérjük a választ
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        roast = messages.data[0].content[0].text.value
        # Forrásjelölések eltávolítása
        roast = re.sub(r"[【\\[].*?source[】\\]]", "", roast).strip()
        return jsonify({"roast": roast})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/roast-image', methods=['POST'])
def roast_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Nincs kép feltöltve!'}), 400

        image_file = request.files['image']
        image_bytes = image_file.read()

        # Kép tömörítése (max 512x512 px)
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((512, 512))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        compressed_bytes = buffer.read()

        image_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
        data_url = f"data:image/png;base64,{image_base64}"

        # 1. Vision API: képleírás generálása
        vision_prompt = (
            "Írd le röviden, magyarul, mit látsz ezen a gamer setup képen! Csak a leírást add vissza, semmi mást."
        )
        vision_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Te egy képelemző vagy, aki rövid, magyar leírást ad a képekről."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {"type": "image_url", "image_url": {"url": data_url, "detail": "auto"}}
                    ]
                }
            ],
            temperature=0.5,
            max_tokens=150
        )
        image_description = vision_response.choices[0].message.content.strip()

        # 2. Assistant: roast generálása a képleírás alapján
        user_input = f"Íme egy gamer setup képleírása: {image_description}"
        thread = client.beta.threads.create(
            messages=[{"role": "user", "content": user_input}]
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )
        import time
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == "completed":
                break
            time.sleep(1)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        roast = messages.data[0].content[0].text.value
        # Forrásjelölések eltávolítása
        roast = re.sub(r"[【\\[].*?source[】\\]]", "", roast).strip()
        return jsonify({"roast": roast})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000) 