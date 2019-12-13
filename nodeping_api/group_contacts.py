#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import _query_nodeping_api, _utils, config

API_URL = "{0}contactgroups".format(config.API_URL)


def get_all(token, customerid=None):
    """ Get all contact groups that exist for the account

    Returns all the data in a dictionary format from the
    original JSON that is gathered from NodePing

    :param token: The NodePing API token for the account
    :type token: str
    :param customerid: (optional) ID for subaccount
    :type customerid: str
    :return: All contact groups for specified account
    :rtype: dict
    """

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.get(url)


def create_group(token, name, members=None, customerid=None):
    """ Create new contact groups for your NodePing account

    Create a new contact group with a specified name and
    optional members.

    :param token: The NodePing token for the account
    :type token: str
    :param name: The name of the contact group
    :type name: str
    :param members: (optional) The contact names that are a part of the group
    :type members: list
    :param customerid: (optional) ID for subaccount
    :type customerid: str
    :return: Information about the newly created contact group
    :rtype: dict
    """

    if members:
        data = {'name': name, 'members': members}
    else:
        data = {'name': name}

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, data)


def update_group(token, group_id, name=None, members=None, customerid=None):
    """ Update an existing contact group on your NodePing account

    Update a contact group with a specified name and
    optional members.

    :param token: The NodePing token for the account
    :type token: str
    :param group_id: the Group ID that will have its information updated
    :type group_id: str
    :param name: Optional new name of the contact group
    :type name: str
    :param members: (optional) The contact names that are a part of the group
    :type members: list
    :param customerid: (optional) ID for subaccount
    :type customerid: str
    :return: Information about the newly created contact group
    :rtype: dict
    """

    if members:
        data = {'name': name, 'members': members}
    else:
        data = {'name': name}

    url = "{0}/{1}".format(API_URL, group_id)
    url = _utils.create_url(token, url, customerid)

    return _query_nodeping_api.put(url, data)


def delete_group(token, group_id, customerid=None):
    """ Delete a contact group for the specified account

    Returns all the data in a dictionary format from the
    original JSON that is gathered from NodePing

    :param token: The NodePing API token for the account
    :type token: str
    :param group_id: The ID for the target contact group
    :type group_id: str
    :param customerid: (optional) ID for subaccount
    :type customerid: str
    :return: All contact groups for specified account
    :rtype: dict
    """

    url = "{0}/{1}".format(API_URL, group_id)
    url = _utils.create_url(token, url, customerid)

    return _query_nodeping_api.delete(url)
