#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join
from PyInquirer import prompt
from modules import _utils


def sqlstat_metric(key_name, client=None):
    """ Set the expected output of a MySQL/MariaDB database
    """

    if client != 'POSIX':
        message = 'What value do you expect to get when running a query? (Default: database count)'

        questions = [
            {
                'type': 'input',
                'name': 'output',
                'message': message,
            }
        ]

        answers = prompt(questions)
        output = int(answers['output'])
    else:
        output = 1

    return {key_name: {'name': key_name, 'min': output, 'max': output}}


def configure_mysqlstat(archive_dir, client):
    """ Sets up the client configuration for mysqlstat metric

    Asks the user for information to connect to their MySQL database
    Places the connection information in the config file
    """

    _utils.seperator()
    print("\n=====Configuring the mysqlstat metric=====")

    questions = [
        {
            'type': 'input',
            'name': 'username',
            'message': 'What is the database username for authentication'
        },
        {
            'type': 'password',
            'name': 'password',
            'message': 'What is the user\'s password? (Will not echo)'
        },
        {
            'type': 'input',
            'name': 'hostname',
            'message': 'What host will you be connecting on (e.g. 127.0.0.1)'
        },
        {
            'type': 'input',
            'name': 'querystring',
            'message': 'Query to run (empty for default of getting db count)'
        }
    ]

    answers = _utils.confirm_choice(questions)

    username = answers['username']
    password = answers['password']
    host = answers['hostname']
    querystring = answers['querystring']

    if client == 'POSIX':
        mysqlstat_dir = "{0}/POSIX/NodePingPUSHClient/modules/mysqlstat".format(
            archive_dir)
        vars_file = join(mysqlstat_dir, "variables.sh")

        if not querystring:
            with open(vars_file, 'r', newline='\n') as f:
                for line in f:
                    if "querystring" in line:
                        querystring = line.split('=')[1]

        with open(vars_file, 'w', newline='\n') as f:
            f.write("username=\"%s\"\n" % username)
            f.write("password=\"%s\"\n" % password)
            f.write("host=\"%s\"\n" % host)
            f.write("querystring=\"%s\"" % querystring)

    elif client in ("Python", "Python3"):
        py_questions = [
            {
                'type': 'input',
                'name': 'unix_socket',
                'message': 'Path to the mysql.sock socket (required if not Windows, usually in /tmp)'
            }
        ]

        py_answers = prompt(py_questions)
        unix_socket = py_answers['unix_socket']

        mysqlstat_dir = "{0}/{1}/NodePing{1}PUSH/metrics/mysqlstat".format(
            archive_dir, client)

        mysqlstat_file = join(mysqlstat_dir, "config.py")

        with open(mysqlstat_file, 'w', newline='\n') as f:
            f.write("username = \'%s\'\n" % username)
            if not host:
                f.write("host = \'localhost\'\n")
            else:
                f.write("host = \'%s\'\n" % host)

            if not unix_socket:
                f.write("unix_socket = \'\'\n")
            else:
                f.write("unix_socket = \'%s\'\n" % unix_socket)
            f.write("password = \'%s\'\n" % password)

            if not querystring:
                f.write(
                    "querystring = \'SELECT * FROM information_schema.SCHEMATA\'\n")
            else:
                f.write("querystring = \'%s\'\n" % querystring)

            f.write("return_db_count = True\n")

    print("\n=====mysqlstat client configuration complete=====")


def configure_pgsqlstat(archive_dir, client):
    """ Sets up the client configuration for pgsqlstat metric

    Asks the user for information to connect to their PostgreSQL database
    Places the connection information in the config file
    """

    _utils.seperator()
    print("\n=====Configuring the pgsqlstat metric=====")

    questions = [
        {
            'type': 'input',
            'name': 'username',
            'message': 'What is the database username for authentication'
        },
        {
            'type': 'input',
            'name': 'querystring',
            'message': 'Query to run (empty for default of getting db count)'
        }
    ]

    answers = _utils.confirm_choice(questions)

    username = answers['username']
    querystring = answers['querystring']

    if client == 'POSIX':
        pgsqlstat_dir = "{0}/POSIX/NodePingPUSHClient/modules/pgsqlstat".format(
            archive_dir)
        vars_file = join(pgsqlstat_dir, "variables.sh")

        if not querystring:
            with open(vars_file, 'r', newline='\n') as f:
                for line in f:
                    if "querystring" in line:
                        querystring = line.split('=')[1]

        with open(vars_file, 'w', newline='\n') as f:
            f.write("username=\"%s\"\n" % username)
            f.write("querystring=\"%s\"" % querystring)
    else:
        pass

    print("\n=====pgsqlstat client configuration complete=====")
