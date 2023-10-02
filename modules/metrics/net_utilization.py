#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from os.path import join
from InquirerPy import prompt
from modules import _utils


def net_utilization_metric(key_name):
    """ Get info for alerting on interface tx/rx values
    """

    get_interfaces = True
    interfaces = {}
    i = 1

    while get_interfaces:

        questions = [
            {
                "type": "input",
                "name": "name",
                "message": "What is the name of the interface (e.g. eth0)?",
            },
            {
                "type": "input",
                "name": "min_rx_percent",
                "message": "What is the minimum % of received bandwidth usage you want to be alerted at?",
            },
            {
                "type": "input",
                "name": "max_rx_percent",
                "message": "What is the maximum % of received bandwidth usage you want to be alerted at?",
            },
            {
                "type": "input",
                "name": "min_tx_percent",
                "message": "What is the minimum % of transferred bandwidth usage you want to be alerted at?",
            },
            {
                "type": "input",
                "name": "max_tx_percent",
                "message": "What is the maximum % of transferred bandwidth usage you want to be alerted at?",
            },
            {
                "type": "confirm",
                "name": "get_bytes",
                "message": "Do you also want to monitor transferred/received bytes?",
            },
            {
                "type": "input",
                "name": "min_rx_bytes",
                "message": "What is the minimum expected received bytes?",
                "when": lambda answers: answers["get_bytes"] is True,
            },
            {
                "type": "input",
                "name": "max_rx_bytes",
                "message": "What is the maximum expected received bytes?",
                "when": lambda answers: answers["get_bytes"] is True,
            },
            {
                "type": "input",
                "name": "min_tx_bytes",
                "message": "What is the minimum expected transferred bytes?",
                "when": lambda answers: answers["get_bytes"] is True,
            },
            {
                "type": "input",
                "name": "max_tx_bytes",
                "message": "What is the maximum expected transferred bytes?",
                "when": lambda answers: answers["get_bytes"] is True,
            },
            {
                "type": "confirm",
                "name": "get_interfaces",
                "message": "Add another interface?",
            },
        ]

        answers = prompt(questions)

        get_interfaces = answers["get_interfaces"]

        name = "{0}.{1}".format(key_name, answers["name"])
        rx_percent_min = answers["min_rx_percent"]
        rx_percent_max = answers["max_rx_percent"]
        tx_percent_min = answers["min_tx_percent"]
        tx_percent_max = answers["max_tx_percent"]

        interfaces.update(
            {
                "{0}{1}".format(key_name, i): {
                    "name": "{0}.rx_percent".format(name),
                    "min": rx_percent_min,
                    "max": rx_percent_max,
                }
            }
        )

        i += 1

        interfaces.update(
            {
                "{0}{1}".format(key_name, i): {
                    "name": "{0}.tx_percent".format(name),
                    "min": tx_percent_min,
                    "max": tx_percent_max,
                }
            }
        )

        i += 1

        if answers["get_bytes"]:
            min_rx_bytes = answers["min_rx_bytes"]
            max_rx_bytes = answers["max_rx_bytes"]
            min_tx_bytes = answers["min_tx_bytes"]
            max_tx_bytes = answers["max_tx_bytes"]

            interfaces.update(
                {
                    "{0}{1}".format(key_name, i): {
                        "name": "{0}.rx_bytes".format(name),
                        "min": min_rx_bytes,
                        "max": max_rx_bytes,
                    }
                }
            )

            i += 1

            interfaces.update(
                {
                    "{0}{1}".format(key_name, i): {
                        "name": "{0}.tx_bytes".format(name),
                        "min": min_tx_bytes,
                        "max": max_tx_bytes,
                    }
                }
            )

            i += 1

    return interfaces


def configure_net_utilization(keys, all_metrics, archive_dir, client):
    """ Puts the net_utilization info in the necessary config files
    """

    # keys
    # ['net_utilization1', 'net_utilization2']
    # all_metrics
    #    {'net_utilization1': {'max': '100',
    #                      'min': '0',
    #                      'name': 'net_utilization.em0.rx_percent'},
    # 'net_utilization2': {'max': '90',
    #                      'min': '10',
    #                      'name': 'net_utilization.em0.tx_percent'}}

    _utils.seperator()
    print("\n=====Configuring the net utilization metric=====")

    interfaces = []

    for key in keys:
        data = all_metrics[key]
        interface = data["name"].split(".")[1]

        interfaces.append(interface)

    interfaces = list(set(interfaces))

    questions = [
        {
            "type": "confirm",
            "name": "EachPush",
            "message": "Do you want to calculate all the bandwidth that has been used in between each PUSH interval?",
        },
        {
            "type": "input",
            "name": "SleepInterval",
            "message": "How many seconds do you want this to collect bandwidth stats on?",
        },
        {
            "type": "input",
            "name": "ExpectedNetUtilizationRX",
            "message": "Max Mbps you expect to be received/downloaded",
        },
        {
            "type": "input",
            "name": "ExpectedNetUtilizationTX",
            "message": "Minimum Mbts you expect to be sent/uploaded",
        },
    ]

    answers = _utils.confirm_choice(questions)

    if client == "POSIX":
        net_utilization_dir = "{0}/POSIX/NodePingPUSHClient/modules/net_utilization".format(
            archive_dir
        )
        vars_file = join(net_utilization_dir, "variables.sh")

        with open(vars_file, "r", newline="\n") as f:
            filedata = f.read()

        filedata = filedata.replace(
            'each_push="true"', 'each_push="%s"' % str(answers["EachPush"]).lower()
        )

        filedata = filedata.replace(
            "sleep_interval=60", "sleep_interval=%s" % answers["SleepInterval"]
        )

        filedata = filedata.replace(
            'interfaces="eth0 eth1"', 'interfaces="%s"' % " ".join(interfaces)
        )

        filedata = filedata.replace(
            "expected_net_utilization_rx=100",
            "expected_net_utilization_rx=%s" % str(answers["ExpectedNetUtilizationRX"]),
        )

        filedata = filedata.replace(
            "expected_net_utilization_tx=10",
            "expected_net_utilization_tx=%s" % str(answers["ExpectedNetUtilizationTX"]),
        )

        with open(vars_file, "w", newline="\n") as f:
            f.write(filedata)

    elif client == "PowerShell":
        net_utilization_dir = "{0}/{1}/NodePing{1}PUSH/modules/net_utilization".format(
            archive_dir, client
        )
        
        # Add interfaces to the answers dictionary
        answers.update({"interfaces": interfaces})

        net_utilization_file = join(net_utilization_dir, "net_utilization.json")

        open(net_utilization_file, "w").close()

        with open(net_utilization_file, "w") as f:
            f.write(json.dumps(answers, indent=8, sort_keys=True))
