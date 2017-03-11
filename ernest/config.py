import sys, configparser

def get():
	config = configparser.ConfigParser()
	config.read_file(open('conf/defaults.cfg'))
	config.read('conf/secret.cfg')

	if config.has_section('API') and config.has_option('API', 'API_HOST'):
		api_host = config['API']['API_HOST']
		if (config.has_option('API', 'API_PORT')):
			api_port = config['API']['API_PORT']
		else:
			api_port = 80
	else:
		sys.exit('ERROR: Missing api_host entry in defaults.cfg')

	if config.has_section('Auth') and config.has_option('Auth', 'RDP_LOGIN') and config.has_option('Auth', 'RDP_PASSWORD'):
		rdp_login 		= config['Auth']['RDP_LOGIN']
		rdp_password 	= config['Auth']['RDP_PASSWORD']
	else:
		sys.exit('ERROR: Unable to get RDP credentials')

	return { 'api': { 'host': api_host, 'port': api_port }, 'rdp': { 'login': rdp_login, 'password': rdp_password } }