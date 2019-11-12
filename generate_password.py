import sys
import base64
import pickle

if len(sys.argv) < 2:
    print('Please specify a Telegram bot password')
    exit(1)

password = sys.argv[1]

content = base64.b64encode(bytes(password, encoding='utf-8'))
pickle.dump(content, open('.password', 'wb'))