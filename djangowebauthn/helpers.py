import os, base64


def token_urlsafe_without_stripping(challenge_len):
    challenge_bytes = os.urandom(challenge_len)
    challenge_base64 = base64.urlsafe_b64encode(challenge_bytes)
    if not isinstance(challenge_base64, str):
        challenge_base64 = challenge_base64.decode('utf-8')
    return challenge_base64
