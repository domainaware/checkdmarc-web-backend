#!/usr/bin/env python

import secrets

api_key = secrets.token_hex(32)  # 64-character hex string
print(api_key)
