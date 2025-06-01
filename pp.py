from flask import Flask, request, jsonify
import cv2
import numpy as np
from sklearn.cluster import KMeans
import os

app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def adjust_hsv_by_lighting(h, s, v, lighting):
    if lighting == "노란 조명":
        h = max(0, h - 10)
    elif lighting == "자연광":
        v = min(255, v + 10)
    elif lighting == "어두운 실내":
        v = max(0, v - 20)
    elif lighting == "하얀 조명":
        s = max(0, s - 10)
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
        lighting = request.form.get("lighting", "자연광")

        if 'image' not in request.files:
            raise Exception("이미지가 포함되지 않았습니다.")
        file = request.files['image']
        image_path = os.path.join(UPLOAD_FOLDER, "temp.jpg")
        file.save(image_path)

        img = cv2.imread(image_path)
        if img is None:
            raise Exception("이미지를 열 수 없습니다.")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_small = cv2.resize(img, (100, 100))
        img_reshape = img_small.reshape((-1, 3))

        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(img_reshape)
        colors = kmeans.cluster_centers_.astype(int)

        tones = []
        for color in colors:
            h, s, v = rgb_to_hsv(*color)
            h, s, v = adjust_hsv_by_lighting(h, s, v, lighting)
            tone = classify_tone(h, s, v)
            tones.append(tone)

        final_tone = max(set(tones), key=tones.count)

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": f"분석 결과: '{final_tone}' 톤이에요! 🎨"
                    }
                }]
            }
        })

    except Exception as e:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": f"오류 발생 😢\n{str(e)}"
                    }
                }]
            }
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
