#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyInquirer import prompt
from nodeping_api import contacts, group_contacts, schedules

from . import _utils


def choose_contacts(contact_dict, cust_schedules):
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
                    'message': 'What notification schedule would you like to use',
                    'choices': cust_schedules,
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

            # Return that no contacts were chosen
            if not answers['contact']:
                return []

            if not add_another:
                add_contacts = False

            for key, value in contact_dict.items():
                if value['name'] in answers['contact'] and value['address'] in answers['contact']:
                    if answers['delay'] == 'Immediate':
                        delay = 0
                    else:
                        delay = answers['delay']

                    if answers['schedule'] == 'All the time':
                        schedule = "All"
                    else:
                        schedule = answers['schedule']

                    # Needed to properly add contact groups
                    if value['address'] == 'Group':
                        if value['name'] not in answers['contact']:
                            continue

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

        formatted_contacts = []
        # For some duplicates to be removed, the accepted contacts needed
        # to be put in a new list
        returned_contacts = []

        for i in user_contacts:
            for key in i:
                name = contact_dict[key]['name']
                address = contact_dict[key]['address']
                delay = i[key]['delay']
                schedule = i[key]['schedule']

            print_contact = "{0} {1}: Delay: {2}  Schedule: {3}".format(
                name, address, delay, schedule)

            # Removing duplicates that have the same name and address
            if print_contact not in formatted_contacts:
                formatted_contacts.append(print_contact)
                returned_contacts.append(i)
                print(print_contact)

        if not user_contacts:
            print("Contacts: None")

        get_confirmation = prompt(confirmation)

        if get_confirmation['complete']:
            complete = True
        else:
            _utils.seperator()

    return returned_contacts


def format_contacts(contacts):
    """ Takes contacts from NodePing and formats the data

    Data is put into a new dictionary that will be used by
    the push client wizard
    """

    contacts_dict = {}

    for key, value in contacts.items():
        try:
            _id = value['addresses']
        # Exception means it is a group contact
        except KeyError:
            contacts_dict.update(
                {key: {'name': value['name'], 'address': 'Group'}})
            continue

        # Add a single contact to the dictionary
        try:
            name = value['name']
        except KeyError:
            name = "(empty)"

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

    # All availavle schedules to user
    all_schedules = ["All the time"]

    # Collects existin schedules from user's account
    cust_schedules = schedules.get_schedule(token, customerid=customerid)

    # Gets the names of the schedules
    for key, _value in cust_schedules.items():
        all_schedules.append(key)

    single_contacts = contacts.get_all(token, customerid=customerid)
    contactgroups = group_contacts.get_all(token, customerid=customerid)
    single_contacts.update(contactgroups)

    single_contacts = format_contacts(single_contacts)

    contact_info = choose_contacts(single_contacts, all_schedules)

    return contact_info
