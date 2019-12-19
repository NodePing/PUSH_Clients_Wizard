#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join


def configure_checkpid(keys, all_metrics, archive_dir, client):
    """ Puts the checkpid metric info in its necessary config file

    Accepts the keys that are generated in the configure_metrics py file
    and the whole output from that. Sorts through the keys and grabs the data
    and stores variables in a format that the language reads.
    """

    print("\n=====Configuring the checkpid metric=====")

    filenames = []

    for key in keys:
        data = all_metrics[key]
        filename = '.'.join(data['name'].split('.')[1:])

        filenames.append(filename)

    if client == "POSIX":
        checkpid_dir = "{0}/POSIX/NodePingPUSHClient/modules/checkpid".format(
            archive_dir)
        checkpid_file = join(checkpid_dir, "checkpid.txt")

        # Clear contents of checkpid.txt file
        open(checkpid_file, 'w').close()

        with open(checkpid_file, 'a', newline='\n') as f:
            for pidfile in filenames:
                f.write("%s\n" % pidfile)

    elif client == "Python" or client == "Python3":
        checkpid_dir = "{0}/{1}/NodePing{1}PUSH/metrics/checkpid".format(
            archive_dir, client)

        checkpid_file = join(checkpid_dir, "config.py")

        # Clear contents of config.py file
        open(checkpid_file, 'w').close()

        with open(checkpid_file, 'w', newline='\n') as f:
            f.write("PIDFILES = ")
            f.write(str(filenames))

    elif client == "PowerShell":
        pass
