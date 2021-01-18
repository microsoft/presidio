from flask import Flask, request

app = Flask(__name__)


@app.route("/analyze", methods=["POST"])
def analyze():
    content = request.json
    return str(request.__dict__)


if __name__ == "__main__":
    app.run()
