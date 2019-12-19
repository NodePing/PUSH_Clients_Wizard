#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import sys
import os.path
import urllib.error
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


def _fetch_checks(token, customerid=None):
    """ Fetches all NodePing checks of type PUSH

    Fetches all NodePing checks for the account and returns only the
    checks that are of type PUSH
    """

    query_nodeping = get_checks.GetChecks(token, customerid=customerid)
    checks = query_nodeping.all_checks()

    return {key: value for key, value in checks.items() if value['type'] == "PUSH"}


def list_checks(token, customerid=None):
    """ List fetched PUSH checks

    Asks the user if they want to print all PUSH checks in a
    user-readable format. Also asks if the user wants to print
    one-by-one or stop printing.
    """

    if customerid:
        subacount_msg = "Do you want to list checks from your subaccount?"
        use_subaccount = _utils.inquirer_confirm(subacount_msg, default=False)

        if not use_subaccount:
            customerid = None

    push_checks = _fetch_checks(token, customerid)

    if not push_checks:
        print("\nNo push checks created for this account account")
        return

    message = 'Print all PUSH checks at once?'
    printall = _utils.inquirer_confirm(message, default=False)

    if printall:
        next_check = 'A'
    else:
        next_check = None

    # Prints each check in a user-readable format
    for _key, contents in push_checks.items():

        # If no label, substitute for placeholder
        try:
            label = contents['label']
        except KeyError:
            label = "(none)"

        # If no oldresultfail, it is False
        try:
            oldresultfail = str(contents['parameters']['oldresultfail'])
        except KeyError:
            oldresultfail = False

        _utils.seperator()
        print("Label: %s" % label)
        print("ID: %s" % contents['_id'])
        print("Checktoken: %s" % contents['parameters']['checktoken'])
        print("Fail when results are old: %s" % oldresultfail)

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

        if next_check != 'A':
            next_check = input(
                "Enter for next, (a)ll checks or (s)top ").upper()
        if next_check == 'S':
            break

    _utils.seperator()


def configure(token, customerid=None):
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
    elif client in ("Python", "Python3"):
        metrics = _variables.python_metrics

    metrics_list = _utils.list_to_dicts(metrics, 'name')

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
            'message': 'Make the check reports public',
            'default': False
        },
        {
            'type': 'confirm',
            'name': 'oldresultfail',
            'message': 'Fail the check when results are old? (heartbeat monitoring)',
            'default': False,
        },
        {
            'type': 'input',
            'name': 'sens',
            'message': 'How many intervals before results are considered \'old\'?',
            'validate': _utils.IntValidator,
            'when': lambda check_answers: check_answers['oldresultfail']
        },
        {
            'type': 'checkbox',
            'name': 'enabled_checks',
            'message': 'Select metrics to be enabled',
            'choices': metrics_list
        }
    ]

    check_answers = _utils.confirm_choice(check_questions)

    # Configures fields for new PUSH check
    fields = configure_metrics.main(check_answers['enabled_checks'], client)

    # Asks user if they want to create the check for their subaccount or main
    if customerid:
        subacount_msg = "Do you want to create your check with your subaccount?"
        use_subaccount = _utils.inquirer_confirm(subacount_msg, default=False)

        if not use_subaccount:
            customerid = None

    _utils.seperator()
    print("Configuring contacts for check\n")
    contacts = configure_contacts.main(token, customerid=customerid)
    _utils.seperator()

    # Removes some data before sending such as checksums and fileage so that
    # info doesn't go over the internet
    send_fields = copy.deepcopy(fields)
    send_fields = _strip_extra_data(send_fields)

    interval = _utils.get_interval(check_answers['interval'])

    label = check_answers['label']

    # Checks if sens was configured. If not configured, the value is set to 2
    try:
        sens = check_answers['sens']
    except KeyError:
        sens = 2

    check_results = create_check.push_check(
        token,
        label=label,
        customerid=customerid,
        fields=send_fields,
        oldresultfail=check_answers['oldresultfail'],
        sens=sens,
        public=check_answers['public'],
        enabled=check_answers['enabled'],
        interval=interval,
        notifications=contacts
    )

    # Add checktoken to fields
    try:
        fields.update(
            {'checktoken': check_results['parameters']['checktoken']})
    # If a checktoken doesn't exist, then querying NodePing failed
    except KeyError:
        print("Unable to connect to NodePing API. Exiting")
        sys.exit(2)

    # Add check ID to fileds
    fields.update({'check_id': check_results['_id']})

    message = "Check successfully created in NodePing. Do you also wish to setup and deploy the client?"

    setup_client = _utils.inquirer_confirm(message)

    if setup_client:
        # Asks user if they want to download the zip file again if it exists
        if isfile(CLIENT_ZIP):
            message = 'Client exists. Do you want to download a fresh copy?'
            get_again = _utils.inquirer_confirm(message)

            if get_again:
                _utils.download_file(CLIENTS_URL, CLIENT_ZIP)
        else:
            _utils.download_file(CLIENTS_URL, CLIENT_ZIP)
            print("File downloaded")

        # Configures the client
        # Returns the path to where the client was stored and os
        remote_data = configure_client.main(fields, CLIENT_ZIP, client)

        remote_dir = remote_data['dest']
        os = remote_data['os']
        user = remote_data['user']

        # Create cron job or windows scheduled task based on target OS
        if os == 'Windows':
            scheduled_job = _utils.create_win_schedule(
                user, remote_dir, client, interval, label)
        else:
            scheduled_job = _utils.create_cron(
                remote_dir, client, interval, label)

        check_results.update({'scheduled_job': scheduled_job})

    return check_results


def delete(token, customerid=None):
    """ Get a list of existing PUSH checks and let the user select and delete

    Lists the existing PUSH checks on the user's account. The user checks the
    checkboxes of checks they want to delete, then NodePing is queried and
    requested to delete the selected checks
    """

    if customerid:
        subacount_msg = "Do you want to delete checks from your subaccount?"
        use_subaccount = _utils.inquirer_confirm(subacount_msg, default=False)

        if not use_subaccount:
            customerid = None

    # Fetches existing PUSH checks
    checks = _fetch_checks(token, customerid=customerid)

    checks_list = []

    for _key, value in checks.items():

        # If no label exists, set label to (No Label)
        try:
            label = value['label']
        except KeyError:
            label = '(No Label)'

        checktoken = value['parameters']['checktoken']

        checks_list.append("%s - %s" % (label, checktoken))

    # Needs to be converted to a list of dictionaries
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

    # Prints the selected checks to console
    for item in answers['remove_checks']:
        print(item)

    _utils.seperator()

    message = "Are you sure you want to remove the selected checks"

    confirm = _utils.inquirer_confirm(message, default=False)

    # Deletes all selected checks
    if confirm:
        for _key, value in checks.items():
            checktoken = value['parameters']['checktoken']

            for to_remove in answers['remove_checks']:
                if checktoken in to_remove:
                    checkid = value['_id']
                    try:
                        delete_checks.remove(token, checkid)
                    except urllib.error.URLError:
                        raise "Lost connection to NodePing"

                    print("Deleted %s" % to_remove)

    _utils.seperator()
    print("Done!\n")
