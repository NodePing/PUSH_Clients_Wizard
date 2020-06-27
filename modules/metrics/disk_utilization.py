#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyInquirer import prompt


def disk_utilization_metric(key_name):
    """ Get The disk names to monitor as well as min/max disk usage
    """

    get_drives = True
    drives = {}
    i = 1

    while get_drives:

        questions = [
            {
                "type": "input",
                "name": "name",
                "message": "Pick the drive letter or dev you want to monitor",
            },
            {
                "type": "input",
                "name": "min",
                "message": "Max disk free space percentage (E.g 20 for 20%)?",
            },
            {
                "type": "input",
                "name": "max",
                "message": "Min disk free space percentage (E.g 80 for 80%)?",
            },
            {
                "type": "confirm",
                "name": "get_another",
                "message": "Add another to the check?",
            },
        ]

        answers = prompt(questions)

        minimum = int(answers["min"])
        maximum = int(answers["max"])

        name = "{0}.{1}".format(key_name, answers["name"]).strip(":")
        key = "{0}{1}".format(key_name, i)

        drives.update({key: {"name": name, "min": minimum, "max": maximum}})

        if answers["get_another"]:
            i += 1
        else:
            break

    return drives
