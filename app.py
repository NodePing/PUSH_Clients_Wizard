#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from os.path import dirname, expanduser, join, realpath
from sys import exit
from modules import _utils, manage_checks
from pprint import pprint
from InquirerPy import prompt


CONFIGFILE = join(dirname(realpath(expanduser(__file__))), "config.ini")


def created_check(info):
    """ Print out the information of the check that was just created
    """

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

    # Print out the required info for Windows PowerShell
    if job and "Set-ScheduledTask" in job:
        print("\nRun these commands in your Windows PowerShell as the administrator:\n")
        print("{0}\n".format(job))
        print("Or run the created windows_task.ps1 PowerShell script as administrator\n\n")
    # Print out a cron job for everything else
    elif job:
        print("\nEnter this cron line to run the client at your specified interval:\n")
        print("{0}\n".format(job))

    input("\nPress enter to continue")


def main():
    """ Prompt the user for which action they want to take

    List, create, delete checks s well as set the user token and/or customerid
    if desired.
    """

    config = configparser.ConfigParser()
    config.read(CONFIGFILE)

    token, customerid = _utils.get_user_token(config, CONFIGFILE)

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

        if answers['user_choice'] == "List PUSH checks":
            manage_checks.list_checks(token, customerid)

        elif answers['user_choice'] == "Create a PUSH check":
            check_info = manage_checks.configure(token, customerid)
            created_check(check_info)

        elif answers['user_choice'] == "Delete PUSH checks":
            manage_checks.delete(token, customerid)
        elif answers['user_choice'] == "Exit":
            print("Bye")
            exit(0)


if __name__ == '__main__':
    main()
