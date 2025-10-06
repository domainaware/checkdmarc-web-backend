# 1/usr/bin/env python

import os
import json
import datetime

import dotenv
import checkdmarc
from expiringdict import ExpiringDict

from flask import Flask, request, Response, render_template

dotenv.load_dotenv()

cache_max_len = int(os.environ["CACHE_MAX_LEN"])
cache_max_age_seconds = int(os.environ["CACHE_MAX_AGE_SECONDS"])
cache = ExpiringDict(max_len=cache_max_len, max_age_seconds=cache_max_age_seconds)

api_key = None
api_key_required = False
if "API_KEY" in os.environ:
    api_key = os.environ["API_KEY"].strip()
else:
    print("Error: API_KEY is missing from the environment variables.")
    exit(1)

if "API_KEY_REQUIRED" in os.environ:
    api_key = True if os.environ["API_KEY_REQUIRED"].lower() in ["1", "true"] else False

nameservers = None
if "NAMESERVERS" in os.environ:
    nameservers = os.environ["NAMESERVERS"].split(",")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/domain/<domain>")
def domain(domain):
    skip_tls = True
    check_smtp_tls = request.args.get("check_smtp_tls")
    provided_api_key = request.args.get("api_key")
    if api_key_required and provided_api_key is None:
        return Response(
            "An api_key parameter must be provided.",
            status=401,
        )
    if check_smtp_tls is not None and check_smtp_tls in [1, "true"]:
        if provided_api_key is None:
            return Response(
                "An api_key parameter must be provided if check_smtp_tls is true.",
                status=401,
            )
        else:
            provided_api_key = provided_api_key.strip()
        if provided_api_key == api_key:
            skip_tls = False
        else:
            return Response("The provided API key is invalid", status=403)

    if domain in cache:
        results = cache[domain]
    else:
        results = checkdmarc.check_domains(
            [domain], nameservers=nameservers, skip_tls=skip_tls
        )
        results["checkdmarc_version"] = checkdmarc.__version__
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        results["timestamp"] = timestamp.strftime("%Y-%m-%d %H:%M UTC")
        results["timestamp_epoch"] = timestamp.timestamp()
        timedelta = datetime.timedelta(seconds=cache_max_age_seconds)
        cache_expires = timestamp + timedelta
        results["cache_expires"] = cache_expires.strftime("%Y-%m-%d %H:%M UTC")
        results["cache_expires_epoch"] = cache_expires.timestamp()
        cache[domain] = results
    status = 200
    if "error" in results["soa"]:
        if "does not exist" in results["soa"]["error"]:
            status = 404
    results = json.dumps(results, indent=2)
    mimetype = "application/json"
    return Response(response=results, status=status, mimetype=mimetype)
