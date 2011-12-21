#!/bin/bash

###node-0###
#/sbin/vconfig add eth0 2&&/sbin/ifconfig eth0.2 10.0.0.1 netmask  255.255.255.248  up

#/sbin/vconfig add eth0 3&&/sbin/ifconfig eth0.3 10.100.0.6 netmask  255.255.255.248  up

#/sbin/vconfig add eth0 9&&/sbin/ifconfig eth0.9 10.100.0.27 netmask  255.255.255.248  up

###node-1###
#/sbin/vconfig add eth0 4&&/sbin/ifconfig eth0.4 10.0.0.2 netmask  255.255.255.248  up

#/sbin/vconfig add eth0 5&&/sbin/ifconfig eth0.5 10.100.0.14 netmask  255.255.255.248  up

#/sbin/vconfig add eth0 8&&/sbin/ifconfig eth0.8 10.100.0.26 netmask  255.255.255.248  up

#/sbin/vconfig add eth0 11&&/sbin/ifconfig eth0.11 10.100.0.35 netmask  255.255.255.248  up

###node-2###
#/sbin/vconfig add eth0 6&&/sbin/ifconfig eth0.6 10.0.0.18 netmask  255.255.255.248  up

#/sbin/vconfig add eth0 7&&/sbin/ifconfig eth0.7 10.100.0.22 netmask  255.255.255.248  up

#/sbin/vconfig add eth0 10&&/sbin/ifconfig eth0.10 10.100.0.34 netmask  255.255.255.248  up

/sbin/vconfig add eth0 51 && /sbin/ifconfig eth0.51 206.223.115.6 netmask 255.255.255.128 up
