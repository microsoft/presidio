from flask import Flask, request
from presidio_anonymizer.domain.anonymizer_request import AnonymizerRequest
from presidio_anonymizer.anonymizer_engine import AnonymizerEngine
from presidio_anonymizer.domain.invalid_exception import InvalidParamException

app = Flask(__name__)


@app.route("/anonymize", methods=["POST"])
def anonymize():
    content = request.get_json()
    if not content:
        return "Invalid request json", 400
    try:
        data = AnonymizerRequest.validate_and_convert(content)
    except InvalidParamException as e:
        return e.err, 400
    except Exception:
        # TODO add logger 2652
        return "Internal server error", 500
    engine = AnonymizerEngine(data)
    text = engine.anonymize()
    return text


if __name__ == "main":
    app.run()
