#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import check_token, _query_nodeping_api, config

API_URL = config.API_URL


def get_results(token,
                check_id,
                customerid=None,
                span=None,
                limit=300,
                start=None,
                end=None,
                clean=True):
    """ Get results for a certain check ID.


    _id - ID of the result record.
    ci - customer id
    t - Check Type: DNS, FTP, HTTP, HTTPCONTENT, IMAP4, MYSQL, PING, POP3,
        PORT, RDP, SMTP, SSH, SSL
    tg - Target, generally the URL or Hostname
    th - Threshold or timeout for this check
    i - Check interval
    ra - Timestamp, when this check was scheduled to run
    q - Internal informationa about what queue this check was in when it ran.
    s - Timestamp, when this check actually ran. This will usually be a few ms
        behind ra
    sc - Short text field showing the result of the check. This varies slighly
         by check type. For HTTP checks, it is the status code returned by the
         remote server.
    m - Message regarding the result of the check. This varies by check type,
        but generally if there is an error code it will appear in this field.
    su - boolean, whether the check was a pass or fail
    rt - The run time. This is the value that get's charted. For many checks
         this is the value of e - s.
    e - Timestamp, when the check finished.
    l - list of locations the check ran in, and the timestamps for each.

    :param token: NodePing API token
    :type token: str
    :param check_id: The ID of the check to get results for
    :type check_id: str
    :param customerid: (Optional) subaccount ID
    :type customerid: str
    :param span: number of hours of results to retrieve
    :type span: int
    :param limit: Limit the nubmer of records to be retrieved
    :type limit: int
    :param start: Date/time for the start of the results. Timestamps in milliseconds
    :type start: int
    :param end: Date/time for the end of the results. Timestanps in milliseconds
    :type end: int
    :param clean: Clean being set to true will use the new output format above
    :type clean: bool
    :return: Returns the output that was queried from NodePing
    :rtype: dict
    """

    check_token.is_valid(token)

    parameters = locals()
    url = "{0}results/{1}?token={2}".format(API_URL, check_id, token)

    for key, value in parameters.items():
        if key in ("token", "check_id"):
            continue
        elif value:
            url = "{0}&{1}={2}".format(url, key, value)

    return _query_nodeping_api.get(url)


def get_uptime(token,
               check_id,
               customerid=None,
               interval="months",
               start=None,
               end="now"):
    """ Retrieves uptime information for a check

    :param token: NodePing API token
    :type token: str
    :param check_id: The ID of the check to get results for
    :type check_id: str
    :param customerid: (Optional) subaccount ID
    :type customerid: str
    :param interval: "days" or "months" for uptimes result for check
    :type interval: str
    :param start: optional start date for the range of days or months
    :type start: str
    :param end: optional end date for the range of days or months
    :type end: str
    :return: Uptime for checks up to the specified end date
    :rtype: dict
    """

    check_token.is_valid(token)

    parameters = locals()
    url = "{0}results/uptime/{1}?token={2}".format(API_URL, check_id, token)

    for key, value in parameters.items():
        if key in ("token", "check_id"):
            continue
        elif value:
            url = "{0}&{1}={2}".format(url, key, value)

    return _query_nodeping_api.get(url)


def get_current(token, customerid=None):
    """ Retrieves information about current "events" for checks"
    Not to be confused with listing checks that are passing/failing.
    For passing/failing, use get_checks.failing_checks or
    get_checks.passing_checks

    :param token: NodePing API token
    :type token: str
    :param customerid: (Optional) subaccount ID
    :type customerid: str
    :return: Information about current events for checks on account
    :rtype: dict
    """

    check_token.is_valid(token)

    if customerid:
        url = "{0}results/current?token={1}&customerid={2}".format(
            API_URL, token, customerid)
    else:
        url = "{0}results/current?token={1}".format(API_URL, token)

    return _query_nodeping_api.get(url)
