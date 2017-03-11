import os, time

def init():
	global crumbs_file_name
	crumbs_file_name = time.strftime("%y%m%d%H%M%S") + ".crmb"

	if not os.path.exists('crumbs'):
		os.makedirs('crumbs')

def log(type, value):
	with open("crumbs/" + crumbs_file_name, "a") as crumbs: crumbs.write(type + '=' + value + "\n");

def clear():
	os.remove("crumbs/" + crumbs_file_name)
