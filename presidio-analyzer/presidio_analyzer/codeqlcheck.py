# codeql_oscmd_injection.py
import os

def vuln_cmd():
    arg = input("file> ")
    # vulnerable: direct user input into shell command
    os.system("ls " + arg)


# codeql_subprocess_shell.py
import subprocess

def vuln_shell():
    user = input("user> ")
    # vulnerable: subprocess with shell=True and untrusted input
    subprocess.run(f"echo {user} | sed 's/^/hello /'", shell=True)


# codeql_pickle_deser.py
import pickle
import base64

def vuln_pickle(b64):
    data = base64.b64decode(b64)   # assume attacker-controlled payload
    # vulnerable: untrusted deserialization
    obj = pickle.loads(data)
    return obj


# codeql_path_traversal.py
def vuln_path():
    p = input("path> ")
    # vulnerable: direct open of user-supplied path
    with open(p, "r") as f:
        return f.read()


# codeql_crypto_weak.py
import random, hashlib

def vuln_crypto(secret):
    # vulnerable: using md5 for security and random for tokens
    token = str(random.random())
    h = hashlib.md5((secret + token).encode()).hexdigest()
    return h


# codeql_flask_sql.py
from flask import Flask, request
import sqlite3
app = Flask(__name__)

@app.route("/search")
def search():
    q = request.args.get("q")   # taint source
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE name = '%s'" % q)  # vulnerable sink
    return str(c.fetchall())


vuln_cmd()

vuln_shell()

vuln_path()
