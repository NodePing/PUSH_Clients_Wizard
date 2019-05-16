#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from os.path import dirname, expanduser, join, realpath
from sys import exit
from modules import _utils, manage_checks
from pprint import pprint


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
    fields = info['parameters']['fields']

    output = "Complete!\n\nLabel: {0}\n_id: {1}\nchecktoken: {2}\nEnabled: {3}\nInterval: {4}\nPublic: {5}\nFields:".format(
        label, _id, checktoken, enabled, interval, public)

    print(output)
    pprint(fields)


def main():

    config = configparser.ConfigParser()
    config.read(CONFIGFILE)

    token = _utils.get_user_token(config, CONFIGFILE)

    interaction = True

    while interaction:
        response = input(
            "Do you want to (L)ist PUSH checks, (C)reate a PUSH check, (D)elete a PUSH check, or (E)xit? ").upper()

        if response == "L":
            manage_checks.list_checks(token)

        elif response == "C":
            check_info = manage_checks.configure(token)
            created_check(check_info)

        elif response == "D":
            manage_checks.delete(token)
        elif response == "E":
            print("Bye")
            exit(0)
        else:
            print(
                "Not a valid response. " +
                "Enter:\nL - List checks\n" +
                "C - create check\n" +
                "D - delete check\n")


if __name__ == '__main__':
    main()
