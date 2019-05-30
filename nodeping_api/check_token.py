#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import _query_nodeping_api

API_URL = 'https://api.nodeping.com/api/1/'


def info(token, customerid=None):
    """ Returns the info for your account
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


if __name__ == '__main__':
    main()
