###Brief
- This script will make the openvswitch to support openflow 1.1,1.2,1.3.
- You can use it with mininet to test openflow 1.3 environment.

###Usage
- Use the -v option to specify the openflow version and it must be OF10,OF11,OF12,OF13. you can specify multiple version using a space-separated list.
- Use the -i option to specify the bridge you want to set and which must be one of the `ovs-vsctl show`.
- Use the -e option to specify the bridge you don't want to set.
- The -i option and -e option are mutually exclusive.

###Example
- python of_version.py -v OF13 -i ALL
- python of_version.py -v OF13 OF12 -i s1 s2
- python of_version.py -v OF10 OF13 -e s3
