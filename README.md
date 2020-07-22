landscape-sysinfo-mini
======================

a trivial re-implementation of the sysinfo printout shown on debian at boot time. No twisted, no reactor, just /proc &amp; utmp  inspired by ubuntu 14.10 /etc/update-motd.d/50-landscape-sysinfo Requires: python-utmp for counting users.

The script now shows updates to install and how many of them are security updates. 

#Sample output

  System information as of Wed Jul 22 16:38:04 2020

  System load:  0.17                 Processes:           158
  Usage of /:   7.0% of 145.71GB     Users logged in:     6
  Memory usage: 94%
                                     IP address for wlan0: 192.168.1.1
                                     IP address for eth1: 192.168.2.2
                                     IP address for eth0: 192.168.3.1
  Swap usage:   0%

0 updates to install.
0 are security updates.
