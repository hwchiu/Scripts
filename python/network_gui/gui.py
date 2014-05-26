#!/usr/bin/env python

from Tkinter import *
import re
import copy
class GUIDemo(Frame):
    def __init__(self, master=None,filename="input"):
        Frame.__init__(self,master,width=1400, height=680, background="white")
        self.initialVariable()
        self.loadFile(filename)
        self.nodeData = self.timedata[self.numberToTime[1]]
        self.pack()
        self.createWidgets()
        self.createTopo()
        self.run()
        """
        for time in self.timedata:
            print time       
            for src in self.timedata[time]:
                nodedata = self.timedata[time]
                for dst in nodedata[src]:
                    print src,dst
                    print "from {}  to {}".format(src,dst)
                    for flow in nodedata[src][dst][0].flows:
                        print "{} -> {} at {}".format(flow.srcIp,flow.dstIp,flow.throughput)
                    print "from {}  to {}".format(dst,src)
                    for flow in nodedata[src][dst][1].flows:
                        print "{} -> {} at {}".format(flow.srcIp,flow.dstIp,flow.throughput)
        """
    def initialVariable(self):
        self.var = StringVar()
        self.timevar = StringVar()
        self.nodeSize = 80
        self.nodeLocation = {}  # key = nodename,value = tuple(x,y)
        self.timedata = {} # key = time, value = link data
        self.numberToTime = {}
        self.numberToName = {}
        self.time = None
        self.isReverse = False
        self.nodeData = {}
        self.srcNode = None
        self.dstNode = None
      
    def run(self):
        self.mainloop()
    def storeData(self):
        if self.time is not None:
            self.timedata[self.time] = self.nodeData
            self.numberToTime[len(self.timedata)] = self.time
            self.nodeData = {}
    def loadFile(self,filename):
        f = open(filename,'r')
        for line in f:
            if "Time at" in line:
                #store the pervios data
                self.storeData()
                #fetch the time
                #Time at 2014-05-14 20:20:55.530
                m = re.match('Time at (.*)',line)
                if m is not None:
                    self.time = m.group(1)
                else:
                    print "Parse time fail"
            elif "Link" in line:
                #Link (node16:4 to node8:4 )
                congestion = False
                #print line
                if "congestion" in line:
                    congestion = True
                m = re.match('node([0-9]+):([0-9]+) to node([\d]{1,2}):([\d]{1,2})',line[6:])
                if int(m.group(3)) > int(m.group(1)):
                    self.isReverse = False
                    self.srcNode = (m.group(1),m.group(2))
                    self.dstNode = (m.group(3),m.group(4))
                else:
                    self.isReverse = True
                    self.srcNode = (m.group(3),m.group(4))
                    self.dstNode = (m.group(1),m.group(2))
                if self.srcNode not in self.nodeData:
                    self.nodeData[self.srcNode] = {}
                if self.dstNode not in self.nodeData[self.srcNode]:
                    t1 = self.Link(self.srcNode[0],self.srcNode[1],self.dstNode[0],self.dstNode[1])
                    t2 = self.Link(self.dstNode[0],self.dstNode[1],self.srcNode[0],self.srcNode[1])
                    if self.isReverse:
                        t2.congestion = congestion
                    else:
                        t1.congestion = congestion
                    self.nodeData[self.srcNode][self.dstNode] = (t1,t2)
                
            elif "Kbit/s" in line:
               #30.0.1.11->30.0.1.3 throughput=1.92Kbit/s
                m = re.match("\t (.*)->(.*) throughput=(.*?)Kbit",line)
                #print self.srcNode,self.dstNode
                if self.isReverse == False:
                    self.nodeData[self.srcNode][self.dstNode][0].flows.append(self.Flow(m.group(1),m.group(2),m.group(3)))
                else:
                    self.nodeData[self.srcNode][self.dstNode][1].flows.append(self.Flow(m.group(1),m.group(2),m.group(3)))
        self.storeData()
        f.close()
    
    def createWidgets(self):
        self.left_widget = Canvas(root,background="#234561",width=800,height=680)
        self.left_widget.place(x=0, y=0)

        
        self.right_widget = Canvas(root,background="#ffffff",width=595,height=800)
        self.right_widget.place(x=800, y=0)
        self.timeLabel = Label(root,textvariable=self.timevar,activeforeground="black")
        self.timeLabel.place(x=0,y=630)              
        self.timebar = Scale(root, orient=HORIZONTAL, length=1200, from_=1.0, to=len(self.timedata),command = self.updateTime)
        self.timebar.place(x=0,y=650)        
        
    def updateTime(self,event):
        self.nodeData = self.timedata[self.numberToTime[self.timebar.get()]]
        self.timevar.set(self.numberToTime[self.timebar.get()])
        
    def createTopo(self):
        self.createNodeLocation()
        #create link
        self.createLink("node4","node11",1,3)
        self.createLink("node4","node12",3,3)
        self.createLink("node4","node15",2,3)
        self.createLink("node4","node16",4,3)
        self.createLink("node8","node11",1,4)
        self.createLink("node8","node12",3,4)
        self.createLink("node8","node15",2,4)
        self.createLink("node8","node16",4,4)
        self.createLink("node11","node3",1,4)
        self.createLink("node11","node7",2,1)
        self.createLink("node15","node3",2,1)
        self.createLink("node15","node7",1,4)
        self.createLink("node12","node17",1,3)
        self.createLink("node12","node18",2,3)
        self.createLink("node16","node17",1,4)
        self.createLink("node16","node18",2,4)
        self.createLink("node3","node1",3,1)
        self.createLink("node3","node2",2,1)
        self.createLink("node7","node9",2,1)
        self.createLink("node7","node10",3,1)
        self.createLink("node17","node5",1,1)
        self.createLink("node17","node6",2,1)
        self.createLink("node18","node13",1,1)
        self.createLink("node18","node14",2,1)        
        #create switch
        self.createSwitch("node4")
        self.createSwitch("node8")
        self.createSwitch("node11")
        self.createSwitch("node15")
        self.createSwitch("node12")
        self.createSwitch("node16")
        self.createSwitch("node3")
        self.createSwitch("node7")
        self.createSwitch("node17")
        self.createSwitch("node18")
        self.createSwitch("node1")
        self.createSwitch("node2")         
        self.createSwitch("node9")
        self.createSwitch("node10")
        self.createSwitch("node5")
        self.createSwitch("node6")         
        self.createSwitch("node13")
        self.createSwitch("node14")

        #create switch label
        self.createLabel("node1")
        self.createLabel("node2")
        self.createLabel("node3")
        self.createLabel("node4")
        self.createLabel("node5")
        self.createLabel("node6")
        self.createLabel("node7")
        self.createLabel("node8")
        self.createLabel("node9")
        self.createLabel("node10")
        self.createLabel("node11")
        self.createLabel("node12")
        self.createLabel("node13")
        self.createLabel("node14")
        self.createLabel("node15")
        self.createLabel("node16")
        self.createLabel("node17")
        self.createLabel("node18")
        #self.left_widget.create_oval(10,10,100,100,fill="#000000",tags='oval1')
    def createNodeLocation(self):
        self.nodeLocation["node4"] = (200,30)
        self.nodeLocation["node8"] = (450,30)
        self.nodeLocation["node11"] = (50,180)
        self.nodeLocation["node15"] = (250,180)
        self.nodeLocation["node12"] = (450,180)
        self.nodeLocation["node16"] = (650,180)
        self.nodeLocation["node3"] = (50,330)
        self.nodeLocation["node7"] = (250,330)
        self.nodeLocation["node17"] = (450,330)
        self.nodeLocation["node18"] = (650,330)
        self.nodeLocation["node1"] = (10,480)
        self.nodeLocation["node2"] = (110,480)         
        self.nodeLocation["node9"] = (210,480)
        self.nodeLocation["node10"] = (310,480)
        self.nodeLocation["node5"] = (410,480)
        self.nodeLocation["node6"] = (510,480)         
        self.nodeLocation["node13"] = (610,480)
        self.nodeLocation["node14"] = (710,480)        
    def createSwitch(self,name):
        x = self.nodeLocation[name][0]
        y = self.nodeLocation[name][1]
        self.nodeLocation[name] = (x,y)
        nodeNumber = self.left_widget.create_oval(x,y,x+self.nodeSize,y+self.nodeSize,fill="#000000",tags=name)
        self.numberToName[nodeNumber] = name
        
    def createLink(self,node1,node2,port1,port2):
        loc1 = self.nodeLocation[node1] 
        loc2 = self.nodeLocation[node2]
        size = self.nodeSize / 2
        name = "{}:{}->{}:{}".format(node1,port1,node2,port2)
        linkNumber = self.left_widget.create_line(loc1[0]+size, loc1[1]+size, loc2[0]+size, loc2[1]+size,width=12,tags=name)
        self.left_widget.tag_bind(name,'<Button-1>',func=self.showLink)
        self.numberToName[linkNumber] = "{}:{} -> {}:{}".format(node1,port1,node2,port2)
    def createLabel(self,node):
        loc1 = self.nodeLocation[node]
        size = self.nodeSize / 2
        self.left_widget.create_text(loc1[0]+size,loc1[1]+size,text=node,fill="white")

    def showLink(self,event):
        self.right_widget.delete(ALL)
        num = self.left_widget.find_closest(event.x, event.y)
        linkname = self.numberToName[num[0]]
        print linkname
        m = re.match("node([0-9]+):([0-9]+) -> node([\d]{1,2}):([\d]{1,2})",linkname)
        src = (m.group(1),m.group(2))
        dst = (m.group(3),m.group(4))
        
        if int(m.group(1)) > int(m.group(3)):
            src,dst = dst,src
        
        if src not in self.nodeData:
            return
        if dst not in self.nodeData[src]:
            return
        print src,dst
        data = self.nodeData[src][dst]
        print data
        if data[0].congestion:
            self.right_widget.create_text(100,20,text="node{} to node{}  congestion".format(src[0],dst[0]))
        else:
            self.right_widget.create_text(100,20,text="node{} to node{}".format(src[0],dst[0]))
        i = 0
        sum = 0
        for flow in data[0].flows:
            self.right_widget.create_text(75,50+i*20,text="{} -> {} = {:.2f} Kbs".format(flow.srcIp,flow.dstIp,flow.throughput),anchor="w")
            sum += flow.throughput
            i +=1
        self.right_widget.create_text(75,50+i*20,text="total = {:.3f} kbit/s".format(sum),anchor="w")	
        if data[1].congestion:
            self.right_widget.create_text(450,20,text="node{} to node{}  congestion".format(dst[0],src[0]))
        else:
            self.right_widget.create_text(450,20,text="node{} to node{}".format(dst[0],src[0]))
        i = 0
        sum = 0
        for flow in data[1].flows:
            self.right_widget.create_text(350,50+i*20,text="{} -> {} = {:.2f} Kbs".format(flow.srcIp,flow.dstIp,flow.throughput),anchor="w")
            i +=1
            sum += flow.throughput            
        #self.right_widget.create_text(50,50,text=len)
        self.right_widget.create_text(350,50+i*20,text="total = {:.3f} kbit/s".format(sum),anchor="w")

    class Link:
        def __init__(self,srcNode,srcPort,dstNode,dstPort):
            self.srcNode = srcNode
            self.srcPort = srcPort
            self.dstNode = dstNode
            self.dstPort = dstPort
            self.flows = []
            self.congestion = False
    class Flow:
        def __init__(self,srcIp,dstIp,throughput):
            self.srcIp = srcIp
            self.dstIp = dstIp
            self.throughput = float(throughput)
            
        
if __name__ == '__main__':
    root = Tk()
    app = GUIDemo(master=root)
    
 
