#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
try:
    from urllib.error import HTTPError as httperror
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen
    from urllib2 import HTTPError as httperror


def post(url, data_dictionary):
    """ Queries the NodePing API via POST and creates a check

    Accepts a URL and data and POSTs the results to NodePing
    which then creates the check on the account with the user
    specified parameters

    :type url: string
    :param url: The URL that will have data that is POSTed to NodePing
    :type data_dictionary: string
    :param data_dictionary: Dictionary of data that is sent to NodePing
    :return: Data that was returned from NodePing after POST
    :rtype: dict
    """

    json_data = json.dumps(data_dictionary).encode('utf-8')

    req = Request(url)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Content-Length', len(json_data))

    try:
        data = urlopen(req, json_data)
    except httperror as err:
        data = err

    json_bytes = data.read()

    return json.loads(json_bytes.decode('utf-8'))


def put(url, data_dictionary=None):
    """ Queries the NodePing API via PUT and updates a check

    Accepts a URL and data and PUTs the results to NodePing. The
    URL must have a checkid in the URL that will be updated. This
    updates the specified fields in the check.

    :type url: string
    :param url: The URL that will have data that is PUT to NodePing
    :type data_dictionary: dict
    :param data_dictionary: Dictionary of data that is sent to NodePing
    :return: Data that was returned from NodePing after PUT
    :rtype: dict
    """

    if data_dictionary:
        json_data = json.dumps(data_dictionary).encode('utf-8')

    req = Request(url)
    req.get_method = lambda: 'PUT'

    if data_dictionary:
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header('Content-Length', len(json_data))

    try:
        if data_dictionary:
            data = urlopen(req, json_data)
        else:
            data = urlopen(req)
    except httperror as err:
        data = err

    json_bytes = data.read()

    return json.loads(json_bytes.decode('utf-8'))


def get(url):
    """ Queries the NodePing API via GET and returns its results

    Accepts a URL to the NodePing API to query and retrieves
    data provided by NodePing, and then converts the contents
    to a dictionary

    :type url: string
    :param url: The URL that will be used for GET request
    :return: Data that was returned from NodePing from GET request
    :rtype: dict
    """

    req = Request(url)

    try:
        data = urlopen(req)
    except httperror as err:
        data = err

    json_bytes = data.read()

    return json.loads(json_bytes.decode('utf-8'))


def delete(url):
    """ Queries the NodePing API via DELETE and returns its result

    Accepts a URL to the NodePing API to do a delete. A dictionary
    will be returned with "ok" == true meaning it was deleted, if
    false then the check wasn't deleted or an invalid ID was given

     :type url: string
    :param url: The URL that will be used for DELETE request
    :return: Data that was returned from NodePing from DELETE request
    :rtype: dict
    """

    req = Request(url)
    req.get_method = lambda: 'DELETE'

    try:
        data = urlopen(req)
    except httperror as err:
        data = err

    json_bytes = data.read()

    return json.loads(json_bytes.decode('utf-8'))
