from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/personalcolor", methods=["POST"])
def personalcolor():
    # 카카오 i 요청인지 확인
    try:
        # JSON 파싱
        req = request.get_json()
        print("받은 요청:", req)

        # 응답 포맷: textCard (기본 테스트)
        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "사진 분석 결과: 예시 응답입니다! 🎨"
                        }
                    }
                ]
            }
        }
        return jsonify(response)

    except Exception as e:
        print("에러 발생:", e)
        return jsonify({"error": "서버 내부 오류"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
