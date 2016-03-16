from random import choice
from string import ascii_uppercase

def rand_str(l=6):
    return ''.join(choice(ascii_uppercase) for i in range(l))
