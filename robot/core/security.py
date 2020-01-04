import hashlib


def create_signature(data: list, reverse=False):
    data.sort(reverse=reverse)
    key = ''.join(data)
    return hashlib.sha1(key.encode()).hexdigest()
