# checkdmarc-web-backend

The backend for a web version of [checkdmarc](https://github.com/domainaware/checkdmarc).

## Why create a web version of checkdmarc?

Websites and much easier to use and understand for some people. Plus, it promotes the `checkdmarc` and `parsedmarc` projects.

## Architecture

This backend is separate from the [frontend project](https://github.com/domainaware/checkdmarc-web-frontend) to that the frontend can be placed behind Cloudflare to prevent abuse and DDoS attacks. The backend cannot be placed behind CloudFlare because the forward and reverse DNS entires need to match when checking SMTP TLS. This also allows the backend to display a a simple webpage explaining its purpose to anyone visiting the reverse DNS hostname with a web browser. To prevent abuse, results are stored in a short-lived cache, and an API key is required to do SMTP TLS checks.

## Environment variables

The following environment variables can be provided by a `.env` file.

- `API_KEY` - An API key to be required for some calls (generate one using `generate_api_key.py`)
- `NAMESERVERS` - A comma separated list of DNS nameservers to use (optional)
- `CACHE_MAX_AGE_SECONDS` - The maximum age of a cached item in seconds (required)
- `CACHE_MAX_LEN` - The maximum size of the cache (required)
