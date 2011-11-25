# Shortcut to start bird routing daemons
sudo bird -c rta.conf -s /usr/local/var/run/bird_rta.ctl -D /var/log/bird-top03-rta.debug & 
sudo bird -c rtb.conf -s /usr/local/var/run/bird_rtb.ctl -D /var/log/bird-top03-rtb.debug &

