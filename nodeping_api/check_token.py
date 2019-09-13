#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import _query_nodeping_api, config

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

    if customerid:
        url = "{0}accounts?token={1}&customerid={2}".format(
            API_URL, token, customerid)
    else:
        url = "{0}accounts?token={1}".format(API_URL, token)

    valid_token = _query_nodeping_api.get(url)

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

    if customerid:
        url = "{0}accounts?token={1}&customerid={2}".format(
            API_URL, token, customerid)
    else:
        url = "{0}accounts?token={1}".format(API_URL, token)

    valid_token = _query_nodeping_api.get(url)

    try:
        valid_token['error']
    except KeyError:
        return True
    except TypeError:
        return False
