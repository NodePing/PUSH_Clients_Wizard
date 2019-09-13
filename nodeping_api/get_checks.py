#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


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

        # Checks to see if the API token provided is valid
        check_token.is_valid(self.token)

    def all_checks(self):
        """ Gets all checks that exist for the account

        Makes a request to NodePing with the supplied API key.
        Returns all check information in a dictionary format.

        Must provide the account's API token and optionally the
        customerid to output subaccount checks
        """

        if self.customerid:
            url = "{0}checks?token={1}&customerid={2}".format(
                API_URL, self.token, self.customerid)
        else:
            url = "{0}checks?token={1}".format(API_URL, self.token)

        return _query_nodeping_api.get(url)

    def passing_checks(self):
        """ Gets all checks that are passing for the account

        Makes a request to NodePing with the supplied API key.
        Collects all checks for the account and removes all checks
        with a state of 0 which means the check is failing.
        """

        passing_checks = {}

        if self.customerid:
            url = "{0}checks?token={1}&customerid={2}".format(
                API_URL, self.token, self.customerid)
        else:
            url = "{0}checks?token={1}".format(API_URL, self.token)

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

        if self.customerid:
            url = "{0}checks?token={1}&customerid={2}".format(
                API_URL, self.token, self.customerid)
        else:
            url = "{0}checks?token={1}".format(API_URL, self.token)

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

        url = "{0}checks/{1}?token={2}".format(API_URL,
                                               self.checkid, self.token)

        return _query_nodeping_api.get(url)

    def disabled_checks(self):
        """ Gets all checks for the account that are disabled

        Makes a request to NodePing with the supplied API key.
        Queries NodePing for current events for the check.
        """

        disabled_checks = {}

        url = "{0}results/current?token={1}".format(API_URL, self.token)

        events_checks = _query_nodeping_api.get(url)

        for check_id, contents in events_checks.items():
            _type = contents['type']

            if _type == 'disabled':
                disabled_checks.update({check_id: contents})

        return disabled_checks

    def last_result(self):

        url = "{0}checks/{1}?token={2}&lastresult=true".format(
            API_URL, self.checkid, self.token)

        return _query_nodeping_api.get(url)
