#! /bin/sh

# Dependencies : Iproute2, vde2, bird 

# This script configure two BGP processes on the current machine. 
# Each Bird BGP daemon will run on port 179

# Enable forwarding
echo "1" | sudo tee -a /proc/sys/net/ipv4/ip_forward

# Create and configure two tap interfaces 
sudo openvpn --mktun --dev tap11
sudo openvpn --mktun --dev tap12

sudo ip addr add 10.10.10.11/32 dev tap11
sudo ip addr add 10.10.10.12/32 dev tap12

sudo ip link set tap11 up
sudo ip link set tap12 up

# Edit routing tables
sudo ip ro add 10.10.10.11/32 dev tap12  
sudo ip ro add 10.10.10.12/32 dev tap11  

# Add specific routing tables for each router
already_done=`cat /etc/iproute2/rt_tables | egrep "(rta|rtb|flap)" | wc -l`
if [ $already_done -lt 3 ]; then
   echo "The following content has been added to /etc/iproute2/rt_tables"
   echo "11	rta" | sudo tee -a /etc/iproute2/rt_tables
   echo "12	rtb" | sudo tee -a /etc/iproute2/rt_tables
   echo "13	flap" | sudo tee -a /etc/iproute2/rt_tables
   echo "---"
fi


# Edit /etc/hosts
already_done=`cat /etc/hosts | grep "10\.10\.10\.1*" | wc -l`
if [ $already_done -lt 2 ]; then
   echo "The following content has been added to /etc/hosts"
   echo "10.10.10.11	rta" | sudo tee -a /etc/hosts
   echo "10.10.10.12	rtb" | sudo tee -a /etc/hosts
   echo "---"
fi

# Create virtual switch
sudo vde_switch -daemon -tap tap11 -tap tap12

# Start bird
sudo bird -c rta.conf -s /usr/local/var/run/bird_rta.ctl -D /var/log/bird-top03-rta.debug &
sudo bird -c rtb.conf -s /usr/local/var/run/bird_rtb.ctl -D /var/log/bird-top03-rtb.debug &

cat useful_commands.txt
