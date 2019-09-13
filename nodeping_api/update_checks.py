#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


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

    if not isinstance(checkid, str):
        # print("To update many checks, use the update_many method")
        raise StrExpected

    check_token.is_valid(token)

    if customerid:
        url = "{0}checks/{1}?token={2}&customerid={3}".format(
            API_URL, checkid, token, customerid)
    else:
        url = "{0}checks/{1}?token={2}".format(
            API_URL, checkid, token)

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

    if not isinstance(checkids, dict):
        raise DictExpected

    check_token.is_valid(token)

    for checkid, checktype in checkids.items():
        if customerid:
            url = "{0}checks/{1}?token={2}&customerid={3}".format(
                API_URL, checkid, token, customerid)
        else:
            url = "{0}checks/{1}?token={2}".format(
                API_URL, checkid, token)

        send_fields = fields.copy()
        send_fields.update({"type": checktype.upper()})

        updated_checks.append(_query_nodeping_api.put(url, send_fields))

    return updated_checks


class StrExpected(Exception):
    """ Raised if the proper type isn't supplied
    """

    pass


class DictExpected(Exception):
    """ Raised if the proper type isn't supplied
    """

    pass
