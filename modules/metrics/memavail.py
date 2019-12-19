#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyInquirer import prompt


def memavail_metric(key_name):
    """
    """

    # Min/max are output in an opposite day sort of fashion due to free memory space being sort of opposite
    questions = [
        {
            'type': 'input',
            'name': 'min',
            'message': 'What is the max memory available you want it to reach (E.g 350)?',
        },
        {
            'type': 'input',
            'name': 'max',
            'message': 'What is the minimum memory available you want it to reach (E.g 8192)?',
        }
    ]

    answers = prompt(questions)

    _min = int(answers['min'])
    _max = int(answers['max'])

    name = "{0}".format(key_name)

    return {name: {'name': name, 'min': _min, 'max': _max}}
