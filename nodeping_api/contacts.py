#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


def get_all(token, customerid=None):
    """ Gets all contacts that exist for the account

    Returns all the data in a dictionary format from the
    original JSON that is gathered from NodePing

    :type token: string
    :param token: NodePing API token
    :type customerid: string
    :param customerid: subaccount ID
    :return: All contacts and their addresses
    :rtype: dict
    """

    check_token.is_valid(token)

    if customerid:
        url = "{0}contacts?token={1}&customerid={2}".format(
            API_URL, token, customerid)
    else:
        url = "{0}contacts?token={1}".format(API_URL, token)

    return _query_nodeping_api.get(url)


def get_by_type(token, contacttype, customerid=None):
    """ Get a contact based on its type, such as email, sms, webhook

    Returns all the data in a dictionary format from the originl
    JSON that is gathered from NodePing.

    :param token: NodePing API token
    :type token: str
    :type contacttype: string
    :param contacttype: Type of contact to be retrieved
    :type customerid: string
    :param customerid: subaccount ID
    :return: Contacts by their contact type
    :rtype: dict
    """

    check_token.is_valid(token)

    contact_dict = {}

    if customerid:
        url = "{0}contacts?token={1}&customerid={2}".format(
            API_URL, token, customerid)
    else:
        url = "{0}contacts?token={1}".format(API_URL, token)

    contacts = _query_nodeping_api.get(url)

    for key, value in contacts.items():
        _id = value['addresses']

        for _contact_id, details in _id.items():
            _type = details['type']

            if _type == contacttype:
                contact_dict.update({key: value})

    return contact_dict


def create_contact(token,
                   customerid=None,
                   name=None,
                   custrole="view",
                   newaddresses=None):
    """ Create a new contact on your NodePing account.
    Create a list of dictionaries for the newaddresses variable
    that will contain contact information such as the address,
    type, and optional values specified in the doctumentation
    for webhooks.

    https://nodeping.com/docs-api-contacts.html#post-put

    newaddresses example:
    [{'address': 'me@email.com'}, {'address': '5551238888'}]

    newaddresses webhook:
    [{'action': 'POST',
      'address': 'https://webhook.example.com',
      'data': {'event': '{event}',
               'id': '{_id}',
               'label': '{label}',
               'runtime': '{runtime}',
               'target': '{target}'},
      'headers': {'Content-Type': 'application/json'},
      'type': 'webhook'}]

    :param token: The NodePing token for the account
    :type token: str
    :param customerid: (optional) ID for subaccount
    :type customerid: str
    :param name: The name of your contact
    :type name: str
    :param custrole: permissions for this contact. Default: view
    :type custrole: str
    :param newaddresses: list of dictionaries containing address info
    :type newaddresses: list
    :return: Created contact information
    :rtype: dict
    """

    check_token.is_valid(token)

    if customerid:
        url = "{0}contacts?token={1}&customerid={2}".format(
            API_URL, token, customerid)
    else:
        url = "{0}contacts?token={1}".format(API_URL, token)

    addresses = [{"address": address} for address in newaddresses]

    data = {'name': name,
            'newaddresses': addresses,
            'custrole': custrole}

    created = _query_nodeping_api.post(url, data)

    return created


def update_contact(token,
                   contact_id,
                   customerid=None,
                   name=None,
                   newaddresses=None,
                   addresses=None,
                   custrole=None):
    """ Supply a dictionary with new contact addresses or an updated dict
    of the contact's addresses to update the specified contact ID.

    NOTE: If you are using the addresses argument to update an existing
    address, you must supply the entire list of contacts. For example, if
    a contact has 2 addresses and you are only updating one, you must supply
    both addresses, one being with the revisions you are planning to make.

    :param token: The NodePing token for the account
    :type token: str
    :param contact_id: The ID of the contact that is being changed
    :type contact_id: str
    :param customerid: (optional) ID for subaccount
    :type customerid: str
    :param name: New name for the contact
    :type name: str
    :param newaddresses: Any new addresses to provide for the contact
    :type newaddresses: list
    :param addresses: Used to update existing addresses for the account
    :type addresses: dict
    :param custrole: The permissions the contact has over checks
    :type custrole: str
    :return: An array with the contents of the updated contact
    :rtype: dict
    """

    check_token.is_valid(token)

    if customerid:
        url = "{0}contacts/{1}?token={2}&customerid={3}".format(
            API_URL, contact_id, token, customerid)
    else:
        url = "{0}contacts/{1}?token={2}".format(API_URL, contact_id, token)

    data = {}

    if newaddresses:
        # Do with newaddresses
        new_addresses = [{"address": address} for address in newaddresses]
        data.update({'newaddresses': new_addresses})
    if addresses:
        # Do with addresses

        data.update({'addresses': addresses})

    if name:
        data.update({'name': name})
    if custrole:
        data.update({'custrole': custrole})

    return _query_nodeping_api.put(url, data)


def delete_contact(token,
                   contact_id,
                   customerid=None):
    """ Delete a contact on your account

    Specify the ID for the contact that will be deleted from your account

    :param token: The NodePing token for the account
    :type token: str
    :param contact_id: The ID of the contact that will be deleted
    :type contact_id: str
    :param customerid: (optional) ID for subaccount
    :type: str
    :return: Info about your check being deleted or an error
    :rtype: dict
    """

    check_token.is_valid(token)

    if customerid:
        url = "{0}contacts/{1}?token={2}&customerid={3}".format(
            API_URL, contact_id, token, customerid)
    else:
        url = "{0}contacts/{1}?token={2}".format(API_URL, contact_id, token)

    return _query_nodeping_api.delete(url)


def reset_password(token, contact_id, customerid=None):
    """ Reset the password for the specified contact

    You can get the contact_id by querying the API with the get_all
    function. The ID would look something like this: "201205050153W2Q4C-OVDN7"

    :param token: The NodePing token for the account
    :type token: str
    :param contact_id: The contact that will have its password reset
    :type contact_id: str
    :param customerid: (optional) ID for subaccount
    :type customerid: str
    :return: A dictionary with a key or 'error' or 'success'
    :rtye: dict
    """

    check_token.is_valid(token)

    if customerid:
        url = "{0}contacts/{1}?token={2}&customerid={3}&action=RESETPASSWORD".format(
            API_URL, contact_id, token, customerid)
    else:
        url = "{0}contacts/{1}?token={2}&action=RESETPASSWORD".format(
            API_URL, contact_id, token)

    return _query_nodeping_api.get(url)
