# checkdmarc-web-backend

The backend for a web version of checkdmarc.

## Why create a web version of checkdmarc?

Websites and much easier to use and understand for some people. Pluse, it promotes the `checkdmarc` and `parsedmarc` projects.

## Architecture

This backend is separate from the [frontend project](https://github.com/domainaware/checkdmarc-web-frontend) to that the frontend can be placed behind Cloudflare to prevent abuse and DDoS attacks. The backend cannot be placed behind CloudFlare because the forward and reverse DNS entires need to match when checking SMTP TLS. to protect the backend, a filter will be placed on the server hosting the backend that will reject any requests not coming from the frontend webserver. Additionally, an API key is required to check for SMTP TLS.

## Environment variables

The following environment variables are required and can be provided by a `.env` file.

- `API_KEY` - An API key (generate one using `generate_api_key.py`)
- `NAMESERVERS` - A comma separated list of DNS nameservers to use
- `CACHE_MAX_LEN` - The maximum size of the cache
- `CACHE_MAX_AGE_SECONDS` - The maximum age of a cached item in seconds
