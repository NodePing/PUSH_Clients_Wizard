#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from os.path import join
from pprint import pprint
from PyInquirer import prompt


def fileage_metric(key_name):
    """
    """

    get_names = True
    names = {}
    i = 1

    while get_names:

        questions = [
            {
                'type': 'input',
                'name': 'name',
                'message': 'What is the full /path/to/file?'
            },
            {
                'type': 'input',
                'name': 'days',
                'message': 'How many days old max should the file be?'
            },
            {
                'type': 'input',
                'name': 'hours',
                'message': 'How many hours old max should the file be?'
            },
            {
                'type': 'input',
                'name': 'minutes',
                'message': 'How many minutes old max should the file be?'
            },
            {
                'type': 'confirm',
                'name': 'get_another',
                'message': 'Add another to the check?'
            }
        ]

        answers = prompt(questions)

        name = "{0}.{1}".format(key_name, answers['name'])
        key = "{0}{1}".format(key_name, i)
        days = answers['days']
        hours = answers['hours']
        minutes = answers['minutes']

        if not days:
            days = 0
        elif not hours:
            hours = 0
        elif not minutes:
            minutes = 0

        names.update(
            {key: {'name': name, 'days': days, 'hours': hours, 'minutes': minutes, 'min': 1, 'max': 1}})

        if answers['get_another']:
            i += 1
        else:
            break

    return names


def configure_fileage(keys, all_metrics, archive_dir, client):
    """ Puts the fileage metric info in its necessary config file

    Sets up the fileage metrics in the appropriate client config files
    """

    print("\n=====Configuring the fileage metric=====")

    if client == 'POSIX':
        fileage_dir = "{0}/POSIX/NodePingPUSHClient/modules/fileage".format(
            archive_dir)
        fileage_file = join(fileage_dir, "fileage.txt")

        lines = []

        for key in keys:
            data = all_metrics[key]
            filename = '.'.join(data['name'].split('.')[1:])
            days = data['days']
            hours = data['hours']
            minutes = data['minutes']

            lines.append("{0} {1} {2} {3}".format(
                filename, days, hours, minutes))

        # Clear contents of fileage.txt file
        open(fileage_file, 'w').close()

        with open(fileage_file, 'a', newline='\n') as f:
            for line in lines:
                f.write("{0}\n".format(line))

    elif client in ("Python", "Python3"):
        fileage_dir = "{0}/{1}/NodePing{1}PUSH/metrics/fileage".format(
            archive_dir, client)
        fileage_file = join(fileage_dir, "config.py")

        files = {}

        for key in keys:
            data = all_metrics[key]
            filename = '.'.join(data['name'].split('.')[1:])
            days = data['days']
            hours = data['hours']
            minutes = data['minutes']
            files.update(
                {filename: {"days": days, "hours": hours, "minutes": minutes}})

        # Clear contents of the config.py file
        open(fileage_file, 'w').close()

        with open(fileage_file, 'a', newline='\n') as f:
            f.write("filenames = ")
            pprint(files, stream=f)

    elif client == 'PowerShell':
        fileage_dir = "{0}/{1}/NodePing{1}PUSH/modules/fileage".format(
            archive_dir, client)

        fileage_file = join(fileage_dir, "fileage.json")

        files = []

        # Clear contents of the fileage.json file
        open(fileage_file, 'w').close()

        for key in keys:
            data = all_metrics[key]
            filename = '.'.join(data['name'].split('.')[1:])
            days = data['days']
            hours = data['hours']
            minutes = data['minutes']

            data = {"FileName": filename, "Age": {
                "days": days, "hours": hours, "minutes": minutes}}

            files.append(data)

        with open(fileage_file, 'w') as f:
            f.write(json.dumps(files, indent=8, sort_keys=True))
