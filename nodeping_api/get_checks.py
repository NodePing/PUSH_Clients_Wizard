#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Get checks that were created on your NodePing account.

Allows you go get all checks, get passing, failing, by its ID,
disabled checks, and last results for a check.
"""

from . import _query_nodeping_api, _utils, config

API_URL = "{0}checks".format(config.API_URL)


class GetChecks:
    def __init__(self, token, checkid=None, customerid=None):
        """
        :type token: string
        :param token: NodePing API token
        :type checkid: string
        :param checkid: ID for check to retrieve data for
        :type customerid: string
        :param customerid: subaccount ID
        """

        self.token = token
        self.checkid = checkid
        self.customerid = customerid

    def all_checks(self):
        """ Gets all checks that exist for the account

        Makes a request to NodePing with the supplied API key.
        Returns all check information in a dictionary format.

        Must provide the account's API token and optionally the
        customerid to output subaccount checks
        """

        url = _utils.create_url(self.token, API_URL, self.customerid)

        return _query_nodeping_api.get(url)

    def passing_checks(self):
        """ Gets all checks that are passing for the account

        Makes a request to NodePing with the supplied API key.
        Collects all checks for the account and removes all checks
        with a state of 0 which means the check is failing.
        """

        passing_checks = {}

        url = _utils.create_url(self.token, API_URL, self.customerid)

        all_checks_dictionary = _query_nodeping_api.get(url)

        for check_id, contents in all_checks_dictionary.items():
            try:
                state = contents['state']
            except KeyError:
                state = 0

            if state == 1:
                passing_checks.update({check_id: contents})

        return passing_checks

    def failing_checks(self):
        """ Gets all checks for the account that are failing

        Makes a request to NodePing with the supplied API key.
        Queries NodePing for current failing checks.

        *NOTE* this will also include disabled checks
        """

        failing_checks = {}

        url = _utils.create_url(self.token, API_URL, self.customerid)

        all_checks_dictionary = _query_nodeping_api.get(url)

        for check_id, contents in all_checks_dictionary.items():
            try:
                state = contents['state']
            except KeyError:
                state = 2

            if state == 0:
                failing_checks.update({check_id: contents})

        return failing_checks

    def get_by_id(self):
        """ Collects the check based on its ID

        Expects a valid check ID and API token. Collects all
        checks from NodePing and looks for the check with the
        specified ID. Returns the contents for that check
        """

        url = "{0}/{1}".format(API_URL, self.checkid)
        url = _utils.create_url(self.token, url, self.customerid)

        return _query_nodeping_api.get(url)

    def disabled_checks(self):
        """ Gets all checks for the account that are disabled

        Makes a request to NodePing with the supplied API key.
        Queries NodePing for current events for the check.
        """

        disabled_checks = {}

        url = "{0}results/current".format(config.API_URL)
        url = _utils.create_url(self.token, url, self.customerid)

        events_checks = _query_nodeping_api.get(url)

        for check_id, contents in events_checks.items():
            _type = contents['type']

            if _type == 'disabled':
                disabled_checks.update({check_id: contents})

        return disabled_checks

    def last_result(self):
        """ Get the last result for the specified check
        """

        url = "{0}/{1}?lastresult=true".format(API_URL, self.checkid)
        url = _utils.create_url(self.token, url, self.customerid)

        return _query_nodeping_api.get(url)
