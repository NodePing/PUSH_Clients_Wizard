#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Delete a NodePing check on an account or subaccount.
"""

from . import _utils, _query_nodeping_api, config

API_URL = "{0}checks".format(config.API_URL)


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

    url = "{0}/{1}".format(API_URL, checkid)
    url = _utils.create_url(token, url, customerid)

    return _query_nodeping_api.delete(url)
