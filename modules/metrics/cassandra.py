#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyInquirer import prompt


def cassandra_metric(key_name):
    """ Sets Cassandra metric to monitor Cassandra cluster

    Asks user for IPs of Cassandra databases to monitor
    """

    cassandra_ips = []

    adding_ips = True

    while adding_ips:
        check_questions = [
            {
                'type': 'input',
                'name': 'ip',
                'message': 'Cassandra IP address'
            },
            {
                'type': 'confirm',
                'name': 'adding_ips',
                'message': 'Add another IP address'
            }
        ]

        check_answers = prompt(check_questions)

        cassandra_ips.append(check_answers['ip'])
        adding_ips = check_answers['adding_ips']

    cassandra_fields = {}
    i = 1

    for ip in cassandra_ips:
        name = "{0}.{1}".format(key_name, ip)
        key = "{0}{1}".format(key_name, i)
        i += 1

        cassandra_fields.update(
            {key: {'name': name, 'min': 1, 'max': 1}})

    return cassandra_fields
