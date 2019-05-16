#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import urllib.request
from os.path import isdir, isfile
from PyInquirer import prompt


def inquirer_confirm(message, default=True):
    """
    """

    questions = [
        {
            'type': 'confirm',
            'name': 'response',
            'message': message,
            'default': default
        }
    ]

    answers = prompt(questions)

    return answers['response']


def write_config(config, conf_ini):
    """ Writes new contents to config file
    """

    with open(conf_ini, 'w') as configfile:
        config.write(configfile)


def get_user_token(config, conf_ini):
    """ Gets the user's NodePing API token from the config.ini file

    Gets the API key from the config.ini file with configparser.
    Accepts a read configfile as an argument. If no API key exists,
    the user is prompted to supply it
    """

    try:
        token = config['main']['token']
    except KeyError:
        config['main'] = {'token': ''}
        write_config(config, conf_ini)

        token = config['main']['token']

    if not token:
        token = str(input("Please enter your API token: "))
        message = "Do you want to store this token for later"
        # save_token = ask_yes_no(message, default="Y")
        save_token = inquirer_confirm(message, default=True)

        if save_token:
            config['main']['token'] = token

            write_config(config, conf_ini)
    else:
        token = config['main']['token']

    return token


def seperator():
    """ Prints dotted separator line 90 chars wide
    """
    print("-" * 90)


def download_file(url, dest):
    """ Downloads a file to the designated path
    """

    try:
        urllib.request.urlretrieve(url, dest)
    except urllib.error.HTTPError:
        print("File not present for download")

        return False

    return True


def list_to_dicts(_list, key_name):
    """ Converts a list to a list of dictionaries

    Takes in a list and a key name. Creates a new list where each dictionary
    has the key_name associated with each index item's value
    """

    new_list = []

    for i in _list:
        new_list.append({key_name: i})

    return new_list


def confirm_choice(questions):
    """ Prompts the user for input and repeats until the data is accepted

    Accepts the questions in the expected format for PyInquirer. Will ask the
    list of questions until the user confirms they are correct. Once the user
    says the data is correct, the dictionary created by PyInquirer is returned
    """

    complete = False

    while not complete:
        answers = prompt(questions)

        confirmation = {
            'type': 'confirm',
            'name': 'complete',
            'message': 'Is this information correct',
            'default': True
        }

        for key, value in answers.items():
            print("{0}: {1}".format(key, value))

        get_confirmation = prompt(confirmation)

        if get_confirmation['complete']:
            complete = True
        else:
            seperator()

    return answers


def make_missing_dirs(sftp_client, remote_dir, remote_os):
    """ Walks a remote directory and creates directories that don't exist

    Expects a paramiko sftp client as an argument and remote directory.
    Looks to see if each directory exists and creates it if it doesn't
    """

    if remote_os == "Windows":
        remote_dir.replace("/", "\\")

        path_seperator = "\\"
    else:
        path_seperator = "/"

    dirs = path_seperator
    dir_split = remote_dir.split('/')

    for _dir in dir_split:
        dirs += "{0}{1}".format(_dir, path_seperator)

        try:
            exists = sftp_client.stat(dirs)
        except FileNotFoundError:
            sftp_client.mkdir(dirs)


def get_sshkey(keyfile, password):
    """ Returns a paramiko private key

    Accepts the keyfile and a password for the keyfile. Finds the type of
    cryptography used for the key and returns the right Pkey value
    """

    if not isfile(keyfile):
        return False

    try:
        pk = paramiko.rsakey.RSAKey.from_private_key(
            open(keyfile), password=password)
    except paramiko.ssh_exception.SSHException:
        pass
    else:
        return pk

    try:
        pk = paramiko.dsskey.DSSKey.from_private_key(
            open(keyfile), password=password)
    except paramiko.ssh_exception.SSHException:
        pass
    else:
        return pk

    try:
        pk = paramiko.ecdsakey.ECDSAKey.from_private_key(
            open(keyfile), password=password)
    except paramiko.ssh_exception.SSHException:
        pass
    else:
        return pk

    try:
        pk = paramiko.ed25519key.Ed25519Key.from_private_key(
            open(keyfile), password=password)
    except paramiko.ssh_exception.SSHException:
        pass
    else:
        return pk

    return False
