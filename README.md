# PUSH Clients Wizard

> User guide on using the PUSH client wizard

## Getting Started

The PUSH Client Wizard is a command line interface tool that lets you
easily manage PUSH checks with NodePing. The tool currently lets you:

  - Create checks

  - List checks

  - Delete checks

The tool currently works on all operating systems that run Python 3.

### Requirements

Requirements to use this tool:

1.  Python 3.5+

2.  Paramiko

3.  PyInquirer

**NOTE**

Paramiko has limitations in which SSH keys are accepted. If you do not use
one of its supported SSH key types, you will either have to copy files
by authenticating with an SSH password or remote copying the files later.

Supported key types:

- dsskey

- rsakey

- ecdsakey

- ed25519key

Paramiko and PyInquirer can be installed via pip or your OS’s package
manager.

For example with pip to install dependencies under your user account:

    $ pip3 install --user PyInquirer paramiko
    $ python3 -m pip install --user PyInquirer paramiko

### Setting Up

Download this program and its contents to a diretory you wish to run
from. You will need to get your API key for NodePing. Place the API
token in the config.ini file where it says `token =`

``` python
[main]
token = your-token-here
```

You can either place the token there or the program will prompt you to
supply it.

### Usage

To run the program, open a command line or PowerShell and call start the
program by running `python3 app.py` from the directory of the program.

You will be prompted to either list checks, create checks,
delete checks, or exit the program.

#### Listing Checks

This will query NodePing for your existing PUSH checks and you will be
asked to list all checks or one at a time until you wish to stop.

#### Creating Checks

Here you are asked multiple things to setup a check

  - Information about the check (such as the name, interval it will run,
    etc)

  - The client you will be using (POSIX, PowerShell, Python, Python3)

  - The metrics you will be checking

  - Data about each metric that will be used to Pass/Fail the check

  - Your contacts that will be alerted if the check fails
  
  - If you wish to configure the client or not

  - Where to save the client to (whether remote or local)

  - Information to set up the metric for the PUSH client

  - If the client will be set up remotely: your ssh login info
  
> **Note**
> 
> When configuring some metrics, it will confirm the information that
> you entered. The information displayed will be what shows up on
> NodePing. For other values that are previously entered (such as
> checksums), values you entered will still be visible to you to
> confirm.

Once the process is done, the check will be configured with NodePing,
and, if you accepted to setting up the client, the client will be
configured and set in your designated location. You will also be provided
with a cron job you can enter if you set the client up to run on a *NIX
system.

If you chose to install the client on Windows, the commands to run are output
to console. In addition, a .ps1 script is also created in the directory
this program is running from and you can optionally run that instead of
copying/pasting lines to set up a Task Scheduler event. Please note,
these commands have to be run as an administrator to set up the event.


#### Deleting Checks

This will query NodePing for your existing PUSH checks and you will be
shown a checklist of your existing PUSH checks which you can select to
delete.

