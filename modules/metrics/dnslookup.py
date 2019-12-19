#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join
from PyInquirer import prompt
from modules import _utils


def dnslookup_metric():
    """ Sets the minimum and maximum for dnslookup to be only 1 for passing

    """
    dnslookup_fields = {
        'dnslookup': {
            'name': 'dnslookup',
            'min': 1,
            'max': 1
        }
    }

    return dnslookup_fields


def configure_dnslookup(archive_dir, client):
    """ Sets up the client configuration for dnslookup metric

    Asks user for the information to perform a DNS query, such as
    the server to query, query, expected result, and record type
    """

    _utils.seperator()
    print("\n=====Configuring the dnslookup metric=====")

    # False if the user is still adding information. This will be true if
    # the user says the info they input is correct
    complete = False

    while not complete:
        check_questions = [
            {
                'type': 'input',
                'name': 'dns_ip',
                'message': 'IP address of the DNS server to query (optional)'
            },
            {
                'type': 'input',
                'name': 'to_resolve',
                'message': 'Hostname or IP to resolve'
            },
            {
                'type': 'input',
                'name': 'record_type',
                'message': 'Record type to query (A, AAAA, CNAME, etc.)'
            }
        ]

        dns_answers = prompt(check_questions)

        dns_results = []

        # Remains true if the user is still adding IPs that are expected
        # as output from DNS query
        adding_ips = True

        while adding_ips:
            result_questions = [
                {
                    'type': 'input',
                    'name': 'output',
                    'message': 'Expected output'
                },
                {
                    'type': 'confirm',
                    'name': 'adding_ips',
                    'message': 'Are there other expected results from the query?'
                }
            ]

            result_answers = prompt(result_questions)

            dns_results.append(result_answers['output'])
            adding_ips = result_answers['adding_ips']

        print("DNS Server IP: %s" % dns_answers['dns_ip'])
        print("FQDN/IP to resolve: %s" % dns_answers['to_resolve'])
        print("Query type: %s" % dns_answers['record_type'])
        print("Expected results: %s " % str(dns_results))

        complete = _utils.inquirer_confirm("Are these IP addresses correct?")

    if client == 'POSIX':
        dnslookup_dir = "{0}/POSIX/NodePingPUSHClient/modules/dnslookup".format(
            archive_dir)
        vars_file = join(dnslookup_dir, "variables.sh")

        results = ' '.join(dns_results)

        with open(vars_file, 'w', newline='\n') as f:
            f.write("# DNS server IP to query\n")
            f.write("dns_ip='{0}'\n".format(dns_answers['dns_ip']))

            f.write("\n# Hostname to resolve\n")
            f.write("to_resolve='{0}'\n".format(dns_answers['to_resolve']))

            f.write("\n# Expected IP or hostname as output.\n")
            f.write("expected_output='{0}'\n".format(results))

            f.write("record_type='{0}'".format(dns_answers['record_type']))
    elif client in ("Python", "Python3"):
        dnslookup_dir = "{0}/{1}/NodePing{1}PUSH/metrics/dnslookup".format(
            archive_dir, client)

        dnslookup_file = join(dnslookup_dir, "config.py")

        with open(dnslookup_file, 'r', newline='\n') as f:
            filedata = f.read()

        filedata = filedata.replace('dns_ip = "64.34.204.155"',
                                    'dns_ip = "%s"' % dns_answers['dns_ip'])
        filedata = filedata.replace('to_resolve = "nodeping.com"',
                                    'to_resolve = "%s"' % dns_answers['to_resolve'])
        filedata = filedata.replace('expected_output = "167.114.101.137"',
                                    'expected_output = %s' % str(dns_results))
        filedata = filedata.replace('query_type = "A"',
                                    'query_type = "%s"' % dns_answers['record_type'])

        with open(dnslookup_file, 'w', newline='\n') as f:
            f.write(filedata)
