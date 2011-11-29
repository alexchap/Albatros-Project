#! /bin/sh

# Reset configuration to default

echo "Kill Bird and virtual switch"
sudo pkill bird
sudo pkill vde_switch

echo "Remove tap interfaces"
sudo ip link set tap11 down
sudo ip link set tap12 down
sudo openvpn --rmtun --dev tap11
sudo openvpn --rmtun --dev tap12

echo "Deleting logs"
sudo rm /var/log/bird-top04-rta.log
sudo rm /var/log/bird-top04-rta.debug
