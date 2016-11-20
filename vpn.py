#!/usr/bin/env python3
import os, sys, subprocess, re, configparser, signal, fileinput
from urllib.request import urlretrieve

euid = os.geteuid()
if euid != 0:
    print("Running script as root.")
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    # the next line replaces the currently-running process with the sudo
    os.execlpe('sudo', *args)

def sighandler(signum, frame):
    print('Killing VPN process (pid: ' + str(vpn_process.pid) + ')')
    vpn_process.terminate()
    exit(0)

signal.signal(signal.SIGTERM, sighandler)

config = configparser.ConfigParser()
config.read_file(open('conf/defaults.cfg'))

ip_pattern = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
if len(sys.argv) > 1 and ip_pattern.match(sys.argv[1]):
	instance_ip = sys.argv[1]
else:
	sys.exit('ERROR: Missing instance ip parameter')

if config.has_section('Locations') \
    and config.has_option('Locations', 'VPN_BINARIES_URL') \
    and config.has_option('Locations', 'TUN_TAP_INSTALLER_URL'):
    vpn_binaries_url = config['Locations']['VPN_BINARIES_URL']
    tun_tap_installer_url = config['Locations']['TUN_TAP_INSTALLER_URL']
else:
    sys.exit('ERROR: Missing some entries in defaults.cfg file')

wd = "tmp"
vpnwd = wd + "/vpn"

# CLEARING WORKING DIR
if os.path.exists(wd):
    print("\nClearing working directory")
    subprocess.call(["rm -rf *"], shell=True, cwd=wd)
else:
    subprocess.call(["mkdir", wd])

# DOWNLOADING VPN BINARIES
print("\nDownloading OpenVPN Binaries")
print("GET " + vpn_binaries_url)
urlretrieve(vpn_binaries_url, wd + "/vpn.tar.gz")

# EXTRACTING VPN BINARIES
print("\nExtracting " + wd + "/vpn.tar.gz")
subprocess.run(["tar", "zxvf", "vpn.tar.gz"], cwd = wd)

# DOWNLOADING OpenVPN CONFIG FILE
print("\nEditing OpenVPN config file")
search_exp = "%%INSTANCE_IP%%"
for line in fileinput.input(vpnwd + "/client.ovpn", inplace=True):
    if search_exp in line:
        line = line.replace(search_exp, instance_ip)
    sys.stdout.write(line)

# CHECKING TUN/TAP INSTALL
print("\nChecking TUN/TAP installation")
if os.path.exists("/Library/Extensions/tun.kext"):
	print("TUN/TAP detected on your system. Installation skipped.");
else:
	print("TUN/TAP was not detected on your system. Downloading TUN/TAP")
	# print("GET " + url)
	urlretrieve(tun_tap_installer_url, wd + "/tuntap.tar.gz")
	
	print("Extracting TUN/TAP archive")
	subprocess.run(["tar", "zxvf", "tuntap.tar.gz"], cwd = wd)
	
	print("Installing TUN/TAP")
	subprocess.call(["installer", "-pkg", "tuntap_20150118.pkg", "-target", "/"], cwd = wd)

# CONNECTING VPN
print("\nConnecting to AWS Instance via VPN tunnel")
vpn_process = subprocess.Popen("./openvpn --config client.ovpn", shell=True, cwd = vpnwd, preexec_fn=os.setsid)
vpn_process.wait()

