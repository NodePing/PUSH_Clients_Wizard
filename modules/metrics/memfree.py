#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from InquirerPy import prompt


def memory_metric(key_name):
    """ Set the minimum and maximum amount of free memory available on a system
    """

    # Min/max are output in an opposite day sort of fashion due to
    # free memory space being sort of opposite

    questions = [
        {
            'type': 'input',
            'name': 'min',
            'message': 'What is the max memory free you want it to reach (E.g 350)?',
        },
        {
            'type': 'input',
            'name': 'max',
            'message': 'What is the minimum memory free you want it to reach (E.g 8192)?',
        }
    ]

    answers = prompt(questions)

    _min = int(answers['min'])
    _max = int(answers['max'])

    return {key_name: {'name': key_name, 'min': _min, 'max': _max}}
