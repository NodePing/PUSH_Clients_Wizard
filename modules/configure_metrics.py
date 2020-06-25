#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from PyInquirer import prompt
from os.path import expanduser, isfile

field_options = {}


def _get_names_and_status(key_name, message):
    """ Gets file paths until the user asks to stop
    """

    get_names = True
    names = {}
    i = 1

    while get_names:

        questions = [
            {"type": "input", "name": "name", "message": message},
            {
                "type": "list",
                "name": "state",
                "message": "Should it be absent or present?",
                "choices": ["Present", "Absent"],
            },
            {
                "type": "confirm",
                "name": "get_another",
                "message": "Add another to the check?",
            },
        ]

        answers = prompt(questions)

        name = "{0}.{1}".format(key_name, answers["name"])
        key = "{0}{1}".format(key_name, i)

        if answers["state"] == "Present":
            names.update({key: {"name": name, "min": 1, "max": 1}})
        elif answers["state"] == "Absent":
            names.update({key: {"name": name, "min": 0, "max": 0}})

        if answers["get_another"]:
            i += 1
        else:
            break

    return names


def checkpid_metric(key_name):
    """
    """

    message = "What is the /path/to/pidfile.pid?"

    return _get_names_and_status(key_name, message)


def iocage_metric(key_name):
    """ Set names of iocage jails and the state you expect them to be in
    """

    message = "What is the name of the iocage jail?"

    return _get_names_and_status(key_name, message)


def start_metric(name):
    """ Print blocks to make metric creation easier to read
    """

    print("===== Configuring {0} =====".format(name))


def end_metric(name):
    """ Print blocks to make metric creation easier to read
    """

    print("===== {0} configuration complete =====\n".format(name))


def main(metrics, client):
    """
    """

    field_values = {}

    for metric in metrics:
        start_metric(metric)

        complete = False

        # metrics with prompts to accept user input are put here to
        # validate if the user input was correct. If not, the while loop
        # repeats and asks the user for the data for that metric again
        while not complete:

            if "cassandra" in metric:
                import modules.metrics.cassandra as cassandra

                data = cassandra.cassandra_metric("cassandra")
            elif "checkiptables" in metric:
                import modules.metrics.checkiptables as checkiptables

                data = checkiptables.checkiptables_metric("checkiptables")
            elif "checkpf_firewall" in metric:
                import modules.metrics.checkpf_firewall as pf_firewall

                data = pf_firewall.checkpf_firewall_metric("checkpf_firewall")
            elif "checksum" in metric:
                import modules.metrics.checksum as checksum

                data = checksum.checksum_metric("checksum", client=client)
            elif "cpu_utilization" in metric:
                import modules.metrics.cpu_utilization as cpu_utilization

                data = cpu_utilization.cpu_utilization_metric("cpu_utilization")
            elif "checkpid" in metric:
                data = checkpid_metric("checkpid")
            elif "drives" in metric:
                import modules.metrics.drives as drives

                data = drives.drives_metric("drives")
            elif "fileage" in metric:
                import modules.metrics.fileage as fileage

                data = fileage.fileage_metric("fileage")
            elif "iocage" in metric:
                data = iocage_metric("iocage")
            elif "memory" in metric:
                import modules.metrics.memfree as memfree

                data = memfree.memory_metric("memory")
            elif "mysqlstat" in metric:
                import modules.metrics.sqlstat as sqlstat

                data = sqlstat.sqlstat_metric("mysqlstat", client=client)
            elif "pgsqlstat" in metric:
                import modules.metrics.sqlstat as sqlstat

                data = sqlstat.sqlstat_metric("pgsqlstat")
            elif "processor" in metric:
                import modules.metrics.processor as processor

                data = processor.processor_metric("processor", client)
            elif "cpuload" in metric:
                import modules.metrics.processor as processor

                data = processor.processor_metric("cpuload", client)
            elif "zfs" in metric:
                import modules.metrics.drives as zfs

                data = zfs.zfs_metric("zfs")
            elif "diskfree" in metric:
                import modules.metrics.drives as drives

                data = drives.drives_metric("diskfree")
            elif "load" in metric:
                import modules.metrics.processor as processor

                data = processor.processor_metric("load", client)
            elif "memavail" in metric:
                import modules.metrics.memavail as memavail

                data = memavail.memavail_metric("memavail")
            elif "memfree" in metric:
                import modules.metrics.memfree as memfree

                data = memfree.memory_metric("memfree")
            elif "pingstatus" in metric:
                import modules.metrics.pingstatus as pingstatus

                data = pingstatus.pingstatus_metric("pingstatus")
            elif "httpcheck" in metric:
                import modules.metrics.httpcheck as httpcheck

                data = httpcheck.httpcheck_metric("httpcheck", client)
            elif "smartctl" in metric:
                import modules.metrics.smartctl as smartctl

                data = smartctl.smartctl_metric("smartctl")
            elif "zpool" in metric:
                import modules.metrics.zpool as zpool

                data = zpool.zpool_metric("zpool")
            else:
                break

            complete_questions = [
                {
                    "type": "confirm",
                    "name": "complete",
                    "message": "Does this information look correct",
                }
            ]

            header = "{0:<50}{1:<10}{2:<10}".format("Name", "Min", "Max")
            print("{0}\n{1}".format(header, ("-" * len(header))))

            for _key, value in data.items():
                print(
                    "{0:<50}{1:<10}{2:<10}".format(
                        value["name"], value["min"], value["max"]
                    )
                )

            print("\n")

            complete_answers = prompt(complete_questions)

            if complete_answers["complete"]:
                complete = True

        # Metrics here expect no user input and don't need to be
        # prompted for user confirmation for the data being correct
        if "apcupsd" in metric:
            import modules.metrics.apcupsd as apcupsd

            data = apcupsd.apcupsd_metric()
        elif "redismaster" in metric:
            import modules.metrics.redismaster as redismaster

            data = redismaster.redismaster_metric("redismaster")
        elif "ip_addrs" in metric:
            import modules.metrics.ip_addrs as ip_addrs

            data = ip_addrs.ip_addrs_metric()
        elif "dnslookup" in metric:
            import modules.metrics.dnslookup as dnslookup

            data = dnslookup.dnslookup_metric()
        elif "mongodbstat" in metric:
            import modules.metrics.mongodbstat as mongodbstat

            data = mongodbstat.mongodbstat_metric()

        end_metric(metric)

        field_values.update(data)

    return field_values
