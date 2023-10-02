#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from InquirerPy import prompt


def checkiptables_metric(key_name):
    """
    """

    check_questions = [
        {
            'type': 'input',
            'name': 'ip4_count',
            'message': 'Expected IPv4 rule count:'
        },
        {
            'type': 'input',
            'name': 'ip6_count',
            'message': 'Expected IPv6 rule count:'
        }
    ]

    check_answers = prompt(check_questions)

    ip4 = check_answers['ip4_count']
    ip6 = check_answers['ip6_count']

    metrics = {
        "{0}_ipv4".format(key_name): {
            'name': "{0}.ipv4".format(key_name),
            'min': ip4,
            'max': ip4
        },
        "{0}_ipv6".format(key_name): {
            'name': "{0}.ipv6".format(key_name),
            'min': ip6,
            'max': ip6
        }

    }

    return metrics
