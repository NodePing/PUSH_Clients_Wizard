#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Update one or many checks on a NodePing account or subaccount
"""

from . import _query_nodeping_api, _utils, config

API_URL = "{0}checks".format(config.API_URL)


def update(token, checkid, checktype, fields, customerid=None):
    """ Updates a field(s) in an exsting NodePing check

    Accepts a token, checkid, and fields to be updated in a NodePing
    check. Updates the specified fields for the one check. To update
    many checks with the same value, use update_many

    :type token: string
    :param token: Your NodePing API token
    :type checkid: string
    :param checkid: CheckID to update
    :param checktype: The type of the check (PING, HTTP, DNS, etc.)
    :type checktype: str
    :type fields: dict
    :param fields: Fields in check that will be updated
    :type customerid: string
    :param customerid: subaccount ID
    :rtype: dict
    :return: Return information from NodePing query
    """

    url = "{0}/{1}".format(API_URL, checkid)
    url = _utils.create_url(token, url, customerid)

    fields.update({"type": checktype.upper()})

    return _query_nodeping_api.put(url, fields)


def update_many(token, checkids, fields, customerid=None):
    """ Updates a field(s) in multiple existing NodePing checks

    Accepts a token, a list of checkids, and fields to be updated in a
    NodePing check. Updates the specified fields for the one check.
    To update many checks with the same value, use update_many

    :type token: string
    :param token: Your NodePing API token
    :type checkids: dict
    :param checkids: CheckIDs with their check type to update
    :type fields: dict
    :param fields: Fields in check that will be updated
    :type customerid: string
    :param customerid: subaccount ID
    :rtype: dict
    :return: Return information from NodePing query
    """

    updated_checks = []

    for checkid, checktype in checkids.items():
        url = "{0}/{1}".format(API_URL, checkid)
        url = _utils.create_url(token, url, customerid)

        send_fields = fields.copy()
        send_fields.update({"type": checktype.upper()})

        updated_checks.append(_query_nodeping_api.put(url, send_fields))

    return updated_checks
