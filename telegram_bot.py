import os
import glob
import time
import base64
import pickle
import requests
import github_api as github
import config_parser as parser

META_FILE = '.meta'
PASSWORD_FILE = '.password'
TOKEN_FILE = '.bot_token'
REPOSITORY_FOLDER = 'repositories'

token = parser.get_value(parser.TOKEN)
if token is None:
    print('The .bot_token file is missing. Add it to the local directory and add the bot token from Telegram.')
    exit(1)

URL = f'https://api.telegram.org/bot{token}'

MISSING_PASSWORD_STR = 'The server is missing the password file.\nPlease create a file called .password in the server\'s main directory, containing the password to log in to the bot.'


def send_message(chat_id, text):
    url = URL + f'/sendMessage?chat_id={chat_id}&text={text}'
    requests.get(url)

def delete_message(chat_id, message_id):
    url = URL + f'/deleteMessage?chat_id={chat_id}&message_id={message_id}'
    requests.get(url)

def update_meta_file(meta):
    with open(META_FILE, 'wb') as meta_file:
        pickle.dump(meta, meta_file)


if not requests.get(URL + '/getMe').ok:
    print('Unable to connect to the Telegram servers. The bot token might be wrong.')
    exit(1)

if not os.path.exists(REPOSITORY_FOLDER):
    os.mkdir(REPOSITORY_FOLDER)

if os.path.exists(META_FILE):
    # load meta information file
    with open(META_FILE, 'rb') as meta_file:
        meta = pickle.load(meta_file)
else:
    # meta information file not existing, generate new one
    meta = {'last_message_id': -1, 'known_users': [], 'password_requested': []}
    with open(META_FILE, 'wb') as meta_file:
        pickle.dump(meta, meta_file)

password = parser.get_value(parser.PASSWORD)

# the bot's update loop
while True:
    # get message updates from the Telegram servers
    response = requests.get(URL + '/getUpdates')
    update = response.json()

    if update['ok'] == True:
        result = update['result']

        for current_result in result:
            if current_result['update_id'] <= meta['last_message_id']:
                # the bot has already answered to this message
                continue

            message = current_result['message']
            user_id = message['from']['id']
            chat_id = message['chat']['id']

            if message['from']['id'] not in meta['known_users']:
                # the user who sent the message is not registered
                if user_id in meta['password_requested']:
                    # the password has previously been requested by this user
                    # delete the message containing the password
                    delete_message(chat_id, message['message_id'])

                    if password is None:
                        # the .password file is missing
                        send_message(chat_id, MISSING_PASSWORD_STR)
                    elif password == message['text']:
                        send_message(chat_id, 'Login successful!')
                        # update the meta file accordingly
                        meta['known_users'].append(user_id)
                        meta['password_requested'].remove(user_id)
                        update_meta_file(meta)
                    else:
                        # user sent the wrong password
                        send_message(chat_id, 'Wrong password!')
                else:
                    # this is the first time this user has sent a message to this bot
                    send_message(chat_id, 'Unknown username, please enter the bot\'s password')
                    meta['password_requested'].append(user_id)
                    update_meta_file(meta)

            if message['text'].startswith('/') and user_id not in meta['password_requested']:
                command = message['text'][1:].split(' ')
                if command[0] == 'start':
                    send_message(chat_id, 'Welcome!')
                elif command[0] == 'list':
                    if '-a' in command:
                    	repos = github.list_repos(modifier='all')
                    elif '-p' in command:
                        repos = github.list_repos(modifier='private')
                    else:
                        repos = github.list_repos()

                    text = 'The available repositories are:\n' + '\n'.join(repos)
                    send_message(chat_id, text)
                elif command[0] == 'clone':
                    if len(command) < 2:
                        send_message(chat_id, 'Please specify a repository to clone. You can list repositories with the /list command.')
                    else:
                        clone_url = github.get_clone_url(command[1])
                        if clone_url is github.REPOSITORY_NOT_FOUND_ERR:
                            send_message(chat_id, f'Couldn\'t find the repository "{command[1]}".')
                        else:
                            path = './' + command[1]
                            os.chdir(REPOSITORY_FOLDER)
                            if os.getcwd().split(os.sep)[-1] == REPOSITORY_FOLDER:
                                if os.path.exists(path):
                                    send_message(chat_id, 'A clone of the requested repository is already present on the server. To update the repository use the /pull command.')
                                else:
                                    send_message(chat_id, 'Cloning repository...')
                                    os.system(f'git clone {clone_url}')
                                    send_message(chat_id, 'Done!')
                            else:
                                send_message(chat_id, 'Unable to find the cloning destination, please restart the server.')
                            os.chdir('..')
                elif command[0] == 'remove':
                    if len(command) < 2:
                        send_message(chat_id, 'Please specify a repository to remove. You can list installed repositories with the /installed command.')
                    else:
                        path = './' + command[1]
                        os.chdir(REPOSITORY_FOLDER)
                        if os.path.exists(path):
                            send_message(chat_id, f'Removing repository {command[1]}...')
                            os.system(f'rm -rf {path}')
                            send_message(chat_id, 'Done!')
                        else:
                            send_message(chat_id, 'The specified repository is not installed. You can list installed repositories with the /installed command.')
                        os.chdir('..')
                elif command[0] == 'installed':
                    files = glob.glob(os.path.join(REPOSITORY_FOLDER, '*'))
                    file_names = [path.split(os.sep)[-1] for path in files]
                    if len(file_names) == 0:
                        send_message(chat_id, 'No repositories installed.')
                    else:
                        text = 'The installed repositories are:\n' + '\n'.join(file_names)
                        send_message(chat_id, text)
                elif command[0] == 'pull':
                    if len(command) < 2:
                        send_message(chat_id, 'Please specify a repository to pull from. You can list installed repositories with the /installed command.')
                    else:
                        files = glob.glob(os.path.join(REPOSITORY_FOLDER, '*'))
                        file_names = [path.split(os.sep)[-1] for path in files]
                        if command[1] in file_names:
                            os.chdir(os.path.join(REPOSITORY_FOLDER, command[1]))
                            send_message(chat_id, f'Pulling code from GitHub for repository {command[1]}...')
                            os.system('git pull')
                            send_message(chat_id, 'Done!')
                            os.chdir(os.path.join('..', '..'))
                        else:
                            send_message(chat_id, 'The specified repository is not installed. You can list installed repositories with the /installed command or clone repositories with /clone.')
                elif command[0] == 'listpython':
                    if len(command) < 2:
                        send_message(chat_id, 'Please specify a repository. You can list installed repositories with the /installed command.')
                    elif command[1] in github.list_repos(modifier='all'):
                        paths = glob.glob(os.path.join(REPOSITORY_FOLDER, command[1], '*.py'))
                        files = [path.split(os.sep)[-1] for path in paths]
                        send_message(chat_id, f'The available python files in repository {command[1]} are:\n' + '\n'.join(files))
                    else:
                        send_message(chat_id, 'Repository not installed. You can check installed repositories with the /installed command.')
                elif command[0] == 'python':
                    if len(command) < 3:
                        send_message(chat_id, 'Please specify a repository and a python file to run. You can list installed repositories with the /installed command and list python files in repositories with /listpython <repository>.')
                    elif command[1] in github.list_repos(modifier='all'):
                        paths = glob.glob(os.path.join(REPOSITORY_FOLDER, command[1], command[2]))
                        if len(paths) == 0:
                            send_message(chat_id, f'The file {command[2]} was not found in repository {command[1]}. You can list all python files with the command /listpython {command[1]}')
                        else:
                            output_file = os.path.join(*paths[0].split(os.sep)[:-1] + ['output.zip'])
                            os.system(f'python {paths[0]} 1> {output_file} 2>&1')
                            send_message(chat_id, f'Running file {command[2]}! You can check its output with /output {command[1]}')
                    else:
                        send_message(chat_id, 'Repository not installed. You can check installed repositories with the /installed command.')
                elif command[0] == 'output':
                    if len(command) < 2:
                        send_message(chat_id, 'Please specify a repository to show the output of. You can list installed repositories with the /installed command.')
                    elif os.path.exists(os.path.join(REPOSITORY_FOLDER, command[1])):
                        path = glob.glob(os.path.join(REPOSITORY_FOLDER, command[1], 'output.txt'))
                        if len(path) == 0:
                            send_message(chat_id, f'No output file found in repository {command[1]}')
                        else:
                            with open(path[0], 'r') as output_file:
                                contents = '\n'.join(output_file.readlines())
                            send_message(chat_id, contents)
                    else:
                        send_message(chat_id, f'Repository {command[1]} not found. You can check installed repositories with the /installed command.')
                elif command[0] == 'reboot':
                    send_message(chat_id, 'Rebooting...')
                    os.system('reboot')
                else:
                    send_message(chat_id, 'Unknown command.')

            # set the last handled message to the current message
            # prevents the bot from answering to messages more than once
            meta['last_message_id'] = current_result['update_id']
            update_meta_file(meta)
    time.sleep(1)