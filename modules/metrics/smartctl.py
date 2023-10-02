#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join
from InquirerPy import prompt
from modules import _utils


def smartctl_metric(key_name):
    """
    """

    devices = []

    adding_drives = True

    while adding_drives:
        questions = [
            {
                'type': 'input',
                'name': 'drive',
                'message': 'Device you want to check SMART data on (eg /dev/sda):'
            },
            {
                'type': 'confirm',
                'name': 'adding_drives',
                'message': 'Add another drive?'
            }
        ]

        check_answers = prompt(questions)

        devices.append(check_answers['drive'])
        adding_drives = check_answers['adding_drives']

    device_fields = {}
    i = 1

    for drive in devices:
        name = "{0}.{1}".format(key_name, drive)
        key = "{0}{1}".format(key_name, drive)

        device_fields.update(
            {key: {'name': name, 'min': 1, 'max': 1}})

    return device_fields


def configure_smartctl(keys, all_metrics, archive_dir, client):
    """
    """

    _utils.seperator()
    print("\n=====Configuring the smartctl metric=====")

    devices = []

    for key in keys:
        data = all_metrics[key]
        dev = '.'.join(data['name'].split('.')[1:])

        devices.append(dev)

    if client == "POSIX":
        smartctl_dir = "{0}/POSIX/NodePingPUSHClient/modules/smartctl".format(
            archive_dir)
        smartctl_file = join(smartctl_dir, "smartdrives.sh")

        devices = ' '.join(devices)

        with open(smartctl_file, 'w', newline='\n') as f:
            f.write("devices=\"%s\"\n" % devices)
