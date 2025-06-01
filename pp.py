from flask import Flask, request, jsonify
import cv2
import numpy as np
from sklearn.cluster import KMeans
import requests
from PIL import Image
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
        return "봄웜" if 20 <= h <= 50 else "여쿨"
    else:
        return "가을웜" if 10 <= h <= 40 else "겨울쿨"

def rgb_to_hsv(r, g, b):
    rgb = np.uint8([[[r, g, b]]])
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    return hsv[0][0]

@app.route("/tone", methods=["POST"])
def tone_analysis():
    try:
        body = request.get_json()
        lighting = body['action']['params'].get('lighting', '자연광')
        image_url = body['userRequest']['image']['url']

        # 이미지 다운로드
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img = img.resize((100, 100))
        img_np = np.array(img).reshape((-1, 3))

        # KMeans
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(img_np)
        colors = kmeans.cluster_centers_.astype(int)

        results = []
        for color in colors:
            h, s, v = rgb_to_hsv(*color)
            h, s, v = adjust_hsv_by_lighting(h, s, v, lighting)
            results.append(classify_tone(h, s, v))

        final = max(set(results), key=results.count)

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"분석 결과: '{final}' 톤이에요! 🎨"
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
                            "text": f"⚠️ 오류 발생: {str(e)}"
                        }
                    }
                ]
            }
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
