#!/usr/bin/env python3

import openai
import sys
import os
import configparser

# Get config dir from environment or default to ~/.config
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')

# Read the organization_id and secret_key from the ini file ~/.config/openaiapirc
# The format is:
# [openai]
# organization_id=<your organization ID>
# secret_key=<your secret key>
# model=gpt-3.5-turbo

# If you don't see your organization ID in the file you can get it from the
# OpenAI web site: https://openai.com/organizations
def create_template_ini_file():
    """
    If the ini file does not exist create it and add the organization_id and
    secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        with open(API_KEYS_LOCATION, 'w') as f:
            f.write('[openai]\n')
            f.write('organization_id=\n')
            f.write('secret_key=\n')
            f.write('model=gpt-3.5-turbo-0613\n')

        print('OpenAI API config file created at {}'.format(API_KEYS_LOCATION))
        print('Please edit it and add your organization ID and secret key')
        print('If you do not yet have an organization ID and secret key, you\n'
               'need to register for OpenAI Codex: \n'
                'https://openai.com/blog/openai-codex/')
        sys.exit(1)


def initialize_openai_api():
    """
    Initialize the OpenAI API
    """
    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    openai.organization_id = config['openai']['organization_id'].strip('"').strip("'")
    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")
    model = config['openai']['model'].strip('"').strip("'")
    return model

model = initialize_openai_api()

cursor_position_char = int(sys.argv[1])

# Read the input prompt from stdin.
buffer = sys.stdin.read()
prompt_prefix = buffer[:cursor_position_char]
prompt_suffix = buffer[cursor_position_char:]
full_command = prompt_prefix + prompt_suffix

response = openai.ChatCompletion.create(model=model, messages=[
    {
        "role":'system',
        "content": """You are a fish shell expert, please help me complete the following command. You should only output the completed command; do not include any other explanation. Do not use Markdown backticks or any other formatting. Do not use shebangs. If the user provides a comment, respond with the command that addresses the comment.

        Examples:
        [User] git reset
        [AI] git reset --hard HEAD

        [User] git reset --soft
        [AI] git reset --soft HEAD^

        [User] # list files in current directory ordered by size and formatted as a table
        [AI] ls -l | sort -n | awk '{print $5, $9}' | column -t
        """,
    },
    {
        "role":'user',
        "content": full_command,
    }
])

# fish doesn't support line breaks in its `commandline`
completed_command = response['choices'][0]['message']['content'].rstrip()

print(completed_command)
