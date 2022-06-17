import random
from string import ascii_letters, digits


def random_string():
    return ''.join([random.choice(ascii_letters + digits) for _ in range(8)])
