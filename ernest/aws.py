import os, http.client, json, re, time
import utils.system

def wait_for_os(instance_ip):
	res = 1
	while res != 0:
		time.sleep(1)
		res = os.system('ping -c 1 10.8.0.1 > /dev/null 2>&1')
	print('    |_ Instance initialization completed\n')

def pop_instance(config):
	print('    |_ Step 1 of 3 - Instance requesting...')
	conn = http.client.HTTPConnection(config['api']['host'], config['api']['port'])
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
		sys.exit('ERROR: Unable to start instance (bid price too low)')
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

	if 'PublicIpAddress' in json_res and utils.system.is_ip_valid(json_res['PublicIpAddress']):
		instance_ip = json_res['PublicIpAddress']
		print('    |_ Done (Instance IP: ' + instance_ip + ')\n')
	else:
		conn.close()
		sys.exit('ERROR: Unable to start instance (Invalid IP)')

	conn.close()

	return instance_ip