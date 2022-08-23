class UserCancelledException(Exception):
    pass


def gcd(a, b):
    return a if b == 0 else gcd(b, a % b)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def calculate_aspect_ratio(width: int, height: int):
    r = gcd(width, height)
    x = int(width / r)
    y = int(height / r)

    return x, y
