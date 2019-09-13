#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


def get_probe(token, probe="All"):
    """ Get information about all NodePing probes or just one

    The list of probes can be found at our FAQ:
    https://nodeping.com/faq.html

    :param token: NodePing API token
    :type token: str
    :param probe: 2-letter abbreviation for the probe, or default All
    :type probe: str
    :return: Returns all information about the specified probe(s)
    :rtype: dict
    """

    check_token.is_valid(token)

    if probe == "All":
        url = "{0}info/probe?token={1}".format(API_URL, token)
    else:
        url = "{0}info/probe/{1}?token={2}".format(API_URL, probe, token)

    return _query_nodeping_api.get(url)


def get_location(token, location="All"):
    """ Locations for probes in all regions or just one

    :param token: NodePing API token
    :type token: str
    :param location: 3-letter abbreviation for the location, or default All
    :type location: str
    :return: Returns all innformation about the specified location(s)
    :rtype: dict
    """

    check_token.is_valid(token)

    if location == "All":
        url = "{0}info/location?token={1}".format(API_URL, token)
    else:
        url = "{0}info/location/{1}?token={2}".format(API_URL, location, token)

    return _query_nodeping_api.get(url)
