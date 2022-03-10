import random
import string

def generate_random_string(length=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(length));