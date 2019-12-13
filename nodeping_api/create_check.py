#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module for creating NodePing checks
"""

from . import _query_nodeping_api, _utils, config

API_URL = "{0}checks".format(config.API_URL)

DEFAULTS = {
    'interval': 15,
    'enabled': False,
    'public': False,
    'runlocations': None,
    'homeloc': False,
    'ipv6': False,
    'threshold': 5,
    'sens': 2
}


def _package_variables(variables, check_type):
    """ Removes token and customer id and adds check type to dict data

    Removes the token from the dictionary that will be sent to NodePing
    in JSON format as well as the customer id since these aren't a part
    of the check data. Also adds the check type.

    :type variables: dict
    :param variables: Parameters that were passed in to the previous function
    :type check_type: string
    :param check_type: The type of NodePing check that will be created
    :return: Variables that will be posted to NodePing
    :rtype: dict
    """
    variables.update({'type': check_type})
    variables.pop('token')
    variables.pop('customerid')
    variables.pop('kwargs')

    return variables


def audio_check(
        token,
        target,
        customerid=None,
        label="",
        verifyvolume=False,
        volumemin=-45,
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing AUDIO check

    Expects a token and target variable. The rest are optional
    and are configured to match the NodePing defaults as described
    in the documentation.

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :param verifyvolume: enable/disable volume detection
    :type verifyvolume: bool
    :param volumemin: The acceptable range for volume detection
    :type volumemin: int
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'AUDIO')
    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def cluster_check(
        token,
        data,
        customerid="",
        label="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing Cluster check. Allows you to have a
    check pass/fail based on the status of other checks. Data is
    expected to be a dictionary with a key "data" and values being
    the ID of checks for the cluster with values of 1 or 0 for pass
    or fail.

    Example dictionary:
        checks = {
        "data": {
        "201205050153W2Q4C-0J2HSIRF": "1",
        "201205050153W2Q4C-4RZT8MLN": "1",
        "201205050153W2Q4C-IOPPFQOT": "1"
        }
        }

    :type token: string
    :param token: NodePing account API token
    :type data: dict
    :param data: List of checks associated with the cluster
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of check that will be created
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'CLUSTER')
    data = check_variables['data']['data']
    check_variables['data'] = data

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def dns_check(
        token,
        target="",
        customerid="",
        port=53,
        transport='udp',
        dnstype='A',
        dnsrd=1,
        contentstring="",
        dnstoresolve="",
        label="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        verify=False,
        **kwargs
):
    """ Creates a NodePing DNS check

    :type token: string
    :param token: NodePing account API token
    :type target: str
    :param target: URL of host to monitor
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type port: int
    :param port: Port for DNS server to query
    :type transport: str
    :param transport: UDP/TCP for DNS query
    :type dnstype: str
    :param dnstype: Type of DNS record to query
    :type dnsrd: int
    :param dnsrd: Recursion desired. 1 for True, 0 for False
    :type contentstring: str
    :param contentstring: What you expect the response to be when resolved
    :type dnstoresolve: str
    :param dnstoresolve: FQDN/IP you want to resolve
    :type label: string
    :param label: Name of check that will be created
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :type verify: bool
    :param verify: If True will authenticate using DNSSEC
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'DNS')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def ftp_check(
        token,
        target,
        customerid="",
        label="",
        port=21,
        username="",
        password="",
        invert=False,
        contentstring="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing FTP check

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type port: int
    :param port: Port to FTP server
    :type username: string
    :param username: Username to test FTP connection
    :type password: string
    :param password: Password for user to test FTP connection
    :type invert: bool
    :param invert: Whether you expect the file to exist or not (true == exists)
    :type contentstring: string
    :param contentstring: The name of the file on the ftp server
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'FTP')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def http_check(
        token,
        target,
        customerid="",
        label="",
        ipv6=False,
        follow=False,
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing HTTP check

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type ipv6: bool
    :param ipv6: Whether to resolve IPv4 or IPv6
    :type follow: bool
    :param follow: Whether to follow redirects or not
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'HTTP')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def httpadv_check(
        token,
        target,
        customerid="",
        label="",
        invert=False,
        contentstring="",
        data="",
        method="",
        postdata="",
        receiveheaders="",
        sendheaders="",
        statuscode=200,
        ipv6=False,
        follow=False,
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing HTTPADV check

    Expects a token and a target variable.

    contentstring - check to see if the content contains this string
    data/postdata - key/value pairs for POST fields
    sendheaders - key/value pairs for request headers
    receiveheaders - key/value pairs for response headers
    statuscode - HTTP status code expected in return

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type invert: bool
    :param invert: Used for "Does not contain" functionality
    :type data: dict
    :param data: key/value pair for POST fields
    :type method: string
    :param method: HTTP method
    :type postdata: dict
    :param postdata: alternative to the data object
    :type receiveheaders: dict
    :param receiveheaders: Headers that should be received
    :type sendheaders: dict
    :param sendheaders: Headers to send in request
    :type statuscode: int
    :param statuscode: HTTP status code expected in return
    :type ipv6: bool
    :param ipv6: Whether to resolve IPv4 or IPv6
    :type follow: bool
    :param follow: Whether to follow redirects or not
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'HTTPADV')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def httpcontent_check(
        token,
        target,
        customerid="",
        label="",
        invert=False,
        contentstring="",
        ipv6=False,
        follow=False,
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing HTTPCONTENT check

    Expects a token and target variable.

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type invert: bool
    :param invert: Used for "Does not contain" functionality
    :type contentstring: string
    :param contentstring: The string to match the response against
    :type ipv6: bool
    :param ipv6: Whether to resolve IPv4 or IPv6
    :type follow: bool
    :param follow: Whether to follow redirects or not
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'HTTPCONTENT')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def httpparse_check(
        token,
        target,
        customerid="",
        label="",
        fields="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing HTTPPARSE check.

    Expects a token and a target. Expects a keyed
    list of fields, with an arbitrary string as the key.
    Each object should have a name, min, and max

    Example dictionary:
        fields = {
        "fields": {
        "processmem": {
        "name": "processmem",
        "min": 1000,
        "max": 5000
        },
        "cpuload": {
        "name": "cpuload",
        "min": 1,
        "max": 5
        }
        }
        }

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type fields: dict
    :param fields: Keyed list of fields, with an arbitrary string as the key.
    Should contain 3 elements: name, min, and max
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'HTTPPARSE')
    fields = check_variables['fields']['fields']
    check_variables['fields'] = fields

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def imap4_check(
        token,
        target,
        customerid="",
        label="",
        port=143,
        verify=True,
        email="",
        username="",
        password="",
        secure=False,
        warningdays="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing IMAP4 check

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type port: int
    :param port: The port used to test IMAP4 communications
    :type verify: bool
    :param verify: The check should fail if the SSL/TLS certificate is invalid
    :type email: string
    :param email: optional string used for IMAP.
    :type username: string
    :param username: Email username for testing logins
    :type password: string
    :param password: Email for username to authenticate
    :type secure: bool
    :param secure: Whether SSL/TLS should be used
    :type warningdays: int
    :param warningdays: Warning days for expiring SSL/TLS certificate
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'IMAP4')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def mysql_check(
        token,
        target,
        customerid=None,
        label="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing MYSQL check.

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'IMAP4')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def ntp_check(
        token,
        target,
        customerid=None,
        label="",
        invert=False,
        port=123,
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing NTP check.

    Expects a token and target variable. An optional port
    value can be passed as well as "invert", where True is
    to pass if it responds, and False is to pass if it fails.

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type invert: bool
    :param invert: True means the check will pass if there is a response
    :type port: int
    :param port: Which port to query for ntp
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'NTP')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def ping_check(
        token,
        target,
        customerid=None,
        label="",
        ipv6=DEFAULTS['ipv6'],
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing PING check

    Expects a token and target variable. The rest are optional
    and are configured to match the NodePing defaults as described
    in the documentation.

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type ipv6: bool
    :param ipv6: If the ping should be icmpv6
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'PING')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def pop3_check(
        token,
        target,
        customerid=None,
        label="",
        port="",
        verify=True,
        email="",
        username="",
        password="",
        secure=False,
        warningdays="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """
    POP monitoring is an important part of an overall email availability
    monitoring strategy. The checks can not only verify that your server is
    providing POP email retrieval properly but that user logins and your
    SSL/TLS certificates are also functioning properly.

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type port: int
    :param port: The port used to test POP communications
    :type verify: bool
    :param verify: The check should fail if the SSL/TLS certificate is invalid
    :type email: string
    :param email: optional string used for POP.
    :type username: string
    :param username: Email username for testing logins
    :type password: string
    :param password: Email for username to authenticate
    :type secure: bool
    :param secure: Whether SSL/TLS should be used
    :type warningdays: int
    :param warningdays: Warning days for expiring SSL/TLS certificate
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'POP3')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def port_check(
        token,
        target,
        customerid=None,
        label="",
        invert=False,
        port="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """
    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type invert: bool
    :param invert: False if you expect to not have connections to port accepted
    :type port: int
    :param port: Port you want to attempt connections to
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'PORT')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def push_check(
        token,
        checktoken="reset",
        customerid=None,
        label="",
        fields="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        oldresultfail=False,
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing PUSH check

    Field variable will look like this:

    fields = {
    "apcupsd": {
    "name": "apcupsd",
    "min": 1,
    "max": 1
    },
    "load1min": {
    "name": "load.1min",
    "min": "0",
    "max": "4"
    },
    "load5min": {
    "name": "load.5min",
    "min": "0",
    "max": "2"
    },
    "memavail": {
    "name": "memavail",
    "min": "100",
    "max": "10000"
    }
    }

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type fields: dict
    :param fields: Contents of each metric collected with min/max values
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'PUSH')
    fields = check_variables['fields']
    check_variables['fields'] = fields

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def rbl_check(
        token,
        target,
        customerid=None,
        label="",
        ignore="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing RBL check

    Set to ignore to be a list of RBLs to ignore at
    https://nodeping.com/rbl_check.html

    Example: ignore=["zen.spamhaus.org", "dnsbl.sorbs.net"]

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type ignore: list
    :param ignore: A list of DNSBL blacklists to ignore
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'RBL')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def rdp_check(
        token,
        target,
        customerid=None,
        label="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing RDP check

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'RDP')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def spec10dns_check(
        token,
        data,
        customerid="",
        label="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing SPEC10DNS check. Allows you to have a
    check pass/fail based on the status of other DNS checks. Data is
    expected to be a dictionary with a key "data" and values being
    the ID of checks for the parent with values of 1 or 0 for pass
    or fail.

    Example dictionary:
        checks = {
        "data": {
        "201205050153W2Q4C-0J2HSIRF": "1",
        "201205050153W2Q4C-4RZT8MLN": "1",
        "201205050153W2Q4C-IOPPFQOT": "1"
        }
        }

    :type token: string
    :param token: NodePing account API token
    :type data: dict
    :param data: Dict of child DNS checks
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of check that will be created
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unnecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'SPEC10DNS')
    data = check_variables['data']['data']
    check_variables['data'] = data

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def spec10rdds_check(
        token,
        data,
        customerid="",
        label="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing SPEC10RDDS check. Allows you to have a
    check pass/fail based on the status of other WHOIS checks. Data is
    expected to be a dictionary with a key "data" and values being
    the ID of checks for the parent with values of 1 or 0 for pass
    or fail.

    Example dictionary:
        checks = {
        "data": {
        "201205050153W2Q4C-0J2HSIRF": "1",
        "201205050153W2Q4C-4RZT8MLN": "1",
        "201205050153W2Q4C-IOPPFQOT": "1"
        }
        }

    :type token: string
    :param token: NodePing account API token
    :type data: dict
    :param data: Dict of child WHOIS checks
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of check that will be created
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unnecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'SPEC10RDDS')
    data = check_variables['data']['data']
    check_variables['data'] = data

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def sip_check(
        token,
        target,
        customerid=None,
        label="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing SIP check

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'SIP')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def smtp_check(
        token,
        target,
        customerid=None,
        label="",
        invert=False,
        port=25,
        verify=True,
        email="",
        username="",
        password="",
        secure=False,
        warningdays="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing SMTP check
    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type invert: bool
    :param invert: Check whether or not SMTP accepts mail from the address
    :type port: int
    :param port: What port to run the SMTP check on
    :type verify: bool
    :param verify: Verify if the SSL/TLS certificate is valid or not
    :type email: string
    :param email: The address that will be used to test smtp connectivity for
    :type username: string
    :param username: Optional login username for testing connectivity
    :type password: string
    :param password: Password for specified username for testing connectivity
    :type secure: bool
    :param secure: Whether or not the connection should be a secure connection
    :type warningdays: int
    :param warningdays: number of warning days for an SSL/TLS cert expires
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'SMTP')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def snmp_check(
        token,
        target,
        customerid=None,
        label="",
        port=161,
        fields="",
        snmpv=1,
        snmpcom="public",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing SNMP check

    Field variable will look like this:

    fields = {
    "name1": {
    "name": "name1",
    "min": 1,
    "max": 5
    },
    "name2": {
    "name": "name2",
    "min": "0",
    "max": "4"
    },
    "name3": {
    "name": "name3",
    "min": "0",
    "max": "2"
    }
    }

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type port: int
    :param port: Port for testing SNMP connectivity
    :type fields: dict
    :param fields: OID fields for testing
    :type snmpv: int
    :param snmpv: SNMP version
    :type snmpcom: string
    :param snmpcom: SNMP community indicator
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'SNMP')
    fields = check_variables['fields']
    check_variables['fields'] = fields

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def ssh_check(
        token,
        target,
        customerid=None,
        label="",
        invert=False,
        contentstring="",
        port=22,
        username="",
        password="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing SSH check

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type contentstring: string
    :param contentstring: string to look for in the response after login
    :type port: int
    :param port: Port to test SSH connectivity on
    :type username: string
    :param username: Username to test SSH login
    :type password: string
    :param password: Password for SSH authentication
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'SSH')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def ssl_check(
        token,
        target,
        customerid=None,
        label="",
        warningdays="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing SSL check

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type warningdays: int
    :param warningdays: Number of days to warn about expiring SSL/TLS cert
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'SSL')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def websocket_check(
        token,
        target,
        customerid=None,
        label="",
        invert=False,
        contentstring="",
        data="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing WebSocket check

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type invert: bool
    :param invert: If the response does/does not contain a string
    :type contentstring: string
    :param contentstring: Contentstring that would be expected in return
    :type data: string
    :param data: string to be sent over WebSocket after connection
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'WEBSOCKET')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)


def whois_check(
        token,
        target,
        customerid=None,
        label="",
        whoisserver="",
        ipv6=False,
        invert=False,
        contentstring="",
        warningdays="",
        interval=DEFAULTS['interval'],
        enabled=DEFAULTS['enabled'],
        public=DEFAULTS['public'],
        runlocations=DEFAULTS['runlocations'],
        homeloc=DEFAULTS['homeloc'],
        threshold=DEFAULTS['threshold'],
        sens=DEFAULTS['sens'],
        dep="",
        notifications="",
        **kwargs
):
    """ Creates a NodePing whois check

    :type token: string
    :param token: NodePing account API token
    :type target: string
    :param target: URL to target host
    :type customerid: string
    :param customerid: Optional NodePing subaccount ID
    :type label: string
    :param label: Name of the check that will be created
    :type whoisserver: string
    :param whoisserver: Server to query for whois entry
    :type ipv6: bool
    :param ipv6: Whether to query the whois server over IPv6 or not
    :type invert: bool
    :param invert: Whether you expect or don't expect a string in the response
    :type contentstring: string
    :param contentstring: String to look for in the response
    :type warningdays: int
    :param warningdays: Days in advance to warn about domain expiration
    :type interval: int
    :param interval: Interval in minutes to monitor target
    :type enabled: bool
    :param enabled: If created check will be enabled or disabled
    :type public: bool
    :param public: If the results for the created check will be public or not
    :type runlocations: str
    :param runlocations: Which region to be originated from
    :type homeloc: str
    :param homeloc: Which probe in the region to originate the check from
    :type threshold: int
    :param threshold: Time in seconds for an acceptable response
    :type sens: int
    :param sens: Rechecks to help avoid unecessary notifications
    :type dep: string
    :param dep: ID of the check used for the notification dependency
    :type notifications: list
    :param notifications: list of objects containing contact ID, delay, and
    scheduling for notifications
    :return: Response from NodePing
    :rtype: dict
    """

    check_variables = _package_variables(locals(), 'WHOIS')

    url = _utils.create_url(token, API_URL, customerid)

    return _query_nodeping_api.post(url, check_variables)
