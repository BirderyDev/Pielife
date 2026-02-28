import hmac
import hashlib

def HMAC_SHA1(key, message):
    hmac_object = hmac.new(key.encode(), message.encode(), hashlib.sha1)
    return hmac_object.hexdigest()

hash_value = HMAC_SHA1("secret_phrase", "76561198752760796@steamgames.com")
print(hash_value)