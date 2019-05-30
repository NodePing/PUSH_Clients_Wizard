#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import urllib.request
from getpass import getuser
from os import name as os_name
from os.path import isdir, isfile, join
from PyInquirer import prompt, Validator, ValidationError


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

    # Get the API token. If no config is present, one is created blank
    try:
        token = config['main']['token']
    except KeyError:
        config['main'] = {'token': '', 'customerid': ''}
        write_config(config, conf_ini)

        token = config['main']['token']

    # Get the subaccount ID. If no subaccount, it is left blank
    try:
        customerid = config['main']['customerid']
    except KeyError:
        customerid = None

    if not token:
        token = str(input("Please enter your API token: "))
        customerid = str(
            input("Enter your subaccount customer id (optional): "))
        message = "Do you want to store this info for later"
        save_token = inquirer_confirm(message, default=True)

        if save_token:
            config['main']['token'] = token

            if customerid:
                config['main']['customerid'] = customerid

            write_config(config, conf_ini)
    else:
        token = config['main']['token']

    return token, customerid


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
            if 'ssh_key_pass' in key or key == 'password':
                print("{0}: {1}".format(key, "*" * len(value)))
            else:
                print("{0}: {1}".format(key, value))

        get_confirmation = prompt(confirmation)

        if get_confirmation['complete']:
            complete = True
        else:
            seperator()

    return answers


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


def make_missing_dirs(sftp_client, remote_dir, remote_os):
    """ Walks a remote directory and creates directories that don't exist

    Expects a paramiko sftp client as an argument and remote directory.
    Looks to see if each directory exists and creates it if it doesn't
    """

    if remote_os == "Windows":
        remote_dir = nix_to_win_path(remote_dir)

        path_seperator = "\\"
    else:
        remote_dir = win_to_other_path(remote_dir)

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


def create_cron(_dir, client, interval, label):
    """ Creates a cronjob for the client
    """

    if client == 'POSIX':
        filename = "NodePingPUSHClient/NodePingPUSH.sh"
    elif client == 'Python' or client == 'Python3':
        filename = "NodePing{0}PUSH/NodePingPythonPUSH.py".format(client)
    elif client == 'PowerShell':
        return create_win_schedule(_dir, client, interval, label)

    full_path = join(_dir, filename)
    full_path = win_to_other_path(full_path)

    if interval == 1:
        cron = "* * * * * %s" % full_path
    elif interval == 3:
        cron = "*/3 * * * * %s" % full_path
    elif interval == 5:
        cron = "*/5 * * * * %s" % full_path
    elif interval == 15:
        cron = "*/15 * * * * %s" % full_path
    elif interval == 60:
        cron = "0 * * * * %s" % full_path
    elif interval == 240:
        cron = "0 */4 * * * %s" % full_path
    elif interval == 360:
        cron = "0 */6 * * * %s" % full_path
    elif interval == 720:
        cron = "0 */12 * * * %s" % full_path
    elif interval == 1440:
        cron = "0 0 * * * %s" % full_path

    return cron


def create_win_schedule(user, _dir, client, interval, label):
    """ Creates a Windows scheduled task
    """

    if not user:
        user = getuser()

    if label == "":
        label = "check"

    label = "NodePing-{0}".format(label)

    if client == 'PowerShell':
        filename = "NodePingPowerShellPUSH/NodePingPUSH.ps1"
        full_path = join(_dir, filename)
        full_path = nix_to_win_path(full_path)
        called_client = "powershell.exe"

        # If creating a Windows client on a POSIX OS, fix the path
        if os_name == 'posix':
            full_path = list(full_path)
            full_path.insert(1, ':')
            full_path = ''.join(full_path)

    elif client == 'Python' or client == 'Python3':
        filename = "NodePing{0}PUSH/NodePingPythonPUSH.py".format(client)
        full_path = join(_dir, filename)
        full_path = nix_to_win_path(full_path)
        called_client = "python.exe"

        # If creating a Windows client on a POSIX OS, fix the path
        if os_name == 'posix':
            full_path = list(full_path)
            full_path.insert(1, ':')
            full_path = ''.join(full_path)

    task = "$client = (Get-Command {0}).Path\n".format(called_client)
    task += "$executable = \"$client\"\n"
    task += "$argument = '{0}'\n".format(full_path)
    task += "$taskname = '{0}'\n".format(label)
    task += "$principal = New-ScheduledTaskPrincipal -LogonType 'S4U' -UserId \"{0}\"\n".format(
        user)
    task += "$action = New-ScheduledTaskAction -execute $executable -Argument $argument\n"
    task += "$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionDuration (New-TimeSpan -Days 10000) -RepetitionInterval (New-TimeSpan -Minutes {0})\n".format(
        interval)
    task += "$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden\n"
    task += 'Register-ScheduledTask -TaskName $taskname -Trigger $trigger -Action $action -Setting $settings -RunLevel 1\n'
    task += "Set-ScheduledTask $taskname -Trigger $trigger -Principal $principal\n"

    with open('windows_task.ps1', 'w') as f:
        f.write("# Run this script to create a Windows Scheduled task\n")
        f.write(task)

    return task


def win_to_other_path(path):
    """ Converts Windows \\ to /

    When doing a join on Windows, it messes up the paths for *NIX.
    This simply replaces the \\ to /
    """

    return path.replace('\\', '/')


def nix_to_win_path(path):
    """ Converts *NIX / to Windows \\

    When doing a join on *NIX, it messes up the paths for Windows.
    This simply replaces the / to \\
    """

    return path.replace('/', '\\')


def get_interval(interval):
    """ Accepts user interval input and converts to seconds
    """

    if interval == '1 minute':
        return 1
    elif interval == '3 minutes':
        return 3
    elif interval == '5 minutes':
        return 5
    elif interval == '15 minutes':
        return 15
    elif interval == '1 hour':
        return 60
    elif interval == '4 hours':
        return 240
    elif interval == '6 hours':
        return 360
    elif interval == '12 hours':
        return 720
    elif interval == '1 day':
        return 1440


class IntValidator(Validator):
    def validate(self, num):
        try:
            num = int(num.text)
        except ValueError:
            raise ValidationError(
                message="Please enter an integer",
                cursor_position=len(num.text))
