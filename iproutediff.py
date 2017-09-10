#!/usr/bin/python3

# iproutediff - Compares outputs of "show ip route" for changes
#
# Written by Foeh Mannay, September 2017

import re

def parse(filename):
# Opens the file referenced by "filename" and attempts to interpret IP routes from it
	
	# Initialise empty values for all fields:
	routes={}
	code = ""
	prefix = ""
	prefixlength = 33
	admindistance = 0
	metric = 0
	nexthop = ""
	interface = ""
	age = ""

	with open(filename, 'r') as infile:
		for line in infile:
			# skip lines with a prompt, the legend and the GOLR
			m = re.search('#|RIP|OSPF|IS-IS|ODR|Gateway|variably', line)
			if(m):
				continue
			# Match lines that imply the prefix length for the following routes
			m = re.search('(\d*.\d*.\d*.\d*)(/\d*)is subnetted', line)
			if(m):
				prefixlength=m.group(2)
				continue
			# Match BGP routes (age, no interface)
			m = re.search('^(B       )(\d*.\d*.\d*.\d*)(/\d*) \[(\d*)/(\d*)\] via (\d*.\d*.\d*.\d*), (.*)', line)
			if(m):
				code=m.group(1)
				prefix=m.group(2)
				prefixlength=m.group(3)
				admindistance=m.group(4)
				metric=m.group(5)
				nexthop=m.group(6)
				age=m.group(7)
				routes[prefix+prefixlength]=[code, admindistance, metric, nexthop, '', age]
				continue
			# Match static routes (age, no interface)
			m = re.search('^(S       )(\d*.\d*.\d*.\d*)(/\d*) \[(\d*)/(\d*)\] via (\d*.\d*.\d*.\d*), (.*)', line)
			if(m):
				code=m.group(1)
				prefix=m.group(2)
				prefixlength=m.group(3)
				admindistance=m.group(4)
				metric=m.group(5)
				nexthop=m.group(6)
				interface=m.group(7)
				routes[prefix+prefixlength]=[code, admindistance, metric, nexthop, interface, '']
				continue
			# Match other route types (age and interface)
			m = re.search('^(.......)(\d*.\d*.\d*.\d*)(/\d*) \[(\d*)/(\d*)\] via (\d*.\d*.\d*.\d*), (.*), (.*)', line)
			if(m):
				code=m.group(1)
				prefix=m.group(2)
				prefixlength=m.group(3)
				admindistance=m.group(4)
				metric=m.group(5)
				nexthop=m.group(6)
				age=m.group(7)
				interface=m.group(8)
				routes[prefix+prefixlength]=[code, admindistance, metric, nexthop, interface, age]
				continue
			# Match the first half of routes that spill onto the next line (prefix and length)
			m = re.search('^(........)(\d*.\d*.\d*.\d*)(/\d*)', line)
			if(m):
				code=m.group(1)
				prefix=m.group(2)
				prefixlength=m.group(3)
				continue
			# Match the second half of routes that spill onto the next line (age and interface)
			m = re.search('^           \[(\d*)/(\d*)\] via (\d*.\d*.\d*.\d*), (.*), (.*)', line)
			if(m):
				admindistance=m.group(1)
				metric=m.group(2)
				nexthop=m.group(3)
				age=m.group(4)
				interface=m.group(5)
				routes[prefix+prefixlength]=[code, admindistance, metric, nexthop, interface, age]
				continue

			
	return(routes)

print("iproutediff - takes the output of two \"show ip route\" commands and notes the differences\n")
print("v0.1 alpha, By Foeh Mannay, September 2017\n")

filename = input("Enter filename of first 'show ip route' (A): ")
A = parse(filename)
if(A is None): 
	raise SystemExit("Error - unable to parse any routes from this file!\n")
	
filename = input("Enter filename of second 'show ip route' (B): ")
B = parse(filename)
if(B is None):
	raise SystemExit("Error - unable to parse any routes from this file!\n")

# Temporary swap variable to get over Python's restriction on editing a dictionary while
# iterating over it
Z = {}

# Compare the two route lists
for key in A.keys():
	if(key in B):
		changed = False
		# Check route type, AD, metric, nexthop & interface
		for i in range(1,5):
			if(A[key][i] != B[key][i]):
				changed = True
		if(changed):
			print ("\nChanged:\n")
			print ("<<< " + A[key][0] + key + " [" + A[key][1] + "/" + A[key][2] + "] via " + A[key][3] + " " + A[key][4] + " " + A[key][5])
			print (">>> " + B[key][0] + key + " [" + B[key][1] + "/" + B[key][2] + "] via " + B[key][3] + " " + B[key][4] + " " + B[key][5] + "\n")
		changed = False
		del B[key]
	else:
		Z[key] = A[key]

A = Z

# Enumerate any routes removed
if(len(A) > 0):
	print ("\nRemoved:\n")
	for key in A.keys():
		print ("<<< " + A[key][0] + key + " [" + A[key][1] + "/" + A[key][2] + "] via " + A[key][3] + " " + A[key][4] + " " + A[key][5] + "\n")
else:
	print ("\nNo routes removed.\n")

# Enumerate any routes added
if(len(B) > 0):
	print ("\nAdded:\n")
	for key in B.keys():
		print (">>> " + B[key][0] + key + " [" + B[key][1] + "/" + B[key][2] + "] via " + B[key][3] + " " + B[key][4] + " " + B[key][5] + "\n")
else:
	print ("\nNo routes added.\n")

