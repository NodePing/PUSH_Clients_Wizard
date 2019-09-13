#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


def get_notifications(token,
                      customerid=None,
                      check_id=None,
                      span=None,
                      limit=300,
                      subaccounts=False):
    """ Get notifications for a check or all checks

    :param check_id: Optional check ID which you want to list notifications
    :type check_id: str
    :param customerid: Optional customerid for subaccount
    :type customerid: str
    :param span: number of hours of notifications to retrieve
    :type span: int
    :param limit: Number of records to retrieve (default 300)
    :type limit: int
    :param subaccounts: subaccount notifications will be included
    :type subaccounts: bool
    :return: Notifications for account based on parameters set
    :rtype: list
    """

    check_token.is_valid(token)

    arguments = locals()
    set_args = {}

    for key, value in arguments.items():
        if value:
            if key in ("token", "check_id"):
                continue

            set_args.update({key: value})

    if check_id:
        url = "{0}notifications/{1}?token={2}".format(
            API_URL, check_id, token)
    else:
        url = "{0}notifications?token={1}".format(API_URL, token)

    for key, value in set_args.items():
        url = "{0}&{1}={2}".format(url, key, value)

    return _query_nodeping_api.get(url)
