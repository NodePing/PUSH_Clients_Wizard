#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyInquirer import prompt


def _get_disk_quotas(key_name, message):
    """ Collects drive names/mountpoints and a min/max capacity
    """

    get_names = True
    names = {}
    i = 1

    while get_names:

        # Min/max are output in an opposite day sort of fashion due to
        # free disk space being sort of opposite
        questions = [
            {
                'type': 'input',
                'name': 'name',
                'message': message
            },
            {
                'type': 'input',
                'name': 'min',
                'message': 'Max disk free space percentage (E.g 20 for 20%)?',
            },
            {
                'type': 'input',
                'name': 'max',
                'message': 'Min disk free space percentage (E.g 80 for 80%)?',
            },
            {
                'type': 'confirm',
                'name': 'get_another',
                'message': 'Add another to the check?'
            }
        ]

        answers = prompt(questions)

        _min = int(answers['min']) / 100
        _max = int(answers['max']) / 100

        name = "{0}.{1}".format(key_name, answers['name'])
        key = "{0}{1}".format(key_name, i)

        names.update({key: {'name': name, 'min': _min, 'max': _max}})

        if answers['get_another']:
            i += 1
        else:
            break

    return names


def drives_metric(key_name):
    """ Collects drive names/mountpoints and a min/max capacity
    """

    message = "What is the drive name/mount point?"

    return _get_disk_quotas(key_name, message)


def zfs_metric(key_name):
    """ Set min/max values on free space for zfs datasets
    """

    message = "Which ZFS dataset do you want to monitor?"

    return _get_disk_quotas(key_name, message)
