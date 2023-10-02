#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from os.path import join
from InquirerPy import prompt
from modules import _utils


def ip_addrs_metric():
    """
    """

    ip_fields = {
        'ip_addrs': {
            'name': 'ip_addrs',
            'min': 1,
            'max': 1
        }
    }

    return ip_fields


def configure_ip_addrs(archive_dir, client):
    """ Sets up the client configuration for ip_addrs metric

    Asks the user for IP addresses that they except to be on their system.
    If any other IP appears, they will be alerted.
    """

    _utils.seperator()
    print("\n=====Configuring the ip_addrs metric=====")

    VAR_NAME = 'acceptable_ips'

    host_ips = []

    adding_ips = True
    complete = False

    while not complete:
        while adding_ips:
            check_questions = [
                {
                    'type': 'input',
                    'name': 'ip',
                    'message': 'Allowed IP address'
                },
                {
                    'type': 'confirm',
                    'name': 'adding_ips',
                    'message': 'Add another IP address'
                }
            ]

            check_answers = prompt(check_questions)

            host_ips.append(check_answers['ip'])
            adding_ips = check_answers['adding_ips']

        print(str(host_ips))

        complete = _utils.inquirer_confirm("Are these IP addresses correct?")

    if client == 'POSIX':
        ip_addrs_dir = "{0}/POSIX/NodePingPUSHClient/modules/ip_addrs".format(
            archive_dir)
        vars_file = join(ip_addrs_dir, "variables.sh")

        ips = ' '.join(host_ips)

        with open(vars_file, 'w', newline='\n') as f:
            f.write("{0}='{1}'\n".format(VAR_NAME, ips))
    elif client in ("Python", "Python3"):
        ip_addrs_dir = "{0}/{1}/NodePing{1}PUSH/metrics/ip_addrs".format(
            archive_dir, client)

        ip_addrs_file = join(ip_addrs_dir, "config.py")

        with open(ip_addrs_file, 'r', newline='\n') as f:
            filedata = f.read()

        filedata = filedata.replace('acceptable_addrs = ["192.168.0.16"]',
                                    'acceptable_addrs = %s' % host_ips)

        with open(ip_addrs_file, 'w', newline='\n') as f:
            f.write(filedata)
    elif client == 'PowerShell':
        ip_addrs_dir = "{0}/{1}/NodePing{1}PUSH/modules/ip_addrs".format(
            archive_dir, client)

        ip_addrs_file = join(ip_addrs_dir, "ip_addrs.json")

        # Clear contents of the ip_addrs.json file
        open(ip_addrs_file, 'w').close()

        with open(ip_addrs_file, 'w') as f:
            f.write(json.dumps(host_ips, indent=8, sort_keys=True))
