#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import sys
import os.path
from os.path import abspath, dirname, isfile, join
from PyInquirer import prompt
from nodeping_api import delete_checks, get_checks, create_check
from . import configure_metrics, configure_client, configure_contacts, _utils, _variables

CLIENTS_URL = 'https://github.com/NodePing/PUSH_Clients/archive/master.zip'
FILENAME = 'master.zip'
PATH = abspath(join(dirname(__file__), os.pardir))
CLIENT_ZIP = join(PATH, FILENAME)


def _strip_extra_data(fields):
    """ Strips extra data from the check data being sent to NodePing

    Some data doesn't need to be sent, This function will remove those fields.
    Namely, the checksums and maximum file ages
    """

    new_fields = {}

    keys = [key for key in fields if 'checksum' in key or 'fileage' in key]

    for key, value in fields.items():
        if key not in keys:
            new_fields.update({key: value})
            continue

    for key in keys:
        data = fields[key]

        if 'checksum' in key:
            data.pop('checksum')
            data.pop('hash_algorithm')
        elif 'fileage' in key:
            data.pop('days')
            data.pop('hours')
            data.pop('minutes')

        new_fields.update({key: data})

    return new_fields


def _fetch_checks(token):
    """ Fetches all NodePing checks of type PUSH

    Fetches all NodePing checks for the account and returns only the
    checks that are of type PUSH
    """

    push_checks = {}

    query_nodeping = get_checks.GetChecks(token)
    checks = query_nodeping.all_checks()

    for key, value in checks.items():
        _type = value['type']

        if _type == 'PUSH':
            push_checks.update({key: value})

    return push_checks


def list_checks(token):
    """ List PUSH checks that are fetched with _fetch_checks

    Asks the user if they want to print all PUSH checks in a
    user-readable format. Also asks if the user wants to print
    one-by-one or stop printing.
    """

    push_checks = _fetch_checks(token)

    next = ""

    print("\n")

    message = 'Print all checks?'
    printall = _utils.inquirer_confirm(message, default=False)

    if printall:
        next = 'A'

    # Prints each check in a user-readable format
    for key, contents in push_checks.items():
        try:
            label = contents['label']
        except KeyError:
            label = "(none)"
        _utils.seperator()
        print("Label: %s" % label)
        print("ID: %s" % contents['_id'])
        print("Checktoken: %s" % contents['parameters']['checktoken'])

        # If the check hasn't had a PASS/FAIL status, a - is put in its place
        try:
            if contents['state'] == 1:
                print("Status: PASS")
            else:
                print("Status: FAIL")
        except KeyError:
            print("Status: -")

        if contents['enable'] == 'active':
            print("Enabled: Yes")
        else:
            print("Enabled: No")

        print("Interval: %s\n" % contents['interval'])

        if next != 'A':
            next = input("Enter for next, (a)ll checks or (s)top ").upper()
        if next == 'S':
            break

    _utils.seperator()


def configure(token):
    """ Configures the check for NodePing and optionally the client
    """

    _utils.seperator()

    # Ask user what their client type is
    client_question = [
        {
            'type': 'list',
            'name': 'client_type',
            'message': 'What client will be used for this check',
            'choices': ['POSIX', 'PowerShell', 'Python', 'Python3']
        }
    ]

    client = prompt(client_question)
    client = client['client_type']

    # Gets the metrics list based on what the client is written in
    if client == "POSIX":
        metrics = _variables.posix_metrics
    elif client == "PowerShell":
        metrics = _variables.powershell_metrics
    elif client == "Python" or client == "Python3":
        metrics = _variables.python_metrics

    metrics_list = _utils.list_to_dicts(metrics, 'name')

    # Asks user if they want to download the client
    questions = [
        {
            'type': 'confirm',
            'name': 'get_clients',
            'message': 'Do you want to download a copy of the client?',
            'default': False
        }
    ]

    answers = prompt(questions)

    get_clients = answers['get_clients']

    # Fetches the master.zip from CLIENTS_URL
    if get_clients:
        # Asks user if they want to download the zip file again if it exists
        if isfile(CLIENT_ZIP):
            message = 'Client exists. Download again?'
            get_again = _utils.inquirer_confirm(message)

            if get_again:
                downloaded = _utils.download_file(CLIENTS_URL, CLIENT_ZIP)
            else:
                # Set to true because the file already exists
                downloaded = True
        else:
            downloaded = _utils.download_file(CLIENTS_URL, CLIENT_ZIP)
            print("File downloaded")

        if not downloaded:
            print("File not downloaded. Setting up without the client")

    # Template of questions to ask user
    check_questions = [
        {
            'type': 'input',
            'name': 'label',
            'message': 'Name/label for check'
        },
        {
            'type': 'list',
            'name': 'interval',
            'message': 'Check interval frequency',
            'choices': [
                '1 minute',
                '3 minutes',
                '5 minutes',
                '15 minutes',
                '1 hour',
                '4 hours',
                '6 hours',
                '12 hours',
                '1 day'
            ]
        },
        {
            'type': 'confirm',
            'name': 'enabled',
            'message': 'Enable the check',
            'default': False
        },
        {
            'type': 'confirm',
            'name': 'public',
            'message': 'Make the check public',
            'default': False
        },
        {
            'type': 'checkbox',
            'name': 'enabled_checks',
            'message': 'Which checks will be enabled',
            'choices': metrics_list
        }
    ]

    check_answers = _utils.confirm_choice(check_questions)

    message = "Preparing to configure metrics. Do you also wish to setup the client"

    # setup_client = _utils.ask_yes_no(message)
    setup_client = _utils.inquirer_confirm(message)

    # Configures fields for new PUSH check
    fields = configure_metrics.main(check_answers['enabled_checks'], client)

    _utils.seperator()
    print("Configuring contacts for check\n")
    contacts = configure_contacts.main(token)
    _utils.seperator()

    # Removes some data before sending such as checksums and fileage so that
    # info doesn't go over the internet
    send_fields = copy.deepcopy(fields)
    send_fields = _strip_extra_data(send_fields)

    check_results = create_check.push_check(
        token,
        label=check_answers['label'],
        fields=send_fields,
        enabled=check_answers['enabled'],
        interval=check_answers['interval'],
        notifications=contacts
    )

    # Add checktoken to fields
    fields.update({'checktoken': check_results['parameters']['checktoken']})
    # Add check ID to fileds
    fields.update({'check_id': check_results['_id']})

    if setup_client:
        configure_client.main(fields, CLIENT_ZIP, client)

    return check_results


def delete(token):
    """
    """

    checks = _fetch_checks(token)

    checks_list = []

    for key, value in checks.items():
        try:
            label = value['label']
        except KeyError:
            label = '(No Label)'

        checktoken = value['parameters']['checktoken']

        checks_list.append("%s - %s" % (label, checktoken))

    checks_dict = _utils.list_to_dicts(checks_list, 'name')

    questions = [
        {
            'type': 'checkbox',
            'name': 'remove_checks',
            'message': 'Which checks do you want to delete',
            'choices': checks_dict
        }
    ]

    answers = prompt(questions)

    _utils.seperator()

    for item in answers['remove_checks']:
        print(item)

    _utils.seperator()

    message = "Are you sure you want to remove the selected checks"

    # confirm = _utils.ask_yes_no(message)
    confirm = _utils.inquirer_confirm(message, default=False)

    if confirm:
        for key, value in checks.items():
            checktoken = value['parameters']['checktoken']

            for to_remove in answers['remove_checks']:
                if checktoken in to_remove:
                    checkid = value['_id']
                    delete_checks.remove(token, checkid)

                    print("Deleted %s" % to_remove)

    _utils.seperator()
    print("Done!\n")
