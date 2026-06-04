import os
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "BOT ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():

    print("=" * 50)
    print("WEBHOOK TETIKLENDI")
    print("=" * 50)

    try:
        data = request.get_json()

        print("GELEN VERI:")
        print(data)

    except Exception as e:

        print("HATA:")
        print(repr(e))

    return "ok", 200

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    print("WEBHOOK TEST SURUMU")
    print("PORT:", port)

    app.run(
        host="0.0.0.0",
        port=port
    )
