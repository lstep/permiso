# Introduction #

The `permiso.collector` module is the link between the firewall and the `permiso.identity` module. The collector gets its information from the `NF_QUEUE` or `IP_QUEUE` iptable module and then sends it using PB to the Identity module where it will be checked against the internal database.

# Requirements #

You must be on a Linux system, with iptables compiled in the kernel (or as a module) and the CONFIG\_NETFILTER\_NETLINK set. You must have support for `IP_QUEUE` (old kernels) or NF\_QUEUE (newer kernels).
The Collector uses the [ipqueue](http://woozle.org/~neale/src/ipqueue/) python module or the [nfqueue](http://woozle.org/~neale/src/ipqueue/) python module.
They are not installable using `easy_install`, so you'll need to download them and install them (gcc is required).

Note: When compiling the ipqueue module, if you get errors like `ipqueue.c:7:20: libipq.h : Aucun fichier ou répertoire de ce type`, it means you haven't installed the [netfilter dev libraries](http://www.netfilter.org/projects/libnetfilter_queue/).


# Details #