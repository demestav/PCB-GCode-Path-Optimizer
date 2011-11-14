import re
import math
import sys

print ''
print '-= pcb-gcode Optimizer version 0.9 =-'
#-= Written by Demetris Stavrou and Michael Skitsas =-'
#-= November 2011 =-'
# Check if the source file is provided from the command line
if (len(sys.argv) < 2):
	print 'Please define the original file... (for example "python cncopt.py myfile.tap")'
	sys.exit("File not defined. Exitting...")
	
# The node class
# Holds the starting coordinates
# the finish coordinates
# and the corresponding gcode string
class mynode(object):

    def __init__(self, nodegcode):
        self.nodegcode = nodegcode
        result = re.findall("G00 X(.*?) Y(.*?)[ ]*?\n",nodegcode)
        self.start=result[0]
        result = re.findall("G01 X(.*?) Y(.*?)[ ]?\nG00 Z[^-]",nodegcode)
        self.finish=result[0]

    def disp(self):
        print self.nodegcode
        
# Function to calculate the euclidian distance between two coordinate points (X1,Y1),(X2, Y2)
def edist(point1,point2):
    distance = math.sqrt(math.pow(float(point1[1])-float(point2[1]),2)+math.pow(float(point1[0])-float(point2[0]),2))
    return distance
filename = sys.argv[1]
gcode = open(filename, 'r').read();  
gcode = re.sub("[ ]{2,}"," ",gcode);    # Clean the gcode from double (or more) spaces
gcode = re.sub(" \n", "\n", gcode)

result = re.findall("^([^~,]+?)(G00 X[-0-9.]{6,7} Y[-0-9.]{6,7}\nG01 Z-[.0-9]{6}[^~,]*)(G00 Z[^-][^~,]+?)$",gcode) # get the header and footer above and below the interesting gcode
print re.findall("^([^~,]+?)G00",gcode);
header = result[0][0]
footer = result[0][2]
m = re.findall("G00 X[-0-9.]{6,7} Y[-0-9.]{6,7}\nG01 Z-[0-9.]{6}[^~,]+?G00 Z[^-].+?\n",gcode); # break done the gcode to paths

nodes=[]
proc_nodes=[]
print "Found "+str(len(m))+" paths..."

for l in m:
    nodes.append(mynode(l)) # Create a node out of each path

# Evaluate the cost before optimization
total_cost=0;
total_cost=total_cost + edist(('0','0'),nodes[0].start)
for l in range(0, len(nodes)-1):
    total_cost = total_cost + edist(nodes[l].finish,nodes[l+1].start)
print "Initial Cost :"+str(total_cost)

# Main optimization algorithm
# First find the path closest to the origin (0,0)
next_node_idx = 0
min_dist=1000
for l in nodes:
    dist = edist(('0','0'),l.start)
    if dist<min_dist:
        min_dist = dist
        next_node_idx = nodes.index(l)

# Then process all the rest   
while(nodes):
    next_node = nodes.pop(next_node_idx)    # Remove node under investigation from unprocesses and place it into processed
    proc_nodes.append(next_node)
    min_dist=1000
    for l in nodes:
        dist = edist(next_node.finish,l.start)
        if dist<min_dist:
            min_dist = dist
            next_node_idx = nodes.index(l)

# Evaluate the cost after optimization
total_cost=0;
total_cost=total_cost + edist(('0','0'),proc_nodes[0].start)
for l in range(0, len(proc_nodes)-1):
    total_cost = total_cost + edist(proc_nodes[l].finish,proc_nodes[l+1].start)
print "Optimized Cost :"+str(total_cost)

# Write the result to file
print 'Your optimized file is '+filename+'.optimized'
print ''
wf = open(filename+'.optimized','w')
wf.write(header)
for l in proc_nodes:
    wf.write(l.nodegcode)
wf.write(footer)
wf.close()
