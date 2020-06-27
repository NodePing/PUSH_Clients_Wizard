#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyInquirer import prompt


def ram_utilization_metric(key_name):
    """ Get memory usage % to specify pass/fail range
    """

    questions = [
        {
            "type": "input",
            "name": "minimum",
            "message": "What is the minimum memory usage % you want to be alerted at?",
        },
        {
            "type": "input",
            "name": "maximum",
            "message": "What is the maximum memory usage % you want to be alerted at?",
        },
    ]

    answers = prompt(questions)

    minimum = answers["minimum"]
    maximum = answers["maximum"]

    return {key_name: {"name": key_name, "min": minimum, "max": maximum}}
