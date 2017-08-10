import json
import os
import socket


with open('lighting-example.json') as data_file:
 d = json.load(data_file)

#print(d)

acl = d["ietf-access-control-list:access-lists"]["acl"]
#print(acl)
 
for i in range(len(acl)): # this loop with go through both the inbound and outbound
 direction = acl[i]["acl-name"]
 print(direction)
 ace = acl[i]["access-list-entries"]["ace"]

 for j in range(len(ace)):
  entry = ace[j]
  print (entry["rule-name"])
  #print(ace)

  #input action
  action = entry["actions"].keys()[0]
  if action == 'permit':
   action = 'ACCEPT'
  print(action)

  #rules
  #inbound port
  try:
   port = entry["matches"]["source-port-range"]["lower-port"]
  except:
   port = entry["matches"]["destination-port-range"]["lower-port"]
  print(port)

  #Source IP
  try:
   ip = entry["matches"]["ietf-acl-dnsname:source-hostname"]
  except:
   ip = entry["matches"]["ietf-acl-dnsname:destination-hostname"]
  print(ip)
  numIp = socket.gethostbyname(ip)
  

  #protocol
  protocol = entry["matches"]["protocol"]
  print(protocol)
  
  ##########################################################################
  I =  "sudo iptables -A INPUT -p "+protocol+" --dport "+str(port)+" -s "+numIp+" -j "+action
  O = "sudo iptables -A OUTPUT -p "+protocol+" --dport "+str(port)+" -d "+numIp+" -j "+action

f2 = "sudo iptables --policy FORWARD DROP"
I2 = "sudo iptables --policy INPUT DROP"
