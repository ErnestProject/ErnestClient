#!/usr/bin/env python3
import http.client, urllib.parse, time, re, sys, os, configparser, subprocess

euid = os.geteuid()
if euid != 0:
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    # the next line replaces the currently-running process with the sudo
    os.execlpe('sudo', *args)

with open('banner.bnr', 'r') as banner:
    print(banner.read())

# Checking Instance IP
ip_pattern = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
if len(sys.argv) > 1 and ip_pattern.match(sys.argv[1]):
	instance_ip = sys.argv[1]
else:
	instance_ip = None

config = configparser.ConfigParser()
config.read_file(open('conf/defaults.cfg'))
config.read('conf/secret.cfg')

if config.has_section('Auth') and config.has_option('Auth', 'STEAM_LOGIN') and config.has_option('Auth', 'STEAM_PASSWORD'):
	steam_login 		= config['Auth']['STEAM_LOGIN']
	steam_password 	= config['Auth']['STEAM_PASSWORD']
else:
	sys.exit('ERROR: Unable to get Steam credentials')

if config.has_section('API') and config.has_option('API', 'API_HOST'):
	api_host = config['API']['API_HOST']
else:
	sys.exit('ERROR: Missing api_host entry in defaults.cfg')


if instance_ip is None:
	print('--> Creating instance...')
	sys.exit("\n/!\ Client side instance creation is disabled for now./!\ \nTo launch Ernest on an existing instance, type: ./ErnestClient.py <instance_ip>\n")

	instance_ip = '52.19.91.72'

	time.sleep(2)
	# conn = http.client.HTTPConnection("localhost", 5000)
	# conn.request("POST", "/instances")
	# res = conn.getresponse()
	# instance_ip = res.read().decode('UTF-8')
	# conn.close()

	ipPattern = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
	if ipPattern.match(instance_ip):
		print('    |_ Done (Instance IP: ' + instance_ip + ')\n')
	else:
		sys.exit('ERROR: Unable to start instance')

else:
	print('--> Starting Ernest on instance: ' + instance_ip + '\n')

print('--> Sending Steam login query...')
print('    |_ Disabled for now\n')

# params = urllib.parse.urlencode({'iip': instance_ip, 'l': steam_login, 'p': steam_password})
# headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
# conn = http.client.HTTPConnection(api_host)
# conn.request("POST", "/test/request_login.php", params, headers)
# res = conn.getresponse()
# sRes = res.read().decode('UTF-8')
# conn.close()

# if sRes == "Steam is starting. Please wait...":
# 	print('   |_ Sent (account: ' + steam_login + ')\n')
# else:
# 	sys.exit('ERROR: Login action failed')


print('--> Creating VPN tunnel...')
vpn_process = subprocess.Popen("./vpn.py " + instance_ip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#vpn_process = subprocess.Popen("./vpn.py " + instance_ip, shell=True)
print('    |_ Connected (pid: ' + str(vpn_process.pid) + ')\n')

print('--> Launching Steam Client...')
steam_process = subprocess.Popen("open -a Steam", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

with open('middle.bnr', 'r') as middle:
    print(middle.read())
input('\n')
print(' ')

print('--> Disconnecting VPN tunnel...')
vpn_process.terminate()
print('    |_ Done\n')

print('--> Sending Instance kill signal...')
print('    |_ Disabled for now\n')

with open('footer.bnr', 'r') as footer:
    print(footer.read())