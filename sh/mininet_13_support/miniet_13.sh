#!/bin/sh
ovs-vsctl show | grep Bridge | awk -F "\"" '{print $2}' | xargs -i  ovs-vsctl set bridge {} protocols=OpenFlow10,OpenFlow12,OpenFlow13
