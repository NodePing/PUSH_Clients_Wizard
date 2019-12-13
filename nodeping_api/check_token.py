#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Queries the accounts portion of the API to collect token
information or see if a token or a token + subaccount ID
are valid.
"""

from . import _query_nodeping_api, _utils, config

API_URL = config.API_URL


def info(token, customerid=None):
    """ Returns the info for your account

    :type token: string
    :param token: Your NodePing API token
    :type customerid: string
    :param customerid: Optional subaccount ID for your account
    :return: Return contents from the NodePing query
    :rtype: dict
    """

    url = "{0}accounts".format(API_URL)

    valid_token = _query_nodeping_api.get(
        _utils.create_url(token, url, customerid))

    return valid_token


def is_valid(token, customerid=None):
    """ Returns if your API key is valid or not

    :type token: string
    :param token: Your NodePing API token
    :type customerid: string
    :param customerid: Optional subaccount ID for your account
    :return: True/False if the token is valid or not
    :rtype: bool
    """

    url = "{0}accounts".format(API_URL)

    valid_token = _query_nodeping_api.get(
        _utils.create_url(token, url, customerid))

    try:
        valid_token['error']
    except KeyError:
        return True
    else:
        return False
