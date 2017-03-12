#!/usr/bin/env python3
import sys, subprocess, time
import ernest.config, ernest.aws, utils.system, utils.crumbs

utils.system.grant_root_access()

utils.system.print_file('banners/banner.bnr')

utils.crumbs.init()

config = ernest.config.get()


######## INIT ########
if len(sys.argv) > 1:
	if utils.system.is_ip_valid(sys.argv[1]):
		instance_ip = sys.argv[1]
		utils.crumbs.log('INSTANCE', instance_ip)
		print('--> Starting Ernest on instance: ' + instance_ip + '\n')
	else:
		sys.exit('ERROR: Unknown argv')
else:
	print('--> Creating instance (this may take a while)')
	instance_ip = ernest.aws.pop_instance(config)
	utils.crumbs.log('INSTANCE', instance_ip)


print('--> Creating VPN tunnel...')
vpn_process = subprocess.Popen("./vpn.py " + instance_ip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#vpn_process = subprocess.Popen("./vpn.py " + instance_ip, shell=True)
utils.crumbs.log('PROCESS', str(vpn_process.pid))
print('    |_ Connected (pid: ' + str(vpn_process.pid) + ')\n')

print('--> Waiting for Instance OS initialization...')
ernest.aws.wait_for_os(instance_ip)

time.sleep(30)

print('--> Opening Steam Server login through RDP...')
rdp_process = subprocess.Popen("yes | xfreerdp -u " + config['rdp']['login'] + " -p " + config['rdp']['password'] + " " + instance_ip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
utils.crumbs.log('PROCESS', str(rdp_process.pid))
utils.crumbs.log('APPLICATION', 'XQuartz')
print('    |_ Connected (pid: ' + str(rdp_process.pid) + ')\n')

print('--> Waiting for Steam login (RDP window)...')
rdp_process.communicate()
print('    |_ RDP connection closed')
subprocess.call(['osascript', '-e', 'tell application "XQuartz" to quit'])
print('    |_ XQuartz terminated\n')

print('--> Launching Steam Client...')
steam_process = subprocess.Popen("open -a Steam", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


######## WAIT FOR USER ########
utils.system.print_file('banners/middle.bnr')
input('\n')


######## CLOSING ########

print('--> Disconnecting VPN tunnel...')
vpn_process.terminate()
print('    |_ Done\n')

print('--> Sending Instance kill signal...')
print('    |_ Disabled for now\n')

utils.crumbs.clear()

utils.system.print_file('banners/footer.bnr')