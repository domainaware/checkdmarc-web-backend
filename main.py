# 1/usr/bin/env python

import os
import json
import datetime

import dotenv
import checkdmarc
from expiringdict import ExpiringDict

from flask import Flask, request, Response, render_template

dotenv.load_dotenv()

nameservers = os.getenv("NAMESERVERS")
if nameservers:
    nameservers = nameservers.lower().split(",")

required_environment_variables = ["API_KEY", "CACHE_MAX_LEN", "CACHE_MAX_AGE_SECONDS"]
missing_required_environment_variables = []
for var in required_environment_variables:
    if var not in os.environ:
        missing_required_environment_variables.append(var)
if len(missing_required_environment_variables):
    print(
        f"The following required environment variables are missing: {",".join(missing_required_environment_variables)}"
    )
    exit(1)

api_key = os.getenv("API_KEY")
if api_key:
    api_key = api_key.strip()
cache_max_len = int(os.getenv("CACHE_MAX_LEN"))
cache_max_age_seconds = int(os.getenv("CACHE_MAX_AGE_SECONDS"))
cache = ExpiringDict(
    max_len=int(cache_max_len), max_age_seconds=int(cache_max_age_seconds)
)


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/domain/<domain>")
def domain(domain):
    skip_tls = True
    check_smtp_tls = bool(request.args.get("check_smtp_tls"))
    provided_api_key = request.args.get("api_key")

    if check_smtp_tls:
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
