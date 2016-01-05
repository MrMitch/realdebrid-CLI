# -*- coding: utf-8 -*-

from getpass import getpass
from hashlib import md5
from json import dump, loads

VERSION = '0.8.3'


def ask_credentials():
    """
    Ask for user credentials
    """
    username = raw_input('What is your Real-Debrid username?\n')
    raw_pass = getpass('What is your Real-Debrid password '
                       '(won\'t be displayed and won\'t be stored as plain text)?')
    password = md5(raw_pass).hexdigest()

    return username, password


def save_credentials(username, password_hash, conf_file):
    """
    Save the credentials to a file on disk
    """
    try:
        update_values({'username': username, 'password': password_hash}, conf_file)
    except BaseException as e:
        exit('Unable to save login information: %s' % str(e))


def update_values(new_values, conf_file):
    """
    Update some values in the config file
    @param new_values:
    @param conf_file:
    @return:
    """

    # make sure the file exists
    open(conf_file, 'a').close()

    with open(conf_file, 'r+b') as output_file:
        # load the config
        json = output_file.read()

        if not json:
            json = '{}'

        config = loads(json)
        config.update(new_values)
        # rewind to the begining of the file
        output_file.seek(0)
        # output the new content, and make sure no extra content is present
        dump(config, output_file, indent=4)
        output_file.truncate()


def update_value(key, value, conf_file):
    if not key:
        print 'ERROR'
    update_values({key: value}, conf_file)
