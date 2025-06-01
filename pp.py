from flask import Flask, request, Response
import cv2
import numpy as np
from sklearn.cluster import KMeans
import requests
import json

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
        lighting = lighting if lighting in ["자연광", "노란 조명", "어두운 실내"] else "자연광"
        image_url = body.get("userRequest", {}).get("params", {}).get("image", {}).get("url")

        if not image_url:
            raise ValueError("No image URL provided")

        # ✅ Wikimedia 403 차단 우회용 User-Agent 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; PersonalColorBot/1.0; +https://personalcolor-bot.onrender.com)'
        }
        response = requests.get(image_url, headers=headers, timeout=5)
        response.raise_for_status()

        # ✅ OpenCV로 이미지 디코딩
        nparr = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("OpenCV로 이미지 디코딩 실패")

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_small = cv2.resize(img, (100, 100))
        img_reshape = img_small.reshape((-1, 3))

        kmeans = KMeans(n_clusters=5, random_state=42, n_init="auto")
        kmeans.fit(img_reshape)
        colors = kmeans.cluster_centers_.astype(int)

        results = []
        for color in colors:
            h, s, v = rgb_to_hsv(*color)
            h, s, v = adjust_hsv_by_lighting(h, s, v, lighting)
            tone = classify_tone(h, s, v)
            results.append(tone)

        final = max(set(results), key=results.count)

        kakao_response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"사진 분석 결과: '{final}' 통이에요! 🎨"
                        }
                    }
                ]
            }
        }

        return Response(
            json.dumps(kakao_response, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )

    except Exception as e:
        error_response = {
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
        }
        return Response(
            json.dumps(error_response, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
