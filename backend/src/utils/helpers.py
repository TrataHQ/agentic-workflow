from enum import Enum
import random
import string
import time

class IdPrefix(str, Enum):
    """IdPrefix length should be three char"""
    APP = 'wf_app'
    CONNECTION = 'wf_con'


def generateRandomId(prefix: str, length: int = 8, delimiter: str = '.') -> str:
    """Generates a random alphanumeric ID with the given prefix.
    Args:
        prefix (str): The prefix to add to the generated ID.
        length (int): The length of the alphanumeric part of the ID. Default is 8.
    Returns:
        str: A string containing the prefix followed by a random alphanumeric ID.
    """
    timestamp = str(int(time.time()))
    alphanumeric_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"{prefix}{delimiter}{timestamp}{delimiter}{alphanumeric_id}"