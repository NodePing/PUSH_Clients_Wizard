#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enable or disable checks on your account or subaccount.
Disable checks by label, the target, by check type
(such as PING, PUSH, HTTP) and disable all.
"""

from . import _utils, _query_nodeping_api, config

API_URL = "{0}checks".format(config.API_URL)


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

    if disable:
        disable = "true"
    else:
        disable = "false"

    url = "{0}?label={1}&disableall={2}".format(
        API_URL, _utils.escape_url_string(label), disable)
    url = _utils.create_url(token, url, customerid)

    return _query_nodeping_api.put(url)


def disable_by_target(token, target, disable=False, customerid=None):
    """ Toggle a check so it is enabled or disabled.

    Accepts an API token, the checkid of the check to be toggled,
    whether it's enabled/disabled (disable by default), and the
    customerid if the check is a part of a subaccount

    :type token: string
    :param token: API token from NodePing
    :type target: string
    :param target: URL of target to disable checks for
    :type disable: bool
    :param disable: Whether the check(s) should be enabled or disables
    :type customerid: string
    :param customerid: subaccount ID if the check is on a subaccount
    :rtype: dict
    :return: Dictionary with response from NodePing about disabled check(s)
    """

    if disable:
        disable = "true"
    else:
        disable = "false"

    url = "{0}?target={1}&disableall={2}".format(API_URL, target, disable)
    url = _utils.create_url(token, url, customerid)

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

    if disable:
        disable = "true"
    else:
        disable = "false"

    url = "{0}?type={1}&disableall={2}".format(API_URL, _type, disable)
    url = _utils.create_url(token, url, customerid)

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

    if disable:
        disable = "true"
    else:
        disable = "false"

    url = "{0}?disableall={1}".format(API_URL, disable)
    url = _utils.create_url(token, url, customerid)

    return _query_nodeping_api.put(url)
