#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from InquirerPy import prompt


def cpu_utilization_metric(key_name):
    """ Get minimum and maximum CPU load % to specify pass/fail range
    """

    questions = [
        {
            "type": "input",
            "name": "minimum",
            "message": "What minimum CPU utilization % do you want to be notified at?",
        },
        {
            "type": "input",
            "name": "maximum",
            "message": "What maximum CPU utilization % do you want to be notified at?",
        },
    ]

    answers = prompt(questions)

    minimum = answers["minimum"]
    maximum = answers["maximum"]

    return {key_name: {"name": key_name, "min": minimum, "max": maximum}}
