#!/usr/bin/python
#
# landscape-sysinfo-mini.py -- a trivial re-implementation of the 
# sysinfo printout shown on debian at boot time. No twisted, no reactor, just /proc & utmp
#
# (C) 2014 jw@owncloud.com
#
# inspired by ubuntu 14.10 /etc/update-motd.d/50-landscape-sysinfo
# Requires: python-utmp 
# for counting users.
#
# 2014-09-07 V1.0 jw, ad hoc writeup, feature-complete. Probably buggy?
# 2014-10-08 V1.1 jw, survive without swap
# 2014-10-13 V1.2 jw, survive without network

import sys,os,time,posix,glob,utmp,subprocess,apt_pkg
from subprocess import PIPE
_version_ = '1.2'

def dev_addr(device):
  """ find the local ip address on the given device """
  if device is None: return None
  for l in subprocess.Popen(['ip route list dev '+device],shell=True,stdout=PIPE,stderr=PIPE).stdout:
    seen=''
    for a in l.split():
      if seen == 'src': return a
      seen = a
  return None

def default_dev():
  """ find the device where our default route is """
  for l in open('/proc/net/route').readlines():
    a = l.split()
    if a[1] == '00000000':
      return a[0]
  return None

def all_iface():
  """ return all the interfaces """
  return  [(interface, dev_addr(interface)) for interface in set([a.split()[0]  for a in open('/proc/net/route').readlines()])  if dev_addr(interface) is not None]

def utmp_count():
  u = utmp.UtmpRecord()
  users = 0
  for i in u:
    if i.ut_type == utmp.USER_PROCESS: users += 1
  return users

def proc_meminfo():
  items = {}
  for l in open('/proc/meminfo').readlines():
    a = l.split()
    items[a[0]] = int(a[1])
  # print items['MemTotal:'], items['MemFree:'], items['SwapTotal:'], items['SwapFree:']
  return items

loadav = float(open("/proc/loadavg").read().split()[1])
processes = len(glob.glob('/proc/[0-9]*'))
statfs = os.statvfs('/')
rootperc = 100-100.*statfs.f_bavail/statfs.f_blocks
rootgb = statfs.f_bsize*statfs.f_blocks/1024./1024/1024
rootusage = "%.1f%% of %.2fGB" % (rootperc, rootgb)
defaultdev = default_dev()
ipaddr = dev_addr(defaultdev)
users = utmp_count()
meminfo = proc_meminfo()
memperc = "%d%%" % (100-100.*meminfo['MemFree:']/(meminfo['MemTotal:'] or 1))
swapperc = "%d%%" % (100-100.*meminfo['SwapFree:']/(meminfo['SwapTotal:'] or 1))

if meminfo['SwapTotal:'] == 0: swapperc = '---'

print "  System information as of %s\n" % time.asctime()
print "  System load:  %-5.2f                Processes:           %d" % (loadav, processes)
print "  Usage of /:   %-20s Users logged in:     %d"% (rootusage, users)
print "  Memory usage: %-4s                 " % memperc
for interface, ip in all_iface():
  print "                                     IP address for %s: %s" % ( interface, ip )
print "  Swap usage:   %s" % (swapperc)
print ""

DISTRO = subprocess.Popen(["lsb_release", "-c", "-s"],
                          stdout=subprocess.PIPE).communicate()[0].strip()

class OpNullProgress(object):
    '''apt progress handler which supresses any output.'''
    def update(self):
        pass
    def done(self):
        pass

def is_security_upgrade(pkg):
    '''
    Checks to see if a package comes from a DISTRO-security source.
    '''
    security_package_sources = [("Ubuntu", "%s-security" % DISTRO),
                               ("Debian", "%s-security" % DISTRO)]

    for (file, index) in pkg.file_list:
        for origin, archive in security_package_sources:
            if (file.archive == archive and file.origin == origin):
                return True
    return False

# init apt and config
apt_pkg.init()

# open the apt cache
try:
    cache = apt_pkg.Cache(OpNullProgress())
except SystemError, e:
    sys.stderr.write("Error: Opening the cache (%s)" % e)
    sys.exit(-1)

# setup a DepCache instance to interact with the repo
depcache = apt_pkg.DepCache(cache)

# take into account apt policies
depcache.read_pinfile()

# initialise it
depcache.init()

# give up if packages are broken
if depcache.broken_count > 0:
    sys.stderr.write("Error: Broken packages exist.")
    sys.exit(-1)

# mark possible packages
try:
    # run distro-upgrade
    depcache.upgrade(True)
    # reset if packages get marked as deleted -> we don't want to break anything
    if depcache.del_count > 0:
        depcache.init()

    # then a standard upgrade
    depcache.upgrade()
except SystemError, e:
    sys.stderr.write("Error: Couldn't mark the upgrade (%s)" % e)
    sys.exit(-1)

# run around the packages
upgrades = 0
security_upgrades = 0
for pkg in cache.packages:
    candidate = depcache.get_candidate_ver(pkg)
    current = pkg.current_ver

    # skip packages not marked as upgraded/installed
    if not (depcache.marked_install(pkg) or depcache.marked_upgrade(pkg)):
        continue

    # increment the upgrade counter
    upgrades += 1

    # keep another count for security upgrades
    if is_security_upgrade(candidate):
        security_upgrades += 1

    # double check for security upgrades masked by another package
    for version in pkg.version_list:
        if (current and apt_pkg.version_compare(version.ver_str, current.ver_str) <= 0):
            continue
        if is_security_upgrade(version):
            security_upgrades += 1
            break

print "%d updates to install." % upgrades
print "%d are security updates." % security_upgrades
print "" # leave a trailing blank line

sys.exit(0)
