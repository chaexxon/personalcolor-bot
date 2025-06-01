from flask import Flask, request, jsonify
import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

def adjust_hsv_by_lighting(h, s, v, lighting):
    if lighting == "노란 조명":
        h = max(0, h - 10)
    elif lighting == "자연광":
        v = min(255, v + 10)
    elif lighting == "어두운 실내":
        v = max(0, v - 20)
    return h, s, v

def classify_tone(h, s, v):
    if v > 170:
        if 20 <= h <= 50:
            return "봄웜"
        else:
            return "여쿨"
    else:
        if 10 <= h <= 40:
            return "가을웜"
        else:
            return "겨울쿨"

def rgb_to_hsv(r, g, b):
    rgb = np.uint8([[[r, g, b]]])
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    return hsv[0][0]

@app.route("/tone", methods=["POST"])
def tone_analysis():
    try:
        body = request.get_json()
        lighting = body.get("action", {}).get("params", {}).get("lighting", "자연광")
        image_url = body.get("userRequest", {}).get("params", {}).get("image", {}).get("url")

        if not image_url:
            raise ValueError("No image URL provided")

        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        img = np.array(image)
        img_small = cv2.resize(img, (100, 100))
        img_reshape = img_small.reshape((-1, 3))

        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(img_reshape)
        colors = kmeans.cluster_centers_.astype(int)

        results = []
        for color in colors:
            h, s, v = rgb_to_hsv(*color)
            h, s, v = adjust_hsv_by_lighting(h, s, v, lighting)
            tone = classify_tone(h, s, v)
            results.append(tone)

        final = max(set(results), key=results.count)

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"사진 분석 결과: '{final}' 톤이에요! 🎨"
                        }
                    }
                ]
            }
        })
    except Exception as e:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"오류 발생: {str(e)}"
                        }
                    }
                ]
            }
        })
