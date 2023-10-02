#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Configures the metric and the client module for httpcheck
"""

import json
from os.path import join
from InquirerPy import prompt
import modules._utils as _utils


def httpcheck_metric(key_name, client):
    """ Configure the NodePing check

    Configure httpcheck information that will be a part of
    the NodePing check.
    """

    print("\nSkip fields if you don't want them checked\n")

    if client == "PowerShell":
        questions = [
            {
                'type': 'input',
                'name': 'http_code',
                'message': 'HTTP Code expected:'
            },
            {
                'type': 'input',
                'name': 'time_total',
                'message': 'Total time for entire operation'
            }
        ]
    else:
        questions = [
            {
                'type': 'input',
                'name': 'http_code',
                'message': 'HTTP Code expected:',
            },
            {
                'type': 'input',
                'name': 'time_namelookup',
                'message': 'Time to resolve the name:',
            },
            {
                'type': 'input',
                'name': 'time_connect',
                'message': 'Time until the TCP connect to remote host:',
            },
            {
                'type': 'input',
                'name': 'time_appconnect',
                'message': 'Time until the connect/handshake is complete:',
            },
            {
                'type': 'input',
                'name': 'time_pretransfer',
                'message': 'Time it took from start until the file transfer was about to begin:',
            },
            {
                'type': 'input',
                'name': 'time_redirect',
                'message': 'Time it took for all redirects:',
            },
            {
                'type': 'input',
                'name': 'time_starttransfer',
                'message': 'Time to frst byte:',
            },
            {
                'type': 'input',
                'name': 'time_total',
                'message': "Total time for entire operation",
            }
        ]

    answers = prompt(questions)

    metrics = {}

    for http_metric, value in answers.items():
        if value:
            name = "{0}.{1}".format(key_name, http_metric)
            key = "{0}{1}".format(key_name, http_metric)
            if 'http_code' in name:
                metrics.update(
                    {key: {'name': name, 'min': value, 'max': value}})
            else:
                metrics.update({key: {'name': name, 'min': 0, 'max': value}})

    return metrics


def configure_httpcheck(archive_dir, client):
    """ Configure the client for the httpcheck metric

    Configure the httpcheck metric in the client code
    """

    _utils.seperator()
    print("\n=====Configuring the httpcheck metric=====")

    questions = [
        {
            'type': 'input',
            'name': 'url',
            'message': 'The URL you want to check'
        },
        {
            'type': 'list',
            'name': 'http_method',
            'message': 'HTTP Method',
            'choices': [
                'GET',
                'POST',
                'PUT',
                'DELETE'
            ]
        },
        {
            'type': 'input',
            'name': 'content_type',
            'message': 'Content type being sent (if applicable)'
        },
        {
            'type': 'input',
            'name': 'data',
            'message': 'Data for POST/PUT (if applicable)'
        }
    ]

    answers = _utils.confirm_choice(questions)

    url = answers['url']
    http_method = answers['http_method']
    content_type = answers['content_type']
    data = answers['data']

    if client == 'POSIX':
        httpcheck_dir = "{0}/POSIX/NodePingPUSHClient/modules/httpcheck".format(
            archive_dir)
        vars_file = join(httpcheck_dir, "variables.sh")

        with open(vars_file, 'r', newline='\n') as f:
            filedata = f.read()

        filedata = filedata.replace(
            'url="https://example.com"', 'url="%s"' % url)
        filedata = filedata.replace('http_method="GET"',
                                    'http_method="%s"' % http_method)
        filedata = filedata.replace(
            'content_type="application/json"', 'content_type="%s"' % content_type)
        filedata = filedata.replace("data=''", 'data=\'%s\'' % data)

        with open(vars_file, 'w', newline='\n') as f:
            f.write(filedata)

    elif client in ("Python", "Python3"):
        httpcheck_dir = "{0}/{1}/NodePing{1}PUSH/metrics/httpcheck".format(
            archive_dir, client)

        httpcheck_file = join(httpcheck_dir, "config.py")

        with open(httpcheck_file, 'r', newline='\n') as f:
            filedata = f.read()

        filedata = filedata.replace('url = ""',
                                    'url = "%s"' % url)

        filedata = filedata.replace('http_method = "GET"',
                                    'http_method = "%s"' % http_method)

        filedata = filedata.replace('content_type = ""',
                                    'content_type = "%s"' % content_type)

        filedata = filedata.replace('data = \'\'', 'data = \'%s\'' % data)

        with open(httpcheck_file, 'w', newline='\n') as f:
            f.write(filedata)

    elif client == 'PowerShell':
        httpcheck_dir = "{0}/{1}/NodePing{1}PUSH/modules/httpcheck".format(
            archive_dir, client)

        httpcheck_file = join(httpcheck_dir, "httpcheck.json")

        # Clear contents of the httpcheck.json file
        open(httpcheck_file, 'w').close()

        with open(httpcheck_file, 'w') as f:
            f.write(json.dumps(answers, indent=8, sort_keys=True))
