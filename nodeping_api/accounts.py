#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Manage your account and subaccounts via the API, as referenced
in the NodePing documentation.

https://nodeping.com/docs-api-accounts.html

If an invalid token is supplied, you will receive a dictionary with
a key called "error"
"""

from . import _query_nodeping_api, _utils, config

API_URL = "{0}accounts".format(config.API_URL)


def get_account(token, customerid=None):
    """ Get parent account and subaccount information

    :param token: The NodePing token for the account
    :type token: str
    :param customerid: (optional) ID for subaccount
    :type customerid: str
    :return: Info that was returned from NodePing about the account
    :rtype: dict

    """

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.get(url)


def create_subaccount(token,
                      name,
                      contactname,
                      email,
                      timezone,
                      location,
                      emailme=False
                      ):
    """ Create a subaccount with your NodePing account.

    :param token: The NodePing token for the account
    :type token: str
    :param name: The name of the subaccount
    :type name: str
    :param contactname: The name of the new contact for the subaccount
    :type contactname: str
    :param email: Email address used for the contact for the subaccount
    :type email: str
    :param timezone: Timezone. +/0 from GMT (e.g. GMT-6) would be -6
    :type timezone: str
    :param location: The region of the subaccount (e.g. name, eur, lam, etc.)
    :type location: str
    :param emailme: email to opt-in the subaccount for features & notifications
    :type emailme: bool
    :return: Info returned from NodePing about the created subaccount
    :rtype: dict
    """

    url = "{0}?token={1}".format(API_URL, token)

    data = locals()

    if data['emailme']:
        data['emailme'] = "yes"
    else:
        data['emailme'] = "no"

    return _query_nodeping_api.post(url, data)


def update_account(token,
                   customerid=None,
                   name=None,
                   timezone=None,
                   location=None,
                   emailme=False,
                   status=None
                   ):
    """ Update information about the parent account or subaccounts

    :param token: The NodePing token for the account
    :type token: str
    :param customerid: (optional) ID for subaccount
    :type customerid: str
    :param name: The name of the subaccount
    :type name: str
    :param timezone: Timezone. +/0 from GMT (e.g. GMT-6) would be -6
    :type timezone: str
    :param location: The region of the subaccount (e.g. name, eur, lam, etc.)
    :type location: str
    :param emailme: email to opt-in the subaccount for features & notifications
    :type emailme: bool
    :param status: subaccount status. Either "Active" or "Suspend"
    :type status: str
    :return: Info returned from NodePing about the updated subaccount
    :rtype: dict
    """

    url = _utils.create_url(token, API_URL, customerid)

    parameters = locals()
    data = {}

    for key, value in parameters.items():
        if value:
            data.update({key: value})

    return _query_nodeping_api.put(url, data_dictionary=data)


def delete_account(token, customerid):
    """ Delete the specified subaccount (parent cannot be deleted)

    :param token: The NodePing token for the account
    :type token: str
    :param customerid: The subaccount of the account to delete
    :type customerid: str
    :return: Status about the subaccount deletion
    :rtype: dict
    """

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.delete(url)


def disable_notifications(token,
                          customerid=None,
                          accountsupressall=False):
    """ Re-enable/disable notifications for an account.

    Disabling notifications on the parent account will not disable
    notifications for any subaccounts.

    :param token: The NodePing token for the account
    :type token: str
    :param customerid: The subaccount ID that notifications will be disabled on
    :type customerid: str
    :param accountsupressall: Whether to enable or disable notifications
    :type accountsupressall: bool
    :return: Response about notifications being supressed or enabled
    :rtype: dict
    """

    url = _utils.create_url(token, "{0}?accountsupressall={1}".format(
        API_URL, accountsupressall), customerid)

    return _query_nodeping_api.put(url)
