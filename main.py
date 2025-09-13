# 1/usr/bin/env python

import os

import dotenv
import checkdmarc

from flask import Flask, jsonify, request, Response

dotenv.load_dotenv()
api_key = None
if "API_KEY" in os.environ:
    api_key = os.environ["API_KEY"].strip()
else:
    print("Error: API_KEY is missing from the environment variables.")
    exit(1)

nameservers = None
if "NAMESERVERS" in os.environ:
    nameservers = os.environ["NAMESERVERS"].split(",")

app = Flask(__name__)


@app.route("/domain/<domain>")
def domain(domain):
    skip_tls = True
    check_smtp_tls = request.args.get("check_smtp_tls")
    provided_api_key = request.args.get("api_key")
    if check_smtp_tls in [1, "true", "True"]:
        if provided_api_key is None:
            return Response(
                "An api_key parameter must be provided if check_smtp_tls is true",
                status=401,
            )
        else:
            provided_api_key = provided_api_key.strip()
        if provided_api_key == api_key:
            skip_tls = False
        else:
            return Response("The provided API key is invalid", status=403)

    results = checkdmarc.check_domains(
        [domain], nameservers=nameservers, skip_tls=skip_tls
    )
    return jsonify(results)
