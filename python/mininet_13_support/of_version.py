import argparse
import subprocess

parser = argparse.ArgumentParser(description='Modify the supported verstion of openvswitch.')
parser.add_argument('-v',"--version",type=str, choices=["OF10","OF11","OF12","OF13"],default="OF10",nargs="*",
                   help='a version that openvswitch will support')
parser.add_argument('-i', "--INCLUDE",type=str,nargs="*",
                   help='the bridges you want to modify. You can set the value to ALL to modify all bridges')
parser.add_argument('-e', "--EXCLUDE",type=str,nargs="*",
                   help='the bridges you don\'t want to modify')
args = parser.parse_args()

versionMapping = {'OF10':'OpenFlow10','OF11':'OpenFlow11','OF12':'OpenFlow12','OF13':'OpenFlow13'}
versions = ",".join([ versionMapping[ver] for ver in args.version])
if args.INCLUDE != None and args.EXCLUDE != None:
	print "INCLUDE option and EXCLUDE option are mutually exclusive"
	exit (1)
if args.INCLUDE == None and args.EXCLUDE == None:
	print "You must set one of INCLUDE or EXCLUDE options"
	exit (1)

def fetchAllBridge(bridges):
	p1 = subprocess.Popen(['ovs-vsctl','show'],stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['grep', 'Bridge'], stdin=p1.stdout,stdout = subprocess.PIPE)
	p3 = subprocess.Popen(['awk','-F','\\\"','{print $2}'],stdin = p2.stdout,stdout=subprocess.PIPE)
	p1.stdout.close() #make sure we close the output so p2 doesn't hang waiting for more input
	p2.stdout.close()
	output = p3.communicate()[0] #run our commands
	for br in output.split("\n"):
		if br!="":
			bridges.add(br)

bridges = set()
if args.INCLUDE !=None:
	if "ALL" in args.INCLUDE or "all" in args.INCLUDE:
		fetchAllBridge(bridges)
	else:
		for br in args.INCLUDE:
			bridges.add(br)
if args.EXCLUDE !=None:
	fetchAllBridge(bridges)
	for br in args.EXCLUDE:
		if br in bridges:
			bridges.remove(br)


#ovs-vsctl set bridge {} protocols=OpenFlow10,OpenFlow12,OpenFlow13
for br in bridges:
	subprocess.call(['ovs-vsctl','set','bridge',br,'protocols='+versions])
