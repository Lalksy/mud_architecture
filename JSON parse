import json
import os
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
#pprint(inaction)
ip = d["ietf-acl:access-list"]["access-list-entries"]["ace"][0]["matches"]["ietf-mud:controller"]
#pprint(ip)
#S = s + ip
#pprint(S)
# DROP FORWARD PACKETS
f2 = "sudo iptables --policy FORWARD DROP"
# OUTGOING PACKETS FOR ALLOWED DESTINATION
O1 = "sudo iptables -A OUTPUT -p tcp -d 10.10.10.10 -j ACCEPT"
# DROP OUTPUT PACKETS 
O2 = "sudo iptables --policy OUTPUT DROP"
# ACCEPT ONLY TCP PACKETS AT PORT 102 FROM ALLOWED IP ADDRESS
I1 = "sudo iptables -A INPUT -p tcp --dport 102 -s 10.10.10.10 -j ACCEPT"
# DROP ALL OTHER INPUT PACKETS
I2 = "sudo iptables --policy INPUT DROP"

os.system(I1)
os.system(O1)
os.system(f2)
os.system(O2)
os.system(I2)
