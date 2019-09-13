#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


def disable_by_label(token, label, disable=False, customerid=None):
    """ Toggle a check so it is enabled or disabled.

    Accepts an API token, the checkid of the check to be toggled,
    whether it's enabled/disabled (disable by default), and the
    customerid if the check is a part of a subaccount

    :type token: string
    :param token: API token from NodePing
    :type label: string
    :param label: label of check that will be disabled/enabled
    :type disable: bool
    :param diable: Whether the check should be enabled or disabled
    :type customerid: string
    :param customerid: subaccount ID if check is on a subaccount
    :rtype: dict
    :return: Dictionary with response from NodePing about disabled check(s)
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

    :type token: string
    :param token: API token from NodePing
    :type target: string
    :param: URL of target to disable checks for
    :type disable: bool
    :param disable: Whether the check(s) should be enabled or disables
    :type customerid: string
    :param customerid: subaccount ID if the check is on a subaccount
    :rtype: dict
    :return: Dictionary with response from NodePing about disabled check(s)
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

    :type token: string
    :param token: API token from NodePing
    :type _type: string
    :param _type: Check type to disable
    :type disable: bool
    :param disable: Whether the check should be disabled or not
    :type customerid: string
    :param customerid: subaccount ID if the check is on a subaccount
    :rtype: dict
    :return: Dictionary with response from NodePing about disabled check(s)
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

    :type token: string
    :param token: API token from NodePing
    :type disable: bool
    :param disable: Whether the check should be disabled or not
    :type customerid: string
    :param customerid: subaccount ID if the check is on a subaccount
    :rtype: dict
    :return:O Dictionary with response from NodePing about disabled check(s)
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
