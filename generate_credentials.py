import sys
import base64
import pickle

if len(sys.argv) < 3:
    print('Please specify a GitHub username and password')
    exit(1)

username = sys.argv[1]
password = sys.argv[2]

content = base64.b64encode(bytes(username + '\n' + password, encoding='utf-8'))
pickle.dump(content, open('.credentials', 'wb'))