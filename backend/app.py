from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
import io
from PIL import Image
import base64

# Környezeti változók betöltése
load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# OpenAI API kulcs beállítása
openai.api_key = os.getenv('OPENAI_API_KEY')

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/api/roast', methods=['POST'])
def generate_roast():
    try:
        data = request.json
        image_description = data.get('description', '')
        
        # Prompt összeállítása
        prompt = f"""Kérlek, generálj egy szarkasztikus, humoros roast-ot egy gamer setupról a következő leírás alapján: {image_description}
        
        A roast-nak tartalmaznia kell:
        1. Egy szarkasztikus megjegyzést a setup-ról
        2. Egy Performate termék javaslatot a problémára
        3. Egy vicces zárómondatot
        
        A válasz formátuma:
        - Rövid és tömör
        - Humoros és szarkasztikus
        - Természetes, beszélgetős hangnem
        - Magyar nyelvű
        - Tartalmaz egy Performate termék javaslatot (HyPerform, MediScreen, VascuLord, vagy Sleepery)
        
        Példa formátum:
        "Ez a setup annyira káosz, hogy még a Windows 98 is megirigyelné. Talán egy Performate HyPerform segítene, hogy ne akadjon be minden kattintásod."
        """

        # OpenAI API hívás
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Te egy szarkasztikus, humoros gamer setup roastoló vagy. A válaszaid viccesek, de nem sértőek."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=150
        )

        roast = response.choices[0].message.content.strip()
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

        # Prompt magyarul, brandinggel, max 5 mondat
        prompt = (
            "Kérlek, generálj egy szarkasztikus, humoros roast-ot a feltöltött gamer setup képről! "
            "A roast legyen többrétegű, tartalmazzon egy Performate termékjavaslatot (HyPerform, MediScreen, VascuLord, Sleepery), "
            "és legyen beszélgetős, magyar nyelvű, de ne legyen sértő. "
            "A válaszod legyen maximum 300 karakter! Ha hosszabb lenne, vágd le 300 karakternél. Példa: "
            "'Ez a setup annyira káosz, hogy még a Windows 98 is megirigyelné. Talán egy Performate HyPerform segítene, hogy ne akadjon be minden kattintásod.'"
        )

        # OpenAI Vision API hívás
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Te egy szarkasztikus, humoros gamer setup roastoló vagy. A válaszaid viccesek, de nem sértőek."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url, "detail": "auto"}}
                    ]
                }
            ],
            temperature=0.8,
            max_tokens=150
        )

        roast = response.choices[0].message.content.strip()
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