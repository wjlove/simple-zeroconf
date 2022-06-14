#!/usr/bin/env python3

""" Example of announcing a service (in this case, a balenAIR senor) """

import argparse
import logging
import socket
import os
import signal
import sys
import time
from time import sleep
import json
import urllib.request
from urllib.error import HTTPError, URLError
from zeroconf import IPVersion, ServiceInfo, Zeroconf


try:
    serviceDescriptionTxt = os.getenv('ZEROCONF_SERVICE_DESCRIPTION', 'No Descrition')
except Exception as e:
    serviceDescriptionTxt = "No Description"
    print("Invalid value for ZEROCONF_SERVICE_DESCRIPTION, using default")
try:
    serviceType = os.getenv('ZEROCONF_SERVICE_TYPE', '_balenair')
    serviceType = serviceType + "._tcp.local."
except Exception as e:
    serviceType = "_balenair._tcp.local."
    print("Invalid value for ZEROCONF_SERVICE_TYPE, using default")
try:
    servicePort = int(os.getenv('ZEROCONF_SERVICE_PORT', '1880'))
except Exception as e:
    servicePort = 1880
    print("Invalid value for ZEROCONF_SERVICE_PORT, using default")
#
# print("From ENV settings, Description:", serviceDescriptionTxt, "Type:", serviceType, "Port:", servicePort)

# Get supervisor info, Actually if either one of these fail we should just bail.....
try:
    supervisorAddress = os.getenv('BALENA_SUPERVISOR_ADDRESS', '127.0.0.1')
except Exception as e:
    supervisorAddress = "Fail"
    print("Invalid value for BALENA_SUPERVISOR_ADDRESS, using default")
try:
    supervisorApiKey = os.getenv('BALENA_SUPERVISOR_API_KEY', '127.0.0.1')
except Exception as e:
    supervisorApiKey = "Fail"
    print("Invalid value for BALENA_SUPERVISOR_ADDRESS_API_KEY, using default")

def exitGracefully(cleanUpInfo):
    print()
    print("Unregistering service.... ")
    zeroconf.unregister_service(cleanUpInfo)
    zeroconf.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument('--v6', action='store_true')
    version_group.add_argument('--v6-only', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    if args.v6:
        ip_version = IPVersion.All
    elif args.v6_only:
        ip_version = IPVersion.V6Only
    else:
        ip_version = IPVersion.V4Only


    # Stuff we need for the service
    serviceDescription = {'Device Type': serviceDescriptionTxt}
    hostName = socket.gethostname()
    # print("Hostname", hostName)

    # Build a URL for accessing the balena supoervisor API
    supervisorURL = supervisorAddress + "/v1/device?apikey=" + supervisorApiKey

    # Get what the balena supervisor believes is the local ip address of the device.  Depends on the container running in network_mode: host
    try:
        deviceRawData = urllib.request.urlopen(supervisorURL, timeout=10).read().decode()
    except HTTPError as error:
        print('HTTP Error: Data not retrieved because %s\nURL: %s', error, supervisorURL)
    except URLError as error:
        if isinstance(error.reason, socket.timeout):
            print('Timeout Error: Data not retrieved because %s\nURL: %s',  error, supervisorURL)
        else:
            print('URL Error: some other error....')

    deviceInfo = json.loads(deviceRawData)
    serviceAddress = deviceInfo['ip_address']
    serviceName = hostName + "." + serviceType
    print("Advertising this service:", serviceName, " Service address: ", serviceAddress, "Service Type:", serviceType)

    info = ServiceInfo(
        serviceType,
        name=serviceName,
        addresses=[socket.inet_aton(serviceAddress)],
        port=servicePort,
        properties=serviceDescription,
        server=hostName + ".local.",
    )

    zeroconf = Zeroconf(ip_version=ip_version)
    print("Registration of", serviceType, "service complete")
    zeroconf.register_service(info)

    # Catch SIGTERM and cleanup if we are restarted by the supervisor
    def sigterm_handler(signal, frame):
        print()
        print('Caught SIGTEM!  Cleanup and unregister service...')
        zeroconf.unregister_service(info)
        zeroconf.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, sigterm_handler)

    # We really just need to sleep forever, this code left in place for testing.
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # print("Unregistering...")
        # zeroconf.unregister_service(info)
        # zeroconf.close()
        exitGracefully(info)