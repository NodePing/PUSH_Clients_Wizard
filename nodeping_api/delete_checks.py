#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


def remove(token, checkid, customerid=None):
    """ Deletes a check with a give Check ID

    :type token: string
    :param token: API token from NodePing
    :type checkid: string
    :param checkid: ID of check that will be deleted
    :type customerid: string
    :param customerid: subaccount ID if check is on a subaccount
    :rtype: dict
    :return: Dictionary with response from NodePing about check removal
    """

    check_token.is_valid(token)

    if customerid:
        url = "{0}checks/{1}?token={2}&customerid={3}".format(
            API_URL, checkid, token, customerid)
    else:
        url = "{0}checks/{1}?token={2}".format(API_URL, checkid, token)

    return _query_nodeping_api.delete(url)
