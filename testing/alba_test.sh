#! /bin/sh

# This script must be run from the testing directory.
# It creates a directory "mybird" outside de the albatros one.
# It configures and install bird with the damping and the debug message.
# Finally, it asks you which topology you want to run


#is_bird_running_status=`pgrep bird`; #?
if test `pgrep bird` 
then 
	echo "\n\n---- Which topology do you want to restart ? (01, 02, ..., 10, 11, ...):"
	read number_topology_restart
	echo "\n\n---- Restart topology #$number_topology_restart:"
	./conf/top$number_topology_restart/reset.sh
fi


echo "\n\n---- Copy file into '../../mybird' and configure -------------"

if test ! -d ../../mybird 
then 
	mkdir ../../mybird; 
	echo "---- ../../mybird created"
fi

cp -r ../bird/* ../../mybird
cd ../../mybird

if test ! -f configure.in
then autoconf
fi
./configure --enable-debug --enable-route-damping


echo "\n\n---- Let's make it! --------------------------------------"
echo "---- How many processor do you have ?  1, 2, ...:"
read proc_number
make -j $proc_number
sudo make install
echo "\n\n---- Make it done. ---------------------------------------"

echo "\n\n---- Which topology do you want to run ? Give an integer:"
read number_topology
echo "\n\n---- Let's run topology #$number_topology:"
cd ../albatros/testing/conf/top$number_topology/
./configure_interface.sh


echo "\n\n---- Alba Test End --------------------------------------\n\n"
