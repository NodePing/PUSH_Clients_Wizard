#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


def update(token, checkid, fields, customerid=None):
    """ Updates a field(s) in an exsting NodePing check

    Accepts a token, checkid, and fields to be updated in a NodePing
    check. Updates the specified fields for the one check. To update
    many checks with the same value, use update_many
    """

    if type(checkid) == list:
        # print("To update many checks, use the update_many method")
        raise(StrExpected)

    check_token.is_valid(token)

    if customerid:
        url = "{0}checks/{1}?token={2}&customerid={3}".format(
            API_URL, checkid, token, customerid)
    else:
        url = "{0}checks/{1}?token={2}".format(
            API_URL, checkid, token)

    return _query_nodeping_api.put(url, fields)


def update_many(token, checkids, fields, customerid=None):
    """ Updates a field(s) in multiple existing NodePing checks

    Accepts a token, a list of checkids, and fields to be updated in a
    NodePing check. Updates the specified fields for the one check.
    To update many checks with the same value, use update_many
    """

    updated_checks = []

    if type(checkids) != list:
        # raise("To update multiple checks, provide a list of Check IDs")
        raise(ListExpected)

    check_token.is_valid(token)

    for _id in checkids:
        if customerid:
            url = "{0}checks/{1}?token={2}&customerid={3}".format(
                API_URL, _id, token, customerid)
        else:
            url = "{0}checks/{1}?token={2}".format(
                API_URL, _id, token)

        updated_checks.append(_query_nodeping_api.put(url, fields))

    return updated_checks


class StrExpected(Exception):
    """ Raised if the proper type isn't supplied
    """

    pass


class ListExpected(Exception):
    """ Raised if the proper type isn't supplied
    """

    pass
