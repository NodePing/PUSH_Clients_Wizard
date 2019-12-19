#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join
from PyInquirer import prompt
from modules import _utils


def pingstatus_metric(key_name):
    """ Sets pingstatus IP addresses and whether they should be pass or fail
    """

    get_hosts = True
    hosts = {}
    i = 1

    while get_hosts:
        questions = [
            {
                'type': 'input',
                'name': 'host',
                'message': 'What is the fqdn or IP of the host you want to ping?'
            },
            {
                'type': 'confirm',
                'name': 'online',
                'message': 'Do you expect this address to be pingable?'
            },
            {
                'type': 'confirm',
                'name': 'get_another',
                'message': 'Do you wish to add another host to ping?'
            }
        ]

        answers = prompt(questions)

        name = "{0}.{1}".format(key_name, answers['host'])
        key = "{0}{1}".format(key_name, i)

        if answers['online']:
            pingable = 1
        else:
            pingable = 0

        hosts.update(
            {key: {'name': name, 'min': pingable, 'max': pingable}})

        if not answers['get_another']:
            break

        i += 1

    return hosts


def configure_pingstatus(keys, all_metrics, archive_dir, client):
    """ Puts the pingstatus metric info in its necessary config file

    Uses the data gathered from configure_metrics.py to insert the hosts
    to ping. This function also prompts the user for the timeout time and
    number of pings to send per host.
    """

    _utils.seperator()
    print("\n=====Configuring the pingstatus metric=====")

    hosts = []

    for key in keys:
        data = all_metrics[key]
        host = '.'.join(data['name'].split('.')[1:])

        hosts.append(host)

    questions = [
        {
            'type': 'input',
            'name': 'ping_count',
            'message': 'How many times do you want to ping each host'
        },
        {
            'type': 'input',
            'name': 'timeout',
            'message': 'How many seconds to wait before timing out'
        }
    ]

    answers = _utils.confirm_choice(questions)

    ping_count = answers['ping_count']
    timeout = answers['timeout']

    if client == "POSIX":
        pingstatus_dir = "{0}/POSIX/NodePingPUSHClient/modules/pingstatus".format(
            archive_dir)
        pingstatus_file = join(pingstatus_dir, "variables.sh")

        hosts = ' '.join(hosts)

        with open(pingstatus_file, 'w', newline='\n') as f:
            f.write("ping_hosts=\"%s\"\n" % hosts)
            f.write("ping_count=%s\n" % ping_count)
            f.write("timeout=%s\n" % timeout)

    elif client in ("Python", "Python3"):
        pingstatus_dir = "{0}/{1}/NodePing{1}PUSH/metrics/pingstatus".format(
            archive_dir, client)

        pingstatus_file = join(pingstatus_dir, "config.py")

        with open(pingstatus_file, 'w', newline='\n') as f:
            f.write("ping_hosts = %s\n" % str(hosts))
            f.write("ping_count = \"%s\"\n" % ping_count)
            f.write("timeout = \"%s\"\n" % timeout)
