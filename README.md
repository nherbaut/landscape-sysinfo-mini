landscape-sysinfo-mini
======================

a trivial re-implementation of the sysinfo printout shown on debian at boot time. No twisted, no reactor, just /proc &amp; utmp  inspired by ubuntu 14.10 /etc/update-motd.d/50-landscape-sysinfo Requires: python-utmp for counting users.

The script now shows updates to install and how many of them are security updates. 

## Sample Output

![Sample Output](https://github.com/spithash/trunk/blob/master/landscape-sysinfo.jpg?raw=true)

### Credits
- Original script from:
https://github.com/jnweiger/landscape-sysinfo-mini
- Modified script from:
https://github.com/nherbaut/landscape-sysinfo-mini
- Show packages update:
https://nickcharlton.net/posts/debian-ubuntu-dynamic-motd.html

I just did the laundry :)
Enjoy
