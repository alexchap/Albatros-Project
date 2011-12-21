python asip.py trace.20100401.1729  > ASIP
cat bird-peerings.conf >> ~/bird/install/etc/vlan-conf/bird.6.conf
time python ../mrt_slice/mrt_slice-0.1.py -i updates.20100401.1729 -o ribupdates.20100401.1728 -r rib.20100401.1728 -t 1s
