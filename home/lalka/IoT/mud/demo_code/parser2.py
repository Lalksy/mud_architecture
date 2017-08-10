import json
import os
import socket


with open('lighting-example.json') as data_file:
 d = json.load(data_file)

#print(d)

acl = d["ietf-access-control-list:access-lists"]["acl"]
#print(acl)
 
direction = []
ace = []
act = []
match = []
for i in range(1):
direction[i]  = acl[i]["acl-name"]
#print(direction)

ace[0] = acl[0]["access-list-entries"]["ace"][0]
#print(iace)

#input action
act = iace["actions"]["permit"] 

#inbound rules#################################################################
imatch  = iace["matches"]
#print(imatch)

#inbound port
iport = imatch["destination-port-range"]["lower-port"]
#print(iport)

#Source IP
sip = imatch["ietf-acl-dnsname:source-hostname"]
#print(sip)

#protocol
iproto = imatch["protocol"]
#print(iproto)
################################################################################
