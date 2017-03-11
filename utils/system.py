import os, sys, re

def grant_root_access():
	euid = os.geteuid()
	if euid != 0:
	    args = ['sudo', sys.executable] + sys.argv + [os.environ]
	    # the next line replaces the currently-running process with the sudo
	    os.execlpe('sudo', *args)

def print_file(filepath):
	with open(filepath, 'r') as file:
		print(file.read())

def is_ip_valid(ipaddress):
	ip_pattern = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
	return ip_pattern.match(ipaddress)
