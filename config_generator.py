import sys
import base64
import pickle

def usage():
    print('Please choose one of:')
    print('-p    bot password')
    print('-c    GitHub credentials')
    print('-t    bot token')

def encode_and_save(file_name, content):
    content = base64.b64encode(bytes(content, encoding='utf-8'))
    pickle.dump(content, open(file_name, 'wb'))


if len(sys.argv) < 3:
    print('Please specify the type of file to generate and corresponding parameters.')
    usage()
    exit(1)

if sys.argv[1] == '-p':
    encode_and_save('.password', sys.argv[2])
elif sys.argv[1] == '-c':
    if len(sys.argv) < 4:
        print('Please specify a username and password')
        exit(1)
    encode_and_save('.credentials', sys.argv[2] + '\n' + sys.argv[3])
elif sys.argv[1] == '-t':
    encode_and_save('.token', sys.argv[2])
else:
    print(f'Unknown modifier {sys.argv[1]}')
    usage()
    exit(1)