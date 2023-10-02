#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from os.path import join
from InquirerPy import prompt
from modules import _utils


def mongodbstat_metric():
    """ Sets mongobdstat metric to fail if the query fails or doesn't match the output
    """

    mongodbstat_fields = {
        'mongodbstat': {
            'name': 'mongodbstat',
            'min': 1,
            'max': 1
        }
    }

    return mongodbstat_fields


def configure_mongodbstat(archive_dir, client):
    """ Sets up the client configuration for mongodbstat metric

    Asks the user for information such as the comand to evaluate, expected
    output (which would be a substring), optional authentication, and
    optionally the path to the mongo executable
    """

    _utils.seperator()
    print("\n=====Configuring the mongodbstat metric=====")

    # False if the user is still adding information. This will be true if
    # the user says the info they input is correct
    complete = False

    while not complete:
        check_questions = [
            {
                'type': 'input',
                'name': 'eval_string',
                'message': 'Command for mongo to evaluate',
                'default': 'db.runCommand( {connectionStatus: 1});'
            },
            {
                'type': 'input',
                'name': 'expected_output',
                'message': 'Expected output or substring',
                'default': '"ok" : 1'
            },
            {
                'type': 'input',
                'name': 'username',
                'message': 'Username for authentication to database (skip if none)',
                'default': ''
            },
            {
                'type': 'password',
                'name': 'password',
                'message': 'Password for authentication to the database',
                'default': '',
                'when': lambda answers: answers['username']
            },
            {
                'type': 'input',
                'name': 'mongo_path',
                'message': 'What is the path to the mongo executable',
                'default': 'mongo'
            }
        ]

        answers = prompt(check_questions)

        if not answers['username']:
            username = None
        else:
            username = answers['username']

        try:
            password = answers['password']
        except KeyError:
            password = None
            answers.update({"password": ""})

        print("Evaluated command: %s" % answers['eval_string'])
        print("Expected response in output: %s" % answers['expected_output'])
        if answers['username']:
            print("Username: %s" % answers['username'])
            print("Password: ****")
        print("Mongo path: %s " % answers['mongo_path'])

        complete = _utils.inquirer_confirm("Is this information correct?")

    if client != "PowerShell":
        answers['expected_output'] = answers['expected_output'].replace(
            '"', r'\"')

    if client == 'POSIX':
        mongodbstat_dir = "{0}/POSIX/NodePingPUSHClient/modules/mongodbstat".format(
            archive_dir)
        vars_file = join(mongodbstat_dir, "variables.sh")

        if not username:
            username = ""
        if not password:
            password = ""

        with open(vars_file, 'w', newline='\n') as f:
            f.write("# This string will be evaluated by mongo with the --eval flag\n")
            f.write("eval_string=\"{0}\"\n".format(answers['eval_string']))

            f.write(
                "# All of or a portion of what you expect in the result to be successful\n")
            f.write("expected_output=\"{0}\"\n".format(
                answers['expected_output']))

            f.write("# Optional user authentication\n")
            f.write("username=\"{0}\"\n".format(username))

            f.write("# Optional password authentication\n")
            f.write("password=\"{0}\"\n".format(password))

    elif client in ("Python", "Python3"):
        mongodbstat_dir = "{0}/{1}/NodePing{1}PUSH/metrics/mongodbstat".format(
            archive_dir, client)

        mongodbstat_file = join(mongodbstat_dir, "config.py")

        with open(mongodbstat_file, 'r', newline='\n') as f:
            filedata = f.read()

        if isinstance(username, str):
            username = '\"%s\"' % username
        if isinstance(password, str):
            password = '\"%s\"' % password

        filedata = filedata.replace('eval_string = "db.runCommand( {connectionStatus: 1});"',
                                    'eval_string = "%s"' % answers['eval_string'])
        filedata = filedata.replace('expected_output = "\"ok\" : 1"',
                                    'expected_output = "%s"' % answers['expected_output'])
        filedata = filedata.replace('username = None',
                                    'username = %s' % username)
        filedata = filedata.replace('password = None',
                                    'password = %s' % password)
        filedata = filedata.replace('mongo_path = r"mongo"',
                                    'mongo_path = r"%s"' % answers['mongo_path'])

        with open(mongodbstat_file, 'w', newline='\n') as f:
            f.write(filedata)

    elif client == 'PowerShell':
        mongodbstat_dir = "{0}/{1}/NodePing{1}PUSH/modules/mongodbstat".format(
            archive_dir, client)

        mongodbstat_file = join(mongodbstat_dir, "mongodbstat.json")

        # Clear contents of the mongodbstat.json file
        open(mongodbstat_file, 'w').close()

        with open(mongodbstat_file, 'w') as f:
            f.write(json.dumps(answers, indent=8, sort_keys=True))
