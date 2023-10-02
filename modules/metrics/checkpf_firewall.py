#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from InquirerPy import prompt


def checkpf_firewall_metric(key_name):
    """
    """

    check_questions = [
        {
            'type': 'input',
            'name': 'count',
            'message': 'Expected rule count:'
        }
    ]

    check_answers = prompt(check_questions)

    count = check_answers['count']

    metrics = {
        key_name: {
            'name': key_name,
            'min': count,
            'max': count
        }
    }

    return metrics
