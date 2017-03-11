#!/usr/bin/env python3
import http.client, urllib.parse, time, re, sys, os, configparser, subprocess, json

euid = os.geteuid()
if euid != 0:
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    # the next line replaces the currently-running process with the sudo
    os.execlpe('sudo', *args)

with open('banners/banner.bnr', 'r') as banner:
    print(banner.read())

crumbs_file_name = time.strftime("%y%m%d%H%M%S") + ".crmb"

# file.write(“This is a test”) 
# file.write(“To add more lines.”)

# file.close()

config = configparser.ConfigParser()
config.read_file(open('conf/defaults.cfg'))
config.read('conf/secret.cfg')

if config.has_section('API') and config.has_option('API', 'API_HOST'):
	api_host = config['API']['API_HOST']
else:
	sys.exit('ERROR: Missing api_host entry in defaults.cfg')

if config.has_section('Auth') and config.has_option('Auth', 'RDP_LOGIN') and config.has_option('Auth', 'RDP_PASSWORD'):
	rdp_login 		= config['Auth']['RDP_LOGIN']
	rdp_password 	= config['Auth']['RDP_PASSWORD']
else:
	sys.exit('ERROR: Unable to get RDP credentials')

if config.has_section('Auth') and config.has_option('Auth', 'STEAM_LOGIN') and config.has_option('Auth', 'STEAM_PASSWORD'):
	steam_login 		= config['Auth']['STEAM_LOGIN']
	steam_password 	= config['Auth']['STEAM_PASSWORD']
else:
	sys.exit('ERROR: Unable to get Steam credentials')

# Checking Instance IP
ip_pattern = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
if len(sys.argv) > 1 and ip_pattern.match(sys.argv[1]):
	instance_ip = sys.argv[1]
	with open("crumbs/" + crumbs_file_name, "a") as crumbs: crumbs.write("INSTANCE=" + instance_ip + "\n");
	print('--> Starting Ernest on instance: ' + instance_ip + '\n')
else:
	print('--> Creating instance (this may take a while)')
	#sys.exit("\n/!\ Client side instance creation is disabled for now./!\ \nTo launch Ernest on an existing instance, type: ./ErnestClient.py <instance_ip>\n")

	#instance_ip = '52.19.91.72'

	#time.sleep(2)

	print('    |_ Step 1 of 3 - Instance requesting...')
	conn = http.client.HTTPConnection(api_host, 5000)
	conn.request("POST", "/spot_instance_requests")
	json_res = json.loads(conn.getresponse().read().decode('UTF-8'))
	status = 'undefined'

	request_id_pattern = re.compile("^sir\-[a-z0-9]{8}$")
	if 'SpotInstanceRequestId' in json_res and request_id_pattern.match(json_res['SpotInstanceRequestId']):
		request_id = json_res['SpotInstanceRequestId']

		print('    |_ Step 2 of 3 - Waiting for request validation...')
		while status not in ['price-too-low', 'fulfilled']:
			time.sleep(1)
			conn.request("GET", "/spot_instance_requests/" + request_id)
			json_res = json.loads(conn.getresponse().read().decode('UTF-8'))
			if 'Status' in json_res and 'Code' in json_res['Status']:
				status = json_res['Status']['Code']
	else:
		conn.close()
		sys.exit('ERROR: Unable to start instance (Unknown error)')

	if status == 'price-too-low':
		conn.close()
		sys.exit('ERROR: Unable to start instance (bid price too high)')
	elif status != 'fulfilled':
		conn.close()
		sys.exit('ERROR: Unable to start instance (Unknown error)')

	print('    |_ Step 3 of 3 - Request approved, instance starting...')
	instance_id = json_res['InstanceId']
	state = 'undefined'
	while state not in ['running']:
		time.sleep(1)
		conn.request("GET", "/instances/" + instance_id)
		json_res = json.loads(conn.getresponse().read().decode('UTF-8'))
		if 'State' in json_res and 'Name' in json_res['State']:
			state = json_res['State']['Name']

	if state != 'running':
		conn.close()
		sys.exit('ERROR: Unable to start instance (Unknown error)')

	if 'PublicIpAddress' in json_res and ip_pattern.match(json_res['PublicIpAddress']):
		instance_ip = json_res['PublicIpAddress']
		with open("crumbs/" + crumbs_file_name, "a") as crumbs: crumbs.write("INSTANCE=" + instance_ip + "\n");
		print('    |_ Done (Instance IP: ' + instance_ip + ')\n')
	else:
		conn.close()
		sys.exit('ERROR: Unable to start instance (Invalid IP)')

	conn.close()

# print('--> Sending Steam login query...')
# print('    |_ Disabled for now\n')

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
with open("crumbs/" + crumbs_file_name, "a") as crumbs: crumbs.write("PROCESS=" + str(vpn_process.pid) + "\n");
print('    |_ Connected (pid: ' + str(vpn_process.pid) + ')\n')

print('--> Waiting for Instance OS initialization...')
response = 1
while response != 0:
	time.sleep(1)
	response = os.system('ping -c 1 10.8.0.1 > /dev/null 2>&1')
print('    |_ Instance initialization completed\n')

print('--> Opening Steam Server login through RDP...')
rdp_process = subprocess.Popen("xfreerdp -u " + rdp_login + " -p " + rdp_password + " " + instance_ip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
with open("crumbs/" + crumbs_file_name, "a") as crumbs: crumbs.write("PROCESS=" + str(rdp_process.pid) + "\n");
print('    |_ Connected (pid: ' + str(rdp_process.pid) + ')\n')

print('--> Waiting for Steam login (RDP window)...')
rdp_process.communicate()
print('    |_ RDP connection closed')
subprocess.call(['osascript', '-e', 'tell application "XQuartz" to quit'])
print('    |_ XQuartz terminated\n')

print('--> Launching Steam Client...')
steam_process = subprocess.Popen("open -a Steam", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

with open('banners/middle.bnr', 'r') as middle:
    print(middle.read())
input('\n')

print('--> Disconnecting VPN tunnel...')
vpn_process.terminate()
print('    |_ Done\n')

print('--> Sending Instance kill signal...')
print('    |_ Disabled for now\n')

os.remove("crumbs/" + crumbs_file_name)

with open('banners/footer.bnr', 'r') as footer:
    print(footer.read())