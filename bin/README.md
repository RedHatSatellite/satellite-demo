Misc Executables
================

Overview
--------

These are a collection of executables.

* `benchmark.sh` - This is a simple script to run a benchmark on different playbooks and sections of the playbooks.
* `getca.py` - This is the executable that is the basis for the `getca` task module in `library/`
* `getca.sh` - This was the first iteration of the function.
* `proxy` - This is a utility that shortens the ability to connect to the proxy hosts.

benchmark.sh
------------

This script uses `time` to benchmark the creation and configuration of the
router and satellite server.

The following is output from a quad core AMD A8-5600K @ 3.6GHz running with the
OS on spinning disk, and pulp/mongodb running on ssd:

    First we clean everything up

    real    1m17.201s
    user    0m19.058s
    sys     0m3.724s

    Time the VM creation of the servers

    real    1m57.447s
    user    0m24.618s
    sys     0m4.219s

    Time the configuration of the router

    real    4m5.637s
    user    0m45.176s
    sys     0m5.757s

    Time the configuration of the satellite

    real    2m47.234s
    user    0m32.486s
    sys     0m4.149s

    Time the installation of Satellite 6

    real    37m33.667s
    user    5m48.715s
    sys     0m34.448s

    Time the configuration of Satellite 6
     [WARNING]: Consider using yum, dnf or zypper module rather than running rpm

    real    53m5.704s
    user    8m25.585s
    sys     0m51.019s

    ALL DONE!!

getca.sh and getca.py
---------------------

These scripts, when given a server and optional port, will extract all the certificates presented from the server and print the last one in the chain, which is typically the root CA. This is useful for grabbing a self-signed cert, or for getting a personal/company CA that you use for your organization.

Usage:

    ./getca.sh server [port]

Reponse:

    [pem encoded x509 Certificate]

proxy.sh
--------

This script is just a helper to connect to the proxied systems.

Usage:

    ./proxy $JUMP_SERVER $PROXIED_SERVER [ssh_options]

Where `ssh_options` are anything you can send to to the ssh binary.
