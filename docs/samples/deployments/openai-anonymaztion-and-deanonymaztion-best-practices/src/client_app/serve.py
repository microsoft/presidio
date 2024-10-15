import configargparse
from textual_serve.server import Server


def main():
    parser = configargparse.ArgParser()
    parser.add_argument("--host", type=str, default="localhost", env_var='TEXTUAL_HOST')
    parser.add_argument("--port", type=int, default=8000, env_var='TEXTUAL_PORT')
    parser.add_argument("--public_url", type=str, default=None, env_var='TEXTUAL_PUBLIC_URL')
    args = parser.parse_args()

    server = Server("python client.py --mode llm", host=args.host, port=args.port, public_url=args.public_url)
    server.serve()


if __name__ == "__main__":
    main()
