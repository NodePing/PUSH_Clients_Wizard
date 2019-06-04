#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


def disable_by_label(token, label, disable=False, customerid=None):
    """ Toggle a check so it is enabled or disabled.

    Accepts an API token, the checkid of the check to be toggled,
    whether it's enabled/disabled (disable by default), and the
    customerid if the check is a part of a subaccount
    """

    check_token.is_valid(token)

    if disable:
        disable = "true"
    else:
        disable = "false"

    if customerid:
        url = "{0}checks?token={1}&customerid={2}&label={3}&disableall={4}".format(
            API_URL, token, customerid, label, disable)
    else:
        url = "{0}checks?token={1}&label={2}&disableall={3}".format(
            API_URL, token, label, disable)

    return _query_nodeping_api.put(url)


def disable_by_target(token, target, disable=False, customerid=None):
    """ Toggle a check so it is enabled or disabled.

    Accepts an API token, the checkid of the check to be toggled,
    whether it's enabled/disabled (disable by default), and the
    customerid if the check is a part of a subaccount
    """

    check_token.is_valid(token)

    if disable:
        disable = "true"
    else:
        disable = "false"

    if customerid:
        url = "{0}checks?token={1}&customerid={2}&target={3}&disableall={4}".format(
            API_URL, token, customerid, target, disable)
    else:
        url = "{0}checks?token={1}&target={2}&disableall={3}".format(
            API_URL, token, target, disable)

    return _query_nodeping_api.put(url)


def disable_by_type(token, _type, disable=False, customerid=None):
    """ Toggle a check so it is enabled or disabled.

    Accepts an API token, the checkid of the check to be toggled,
    whether it's enabled/disabled (disable by default), and the
    customerid if the check is a part of a subaccount
    """

    check_token.is_valid(token)

    if disable:
        disable = "true"
    else:
        disable = "false"

    if customerid:
        url = "{0}checks?token={1}&customerid={2}&type={3}&disableall={4}".format(
            API_URL, token, customerid, _type, disable)
    else:
        url = "{0}checks?token={1}&type={2}&disableall={3}".format(
            API_URL, token, _type, disable)

    return _query_nodeping_api.put(url)


def disable_all(token, disable=False, customerid=None):
    """ Toggle a check so it is enabled or disabled.

    Accepts an API token, the checkid of the check to be toggled,
    whether it's enabled/disabled (disable by default), and the
    customerid if the check is a part of a subaccount
    """

    check_token.is_valid(token)

    if disable:
        disable = "true"
    else:
        disable = "false"

    if customerid:
        url = "{0}checks?token={1}&customerid={2}&disableall={3}".format(
            API_URL, token, customerid, disable)
    else:
        url = "{0}checks?token={1}&disableall={2}".format(
            API_URL, token, disable)

    return _query_nodeping_api.put(url)
