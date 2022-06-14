# simple-zeroconf

This is fork of python-zeroconf by Jakub Stasiak (https://github.com/jstasiak/python-zeroconf). It has been modified to simply advertise a single service via DNS-SD via a balena block.

Compatible with:

* Bonjour
* Avahi

## Usage

Here is an example of using this block in your `docker-compose.yml`.  

```
version: '2.1'
services:

  simple-zeroconf:
    image: bh.cr/william_love/simple-zeroconf-<arch>
    restart: "always"
    network_mode: host
    environment:
      ZEROCONF_SERVICE_PORT: 8080
      ZEROCONF_SERVICE_TYPE: "_mytestservice"
      ZEROCONF_SERVICE_DESCRIPTION: "My Test Service"
    labels:
      io.balena.features.supervisor-api: '1'

```
Currently the supported `<arch>` are `arm7hf`, `aarch64` and `amd64`.

The environment variable ZEROCONF_SERVICE_TYPE defines the name of the service to advertise (the leading "_" is required), while ZEROCONF_SERVICE_PORT and ZEROCONF_SERVICE_DESCRIPTION respectively define the port the service can be found on and a short description of the service.

You can also set these variables via the balena dashboard, review [this](https://www.balena.io/docs/learn/manage/variables/) for more information about setting variables in the balenaCloud.

Note:  This block uses the balena supervisor API to discover the host name of the hostOS as visiable to the local network to be able to create the full service name.  If you change the hostname using the balena supervisor API the block will notice the change and update the service advertisement.  For more inforation about working with the supervisor API refer to this [documentation](https://www.balena.io/docs/reference/supervisor/supervisor-api/#http-api-reference).