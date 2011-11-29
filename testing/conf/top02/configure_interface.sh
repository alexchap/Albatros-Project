#! /bin/sh

# Dependencies : Iproute2, vde2, bird,mdmft 

# Enable forwarding
echo "1" | sudo tee -a /proc/sys/net/ipv4/ip_forward

# Create and configure two tap interfaces 
sudo openvpn --mktun --dev tap11
sudo openvpn --mktun --dev tap12


sudo ip link set tap11 up
sudo ip link set tap12 up

# add ip addresses to interface & routing table
sudo ip addr add 10.10.10.11/32 dev tap11
sudo ./conf_ips.pl

# Edit routing tables
sudo ip ro add 10.10.10.11/32 dev tap12  


# Add specific routing tables for each router
already_done=`cat /etc/iproute2/rt_tables | egrep "(rta)" | wc -l`
if [ $already_done -lt 1 ]; then
   echo "The following content has been added to /etc/iproute2/rt_tables"
   echo "11	rta" | sudo tee -a /etc/iproute2/rt_tables
   echo "---"
fi


# Edit /etc/hosts
already_done=`cat /etc/hosts | grep "10\.10\.10\.11" | wc -l`
if [ $already_done -lt 1 ]; then
   echo "The following content has been added to /etc/hosts"
   echo "10.10.10.11	rta" | sudo tee -a /etc/hosts
   echo "---"
fi

# Create virtual switch
sudo vde_switch -daemon -tap tap11 -tap tap12

# Start bird
sudo bird -c rta.conf -s /usr/local/var/run/bird_rta.ctl -D /var/log/bird-top02-rta.debug &

cat  useful_commands.txt

echo "Packet generation will start in 10 seconds"
sleep 10

# Start packet generator 
echo "Starting packet generator"
sudo ../../tools/mdfmt/update_regenerator/update_regenerator.py -m ../../updates/updates.20100401.1729 -d 10.10.10.11 -a ./ASIP

