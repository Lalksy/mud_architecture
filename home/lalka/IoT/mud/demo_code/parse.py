import json
import os
import socket
from pprint import pprint

with open('plc-example.json') as data_file:
 d = json.load(data_file)

#pprint(d)
ace = d["ietf-acl:access-list"]["access-list-entries"]["ace"]
lport = d["ietf-acl:access-list"]["access-list-entries"]["ace"][0]["matches"]["destination-port-range"]["lower-port"]
#pprint(ace)

protocol = d["ietf-acl:access-list"]["access-list-entries"]["ace"][0]["matches"]["protocol"]
#pprint(protocol)

inaction = d["ietf-acl:access-list"]["access-list-entries"]["ace"][0]["actions"]["packet-handling"]
if inaction == 'permit' :
 inaction = "ACCEPT"
else :
 inaction = "DROP"
print(inaction)

ip = d["ietf-acl:access-list"]["access-list-entries"]["ace"][0]["matches"]["ietf-mud:controller"]
host = ip.split("//",1)[1]
host = host.split("/", 1)[0]
#print(host)
TranslatedIp = socket.gethostbyname(host)

#pprint(ip)
#S = s + ip
#pprint(S)

# By default DROP FORWARD PACKETS
f2 = "sudo iptables --policy FORWARD DROP"
print(f2)

# OUTGOING PACKETS FOR ALLOWED DESTINATION

O1 = "sudo iptables -A OUTPUT -p "+protocol+" -d "+TranslatedIp+" -j ACCEPT"
print(O1)

# By default DROP OUTPUT PACKETS 
O2 = "sudo iptables --policy OUTPUT DROP"
# ACCEPT ONLY TCP PACKETS AT PORT 102 FROM ALLOWED IP ADDRESS
print(O2)

I1 = "sudo iptables -A INPUT -p "+protocol+" --dport "+str(lport)+" -s "+TranslatedIp+" -j "+inaction
print(I1)

# By default DROP ALL OTHER INPUT PACKETS
I2 = "sudo iptables --policy INPUT DROP"
print(I1)

#os.system(I1)
#os.system(O1)
#os.system(f2)
#os.system(O2)
#os.system(I2)
