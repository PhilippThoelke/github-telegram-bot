import os
import base64
import pickle

PASSWORD = 0
CREDENTIALS = 1
TOKEN = 2

PASSWORD_FILE = '.password'
CREDENTIALS_FILE = '.credentials'
TOKEN_FILE = '.token'

def load_values(file):
    if os.path.exists(file):
        with open(file, 'rb') as current_file:
            encoded = pickle.load(current_file)

        decoded = base64.b64decode(encoded)
        return str(decoded, encoding='utf-8')

def get_value(value_type):
    if value_type == PASSWORD:
        return load_values(PASSWORD_FILE)
    elif value_type == CREDENTIALS:
        return load_values(CREDENTIALS_FILE).split('\n')
    elif value_type == TOKEN:
        return load_values(TOKEN_FILE)
    else:
        return None
