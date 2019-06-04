#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


def get_all(token, customerid=None):
    """ Gets all contacts that exist for the account

    Returns all the data in a dictionary format from the
    original JSON that is gathered from NodePing
    """

    check_token.is_valid(token)

    if customerid:
        url = "{0}contacts?token={1}&customerid={2}".format(
            API_URL, token, customerid)
    else:
        url = "{0}contacts?token={1}".format(API_URL, token)

    return _query_nodeping_api.get(url)


def get_by_type(token, contacttype, customerid=None):
    """ Get a contact based on its type, such as email, sms, webhook

    Returns all the data in a dictionary format from the originl
    JSON that is gathered from NodePing.
    """

    contact_dict = {}

    if customerid:
        url = "{0}contacts?token={1}&customerid={2}".format(
            API_URL, token, customerid)
    else:
        url = "{0}contacts?token={1}".format(API_URL, token)

    contacts = _query_nodeping_api.get(url)

    for key, value in contacts.items():
        _id = value['addresses']

        for contact_id, details in _id.items():
            _type = details['type']

            if _type == contacttype:
                contact_dict.update({key: value})

    return contact_dict
