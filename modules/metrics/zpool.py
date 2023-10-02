#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join
from InquirerPy import prompt
from modules import _utils


def zpool_metric(key_name):
    """
    """

    zpools = []
    adding_zpools = True

    while adding_zpools:
        check_questions = [
            {
                'type': 'input',
                'name': 'zpool',
                'message': 'Name of zpool you want to monitor:'
            },
            {
                'type': 'confirm',
                'name': 'adding_zpools',
                'message': 'Add another pool'
            }
        ]

        check_answers = prompt(check_questions)

        zpools.append(check_answers['zpool'])
        adding_zpools = check_answers['adding_zpools']

    zpool_fields = {}
    i = 1

    for zpool in zpools:
        name = "{0}.{1}".format(key_name, zpool)
        key = "{0}{1}".format(key_name, i)
        i += 1

        zpool_fields.update(
            {key: {'name': name, 'min': 1, 'max': 1}})

    return zpool_fields


def configure_zpool(keys, all_metrics, archive_dir, client):
    """
    """

    _utils.seperator()
    print("\n=====Configuring the zpool metric=====")

    zpools = []

    for key in keys:
        data = all_metrics[key]
        zpool = '.'.join(data['name'].split('.')[1:])

        zpools.append(zpool)

    if client == 'POSIX':
        zpool_dir = "{0}/POSIX/NodePingPUSHClient/modules/zpool".format(
            archive_dir)
        zpools_file = join(zpool_dir, "pools.sh")

        zpools = ' '.join(zpools)

        with open(zpools_file, 'w', newline='\n') as f:
            f.write("pools=\"%s\"\n" % zpools)
