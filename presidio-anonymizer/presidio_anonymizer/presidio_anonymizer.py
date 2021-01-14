from flask import Flask, request

app = Flask(__name__)


@app.route('/anonymize', methods=['POST'])
def anonymize():
    content = request.json
    return content


if __name__ == 'main':
    app.run()
