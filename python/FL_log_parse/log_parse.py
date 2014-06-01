import re,sys

class AmyParse:
	def __init__(self,in_file,out_file,info="mapping"):
		self.macMapping={}
		self.topo={}
		self.time=0
		self.link={}
		self.flows={} # flows to link
		self.loadInfo(info)
		self.openFile(in_file,out_file)
	def parse(self):
		START,END = range(0,2)
		status = END
		for  line in self.fin:
			if status == END and "Starting timer!!!" in line:
				status = START
			elif status == START :
				if "collect complete!!!" in line or "Exception:java.lang.NullPointerException" in line:
					self.fout.write( "\n\n")
					self.fout.write("Time at "+self.time+"\n")
					for node in self.link.values():
						self.fout.write(str(node))
						for flow in node.flows.values():
							if flow.throughput != -1:
								self.fout.write( "\t  {} throughput={}Kbit/s\n".format(str(flow),flow.throughput))
					status = END
				elif "collect back:" in line:
					#2014-05-14 21:08:55.500 WARN  [n.f.m.Monitoring] collect back:00:00:00:13:3b:0e:d9:5f!![]
					m = re.match('(.*) WARN.*collect back:(.*)!!(.*)',line)
					self.time = m.group(1)
					self.node = m.group(2)
					if len(m.group(3)) >2 :  ##has action fileds
						mymatch = m.group(3).split("match")
						for i in xrange(len(mymatch)):
							if len(mymatch[i]) > 1:
								m = re.match('.*in_port=(\d*),dl_dst=(.*),dl_src=(.*?),dl_vlan.*',mymatch[i])
								if m is not None:
									try:
										srcip = self.macMapping[m.group(3)]
										dstip = self.macMapping[m.group(2)]
										name = self.changeName(self.node[6:])
										node,port = name[4:],m.group(1)
										if node in self.topo and port in self.topo[node]:
											src = self.topo[node][port]
											key = "node{}:{}".format(node,port)
											if key not in self.link:
												self.link[key] = self.Link()
 											self.link[key].setSrcLink(src[0],src[1])
											self.link[key].setDstLink(node,port)
											flow = self.Flow(srcip,dstip)
											self.link[key].addFlows(flow)
											self.flows["{}->{}".format(srcip,dstip)]= flow
											#print "src={} to dst={} , on {}:{} to {}:{}".format(ip1,ip2,node,port,dst[0],dst[1])
									except Exception ,ex :
										# ignore all exception
										pass
										#print ex
								else :
									print mymatch[i]
				elif "congestion" in line:
					#2014-05-14 20:53:01.35 WARN  [n.f.m.Monitoring] #congestion:00:00:90:2b:34:51:b7:5c #port: 2#in_throughput:8641779.408235526 #out_throughput: 1.0202258824637966E7
					m = re.match(".*congestion:(.*) #port: (\d){,2}#in_throughput:(.*) #out_throughput: (.*)",line)
					switch = self.changeName(m.group(1)[6:])
					port = m.group(2)
					in_th = float(m.group(3))
					out_th = float(m.group(4))
					#check incoming
					if in_th > 9646899.2:
						key = "{}:{}".format(switch,port)
						self.link[key].congestion = True
					if out_th > 9646899.2:
						dst = self.topo[switch[4:]][port]
						key = "node{}:{}".format(dst[0],dst[1])
						if key not in self.link:
							self.link[key] = self.Link()
						self.link[key].congestion = True

					#check outgoing
				elif "collect:match" in line:
					#ignore 
					pass
				elif "Flow from" in line:
					#2014-05-14 20:54:42.534 WARN  [n.f.m.Monitoring] Flow fromfa:16:3e:ac:1b:0d to fa:16:3e:82:2b:ed && throughtput=967.4936912634861 Kbit/s.
					m = re.match('.* from(.*) to (.*) && throughtput=([\d\.]*).*',line)
					if m is not None:
						try:
							srcip = self.macMapping[m.group(1)]
							dstip = self.macMapping[m.group(2)]
							throughput = m.group(3)
							if "{}->{}".format(srcip,dstip) in self.flows:
								flow = self.flows["{}->{}".format(srcip,dstip)]
								flow.setThroughput(throughput)
							else:
								pass
						except Exception,ex:
							pass
			elif "[adjusted flow]" in line:	
				self.fout.write(line)
		self.fin.close()
		self.fout.close()
	def loadInfo(self,info):
		fin = open(info,'r')
		state = 0
		for line in fin:
			if line == "MAC TO IP\n":
				state = 1
			elif line =="TOPOLOGY\n":
				state = 2
			elif state == 1:
				#fa:16:3e:ef:5d:fd 30.0.1.3
				m =  re.match('(.*) (.*)\n',line)
				if m is not None:
					self.macMapping[m.group(1)] = m.group(2)
			elif state == 2:
				#node1:1->node3:3
				m = re.match('node(\d{,2}):(\d)->node(\d{,2}):(\d)',line)
				if m is not None:
					#build bidirectional link (srcNode,srcPort) <=> (dstNode,dstPort)
					if m.group(1)  not in self.topo:
						self.topo[m.group(1)] = {}
					self.topo[m.group(1)][m.group(2)] = (m.group(3),m.group(4))
					if m.group(3)  not in self.topo:
						self.topo[m.group(3)] = {}
					self.topo[m.group(3)][m.group(4)] = (m.group(1),m.group(2))
		fin.close()			
	def openFile(self,in_file,out_file):
		try:
			self.fin = open(in_file,'r')
			self.fout = open(out_file,'w')
		except Exception, e:
			print "openFile error" + e

	def changeName(self,name):
		if name == "bc:5f:f4:b0:33:78":
			return "node1"
		if name == "bc:5f:f4:b8:e2:5a":
			return "node2"
		if name == "90:2b:34:51:b7:5c":
			return "node3"
		if name == "00:13:3b:0e:d9:5f":
			return "node4"
		if name == "bc:5f:f4:b8:e2:fc":
			return "node5"
		if name == "bc:5f:f4:be:0c:12":
			return "node6"
		if name == "00:13:3b:0e:cd:6f":
			return "node7"
		if name == "1c:6f:65:d3:0f:a9":
			return "node8"
		if name == "bc:5f:f4:b8:e2:d2":
			return "node9"
		if name == "bc:5f:f4:b8:e3:0a":
			return "node10"
		if name == "00:13:3b:0e:d1:54":
			return "node11"
		if name == "00:13:3b:0e:d4:14":
			return "node12"
		if name == "bc:5f:f4:b8:e3:65":
			return "node13"
		if name == "bc:5f:f4:b0:33:80":
			return "node14"
		if name == "00:13:3b:0e:d2:c2":
			return "node15"
		if name == "00:13:3b:0e:d3:c3":
			return "node16"
		if name == "20:cf:30:ec:98:ce":
			return "node17"
		if name == "14:da:e9:b3:99:f3":
			return "node18"
		if name == "bc:5f:f4:b8:e2:9f":
			return "node0"  #network node
		else:
			return name

	class Flow:
		def __init__(self,srcIp,dstIp):
			self.throughput = -1
			self.srcIp = srcIp
			self.dstIp = dstIp
		def setThroughput(self,throughput):
			self.throughput = "{:.2f}".format(float(throughput))
		def __repr__(self):
			return "{}->{}".format(self.srcIp,self.dstIp)

	class Link:
		def __init__(self):
			self.srcLink = (0,0)
			self.dstLink = (0,0)
			self.flows = {}
			self.congestion = False
		def setSrcLink(self,node,port):
			self.srcLink = (node,port)
		def setDstLink(self,node,port):
			self.dstLink = (node,port)
		def addFlows(self,flows):
			if str(flows) not in self.flows:
				self.flows[str(flows)] = flows
		def __repr__(self):
			if self.congestion == True:
				return "Link (node{}:{} to node{}:{} )   (congestion)\n".format(self.srcLink[0],self.srcLink[1],self.dstLink[0],self.dstLink[1])
			else:
				return "Link (node{}:{} to node{}:{} ) \n".format(self.srcLink[0],self.srcLink[1],self.dstLink[0],self.dstLink[1])



if len(sys.argv) != 3:
	print "Usage: input_file, output_file"
	exit(0)
else:
	amy =  AmyParse(sys.argv[1],sys.argv[2])
	amy.parse()

