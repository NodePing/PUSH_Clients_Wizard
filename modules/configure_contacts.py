#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyInquirer import prompt
from nodeping_api import get_contacts

from . import _utils


def choose_contacts(contact_dict):
    """ Asks the user what contacts they wish to use

    Asks the user what contacts will be assigned to notifications
    Takes a dictionary formated by format_contacts() and returns
    a list that contains the user selected contacts
    """

    view_contacts = []

    for key, value in contact_dict.items():
        string = "{0} - {1}".format(value['name'], value['address'])
        view_contacts.append(string)

    view_contacts.append('None')

    complete = False

    while not complete:
        user_contacts = []
        add_contacts = True

        while add_contacts:
            questions = [
                {
                    'type': 'list',
                    'name': 'contact',
                    'message': 'Select a contact for notifications',
                    'choices': view_contacts
                },
                {
                    'type': 'list',
                    'name': 'delay',
                    'message': 'How many minutes do you want to delay notifications',
                    'choices': [
                        'Immediate',
                        '1', '2', '3', '5', '8', '10', '15', '20', '30', '45', '60'
                    ],
                    'when': lambda answers: answers['contact'] != "None"
                },
                {
                    'type': 'list',
                    'name': 'schedule',
                    'message': 'What is the time schedule for receiving notifications',
                    'choices': [
                        'All the time',
                        'Weekends',
                        'Weekdays',
                        'Days',
                        'Nights'
                    ],
                    'when': lambda answers: answers['contact'] != "None"
                },
                {
                    'type': 'confirm',
                    'name': 'add_another',
                    'message': 'Do you want to add another contact',
                    'when': lambda answers: answers['contact'] != "None"
                }
            ]

            answers = prompt(questions)

            try:
                add_another = answers['add_another']
            except KeyError:
                add_another = False

            if not answers['contact']:
                return []

            if not add_another:
                add_contacts = False

            for key, value in contact_dict.items():
                if value['name'] in answers['contact']:
                    if answers['delay'] == 'Immediate':
                        delay = 0
                    else:
                        delay = answers['delay']

                    if answers['schedule'] == 'All the time':
                        schedule = "All"
                    else:
                        schedule = answers['schedule']

                    info = {key: {"delay": delay,
                                  "schedule": schedule}}

                    user_contacts.append(info)

        confirmation = {
            'type': 'confirm',
            'name': 'complete',
            'message': 'Is this information correct',
            'default': True
        }

        print("\n")

        for i in user_contacts:
            for key in i:
                name = contact_dict[key]['name']
                delay = i[key]['delay']
                schedule = i[key]['schedule']

            print("{0}: Delay: {1}  Schedule: {2}".format(
                name, delay, schedule))

        if len(user_contacts) == 0:
            print("Contacts: None")

        get_confirmation = prompt(confirmation)

        if get_confirmation['complete']:
            complete = True
        else:
            _utils.seperator()

    return user_contacts


def format_contacts(contacts):
    """ Takes contacts from NodePing and formats the data

    Data is put into a new dictionary that will be used by
    the push client wizard
    """

    contacts_dict = {}

    for key, value in contacts.items():
        _id = value['addresses']
        name = value['name']

        for contact_id, details in _id.items():
            address = details['address']

            i = {contact_id: {'name': name, 'address': address}}

            contacts_dict.update(i)

    return contacts_dict


def main(token, customerid=None):
    """
    Gets contacts and prompts user for what contacts
    and alert times will be used for check
    """

    query_nodeping = get_contacts.GetContacts(token, customerid)
    contacts = query_nodeping.get_all()

    contacts = format_contacts(contacts)

    contact_info = choose_contacts(contacts)

    return contact_info
