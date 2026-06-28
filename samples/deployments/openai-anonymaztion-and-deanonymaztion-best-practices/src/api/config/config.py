from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    class Redis:
        hostname = os.getenv('REDIS_HOSTNAME')
        port = int(os.getenv('REDIS_PORT'))
        key = os.getenv('REDIS_KEY')
        ssl = os.getenv('REDIS_SSL')

    class Presidio:
        analyzer_url = os.getenv('PRESIDIO_ANALYZER_URL')
        anonymizer_url = os.getenv('PRESIDIO_ANONYMIZER_URL')

config = Config()
