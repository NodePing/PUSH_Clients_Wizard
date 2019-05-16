#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api

API_URL = 'https://api.nodeping.com/api/1/'


def get_all(token, customerid=None):
    """ Gets all contacts that exist for the account

    Returns all the data in a dictionary format from the
    original JSON that is gathered from NodePing
    """

    check_token.main(token)

    if customerid:
        url = "{0}contacts?token={1}&customerid={2}".format(
            API_URL, token, customerid)
    else:
        url = "{0}contacts?token={1}".format(API_URL, token)

    return _query_nodeping_api.get(url)


class GetContacts:
    def __init__(self, token, customerid=None, contacttype=None):
        self.token = token
        self.customerid = customerid
        self.contacttype = contacttype

        check_token.main(self.token)

    def get_all(self):
        """ Gets all contacts that exist for the account

        Returns all the data in a dictionary format from the
        original JSON that is gathered from NodePing
        """

        if self.customerid:
            url = "{0}contacts?token={1}&customerid={2}".format(
                API_URL, self.token, self.customerid)
        else:
            url = "{0}contacts?token={1}".format(API_URL, self.token)

        return _query_nodeping_api.get(url)

    def get_by_type(self):
        """ Get a contact based on its type, such as email, sms, webhook

        Returns all the data in a dictionary format from the originl
        JSON that is gathered from NodePing.
        """

        contact_dict = {}

        if self.customerid:
            url = "{0}contacts?token={1}&customerid={2}".format(
                API_URL, self.token, self.customerid)
        else:
            url = "{0}contacts?token={1}".format(API_URL, self.token)

        contacts = _query_nodeping_api.get(url)

        for key, value in contacts.items():
            _id = value['addresses']

            for contact_id, details in _id.items():
                _type = details['type']

                if _type == self.contacttype:
                    contact_dict.update({key: value})

        return contact_dict
