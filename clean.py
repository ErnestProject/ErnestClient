#!/usr/bin/env python3
import sys, os, signal, subprocess, psutil

euid = os.geteuid()
if euid != 0:
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    # the next line replaces the currently-running process with the sudo
    os.execlpe('sudo', *args)

for (dirpath, _, filenames) in os.walk('crumbs'):
	for filename in filenames:
		filepath = dirpath + "/" + filename
		print("-> Parsing file: " + filepath)
		with open(filepath, 'r') as crumbfile:
			content = crumbfile.read().splitlines()
			for line in content:
				sline = line.split('=')
				if len(sline) == 2:
					if sline[0] == 'INSTANCE':
						print("    |_ Killing instance " + sline[1])
					elif sline[0] == 'APPLICATION':
						print("    |_ Closing application " + sline[1])
						subprocess.call(['osascript', '-e', 'tell application "' + sline[1] + '" to quit'])
						print("        |_ Application closed")
					elif sline[0] == 'PROCESS':
						print("    |_ Killing process " + sline[1])
						try:
							os.kill(int(sline[1]), signal.SIGKILL)
							print("        |_ Process killed")
						except Exception as e:
							print("        |_ No such process")
					else:
						print("    |_ Unknown instruction. Skipped.")
				else:
					print("    |_ Unknown instruction. Skipped.")
			print('\n\n')
		os.remove(filepath)

if len(sys.argv) > 1 and '--hard' in sys.argv:
	print("-------- HARD MODE --------")
	print("-> Killing all openvpn processes")
	for proc in psutil.process_iter():
		if proc.name() == 'openvpn':
			proc.kill()
