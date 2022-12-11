import os
import subprocess

def deflog():
    if os.name == 'posix':
        os.command('kali')
        test = subprocess.check_output("kali", shell=True)
        if test == "Login incorrect":
            os.command('msfadmin')
            os.command('msfadmin')

