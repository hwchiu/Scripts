Brief
-----
- It will use the Restful api to query floodlight controller and parse the default flow entry to collect data.
- The default restful server at 127.0.0.1
- The result will contains all pair sec/dst mac address and switches which have the flow entry about that src/dst mac address.


Usage
-----
- python show_switches.py



Example
-------
``` 
(u'02:98:ff:7a:18:8b', u'32:26:d0:e7:5b:6b')
dpid=00:00:00:00:00:00:00:05
dpid=00:00:00:00:00:00:00:07
dpid=00:00:00:00:00:00:00:06
------------------------------------
(u'86:ca:c2:61:c2:9d', u'92:69:ca:81:fb:db')
dpid=00:00:00:00:00:00:00:03
dpid=00:00:00:00:00:00:00:02
dpid=00:00:00:00:00:00:00:04
------------------------------------
```
