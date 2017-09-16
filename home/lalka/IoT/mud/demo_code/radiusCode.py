#!/usr/bin/python

'This example shows authentication of a station using certificate-based auth'

from mininet.net import Mininet
from mininet.node import  Controller, UserAP
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def topology():
    "Create a network."
    net = Mininet( controller=Controller, link=TCLink, accessPoint=UserAP, enable_wmediumd=True, enable_interference=True )

    print "*** Creating nodes"
    sta1 = net.addStation( 'sta1', encrypt='wpa2', config='key_mgmt=IEEE8021X,eap=TLS,identity="Merkle",ca_cert="/home/lalka/IoT/CA/mudCA.crt",client_cert="/home/lalka/IoT/CA/light.crt",private_key="/home/lalka/IoT/CA/light.key",eapol_flags=3', position='150,90,0')
    sta2 = net.addStation( 'sta2', radius_passwd='MUDinmud', encrypt='wpa2', radius_identity='Merkle', position='150,110,0' )
    ap1 = net.addAccessPoint( 'ap1', ssid='simplewifi', authmode='8021x', mode='a', channel='36', encrypt='wpa2', shared_secret='testingMUD', position='150,100,0' )
    c0 = net.addController('c0', controller=Controller, ip='127.0.0.1', port=6633 )

    print "*** Configuring Propagation Model"
    net.propagationModel("logDistancePropagationLossModel", exp=3.5)

    print "*** Configuring wifi nodes"
    net.configureWifiNodes()

    print "*** Associating Stations"
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)

    print "*** Starting network"
    net.build()
    c0.start()
    ap1.start( [c0] )

    print "*** Building graph"
    net.plotGraph(max_x=300, max_y=300)

    print "*** Running CLI"
    CLI( net )

    print "*** Stopping network"
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()
