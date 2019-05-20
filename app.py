#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from os.path import dirname, expanduser, join, realpath
from sys import exit
from modules import _utils, manage_checks
from pprint import pprint
from PyInquirer import prompt


CONFIGFILE = join(dirname(realpath(expanduser(__file__))), "config.ini")


def created_check(info):
    try:
        label = info['label']
    except KeyError:
        label = '-'

    _id = info['_id']
    checktoken = info['parameters']['checktoken']
    enabled = info['enable']
    interval = info['interval']
    public = info['public']
    oldresultfail = info['parameters']['oldresultfail']
    fields = info['parameters']['fields']

    try:
        job = info['scheduled_job']
    except KeyError:
        job = False

    output = "Complete!\n\nLabel: {0}\n_id: {1}\nchecktoken: {2}\nEnabled: {3}\nInterval: {4}\nPublic: {5}\nFail when resultsare old: {6}\nFields:".format(
        label, _id, checktoken, enabled, interval, public, oldresultfail)

    print(output)
    pprint(fields)

    if job and "schtasks" in job:
        print("\nRun this command in your Windows PowerShell:\n")
        print("{0}\n".format(job))
    elif job:
        print("\nEnter this cron line to run the client at your specified interval:\n")
        print("{0}\n".format(job))

    input("\nPress enter to continue")


def main():

    config = configparser.ConfigParser()
    config.read(CONFIGFILE)

    token = _utils.get_user_token(config, CONFIGFILE)

    interaction = True

    while interaction:
        print("##########################")
        print("\nNodePing PUSH Check Wizard\n")
        print("##########################\n")

        get_started = [
            {
                'type': 'list',
                'name': 'user_choice',
                'message': 'Please select an action',
                'choices': [
                    'List PUSH checks',
                    'Create a PUSH check',
                    'Delete PUSH checks',
                    'Exit'
                ]
            }
        ]

        answers = prompt(get_started)

        if answers['user_choice'].startswith("L"):
            manage_checks.list_checks(token)

        elif answers['user_choice'].startswith("C"):
            check_info = manage_checks.configure(token)
            created_check(check_info)

        elif answers['user_choice'].startswith("D"):
            manage_checks.delete(token)
        elif answers['user_choice'].startswith("E"):
            print("Bye")
            exit(0)


if __name__ == '__main__':
    main()
