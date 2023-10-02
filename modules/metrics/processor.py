#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from InquirerPy import prompt


def processor_metric(key_name, client):
    """ Set the minimum and maximum load averages expected for a system
    """

    if client == 'POSIX':
        questions = [
            {
                'type': 'input',
                'name': '1min_min',
                'message': "What's the 1 minute load min (Blank if ignoring)?",
            },
            {
                'type': 'input',
                'name': '1min_max',
                'message': "What's the 1 minute load max (Blank if ignoring)?",
            },
            {
                'type': 'input',
                'name': '5min_min',
                'message': "What's the 5 minute load min (Blank if ignoring)?",
            },
            {
                'type': 'input',
                'name': '5min_max',
                'message': "What's the 5 minute load max (Blank if ignoring)?",
            },
            {
                'type': 'input',
                'name': '15min_min',
                'message': "What's the 15 minute load min (Blank if ignoring)?",
            },
            {
                'type': 'input',
                'name': '15min_max',
                'message': "What's the 15 minute load max (Blank if ignoring)?",
            }
        ]
    elif client == 'PowerShell':
        questions = [
            {
                'type': 'input',
                'name': 'cpumin',
                'message': "What's the min CPU load (load average) you expect?",
            },
            {
                'type': 'input',
                'name': 'cpumax',
                'message': "What's the max CPU load (or load average) you expect?",
            }
        ]
    else:
        questions = [
            {
                'type': 'confirm',
                'name': 'is_windows',
                'message': 'Are you getting load metrics for Windows?',
                'default': False,
            },
            {
                'type': 'input',
                'name': 'cpumin',
                'message': "What's the min CPU load (load average) you expect?",
                'when': lambda answers: answers['is_windows']
            },
            {
                'type': 'input',
                'name': 'cpumax',
                'message': "What's the max CPU load (or load average) you expect?",
                'when': lambda answers: answers['is_windows']
            },
            {
                'type': 'input',
                'name': '1min_min',
                'message': "What's the 1 minute load min (Blank if ignoring)?",
                'when': lambda answers: not answers['is_windows']
            },
            {
                'type': 'input',
                'name': '1min_max',
                'message': "What's the 1 minute load max (Blank if ignoring)?",
                'when': lambda answers: not answers['is_windows']
            },
            {
                'type': 'input',
                'name': '5min_min',
                'message': "What's the 5 minute load min (Blank if ignoring)?",
                'when': lambda answers: not answers['is_windows']
            },
            {
                'type': 'input',
                'name': '5min_max',
                'message': "What's the 5 minute load max (Blank if ignoring)?",
                'when': lambda answers: not answers['is_windows']
            },
            {
                'type': 'input',
                'name': '15min_min',
                'message': "What's the 15 minute load min (Blank if ignoring)?",
                'when': lambda answers: not answers['is_windows']
            },
            {
                'type': 'input',
                'name': '15min_max',
                'message': "What's the 15 minute load max (Blank if ignoring)?",
                'when': lambda answers: not answers['is_windows']
            }
        ]

    answers = prompt(questions)

    if client in ("Python", "Python3"):
        if answers['is_windows']:
            if not answers['cpumin']:
                _min = 0
            else:
                _min = int(answers['cpumin']) / 100

            _max = int(answers['cpumax']) / 100

            return {key_name: {'name': 'load.usage', 'min': _min, 'max': _max}}
    elif client == 'PowerShell':
        if not answers['cpumin']:
            _min = 0
        else:
            _min = int(answers['cpumin']) / 100

        _max = int(answers['cpumax']) / 100

        return {key_name: {'name': 'cpuload', 'min': _min, 'max': _max}}

    loads = {}

    if answers['1min_max'] != '':
        key = "{0}{1}".format(key_name, "1min")
        name = "{0}.{1}".format(key_name, "1min")

        if not answers['1min_min']:
            _min = 0
        else:
            _min = answers['1min_min']
        loads.update(
            {key: {'name': name, 'min': _min, 'max': answers['1min_max']}})

    if answers['5min_max'] != '':
        key = "{0}{1}".format(key_name, "5min")
        name = "{0}.{1}".format(key_name, "5min")

        if not answers['5min_min']:
            _min = 0
        else:
            _min = answers['5min_min']
        loads.update(
            {key: {'name': name, 'min': _min, 'max': answers['5min_max']}})

    if answers['15min_max'] != '':
        key = "{0}{1}".format(key_name, "15min")
        name = "{0}.{1}".format(key_name, "15min")

        if not answers['15min_min']:
            _min = 0
        else:
            _min = answers['15min_min']

        loads.update(
            {key: {'name': name, 'min': _min, 'max': answers['15min_max']}})

    return loads
