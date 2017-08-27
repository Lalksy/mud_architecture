#!/usr/bin/python

"""
This example shows how to create an empty Mininet object
(without a topology object) and add nodes to it manually.
"""

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def emptyNet():

    "Create an empty network and add nodes to it."

    net = Mininet( controller=Controller )

    info( '*** Adding controller\n' )
    net.addController( 'c0' )

    info( '*** Adding hosts\n' )
    h1 = net.addHost( 'h1', ip='10.0.0.1' )
    h2 = net.addHost( 'h2', ip='10.0.0.2' )
    h3 = net.addHost( 'h3', ip='10.0.0.3' )
    
    info( '*** Adding switch\n' )
    s3 = net.addSwitch( 's3' )

    info( '*** Creating links\n' )
    net.addLink( h1, s3 )
    net.addLink( h2, s3 )
    net.addLink( h3, s3 )
    
    info( '*** Starting network\n')
    net.start()

    h1.cmdPrint('sudo radiusd -X > radbug.txt 2>&1 &')
    h1.cmd('sleep 15')
    h3.cmdPrint('python -m SimpleHTTPServer 80 &')
    h3.cmd('sleep 5')
    h2.cmdPrint('sudo echo "User-Name=Merkle, User-Password=MUDinmud, Cisco-MUD-URI=http://10.0.0.3/mud/lighting-example.json" | /usr/local/bin/radclient -x 10.0.0.1 auth testingMUD')

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()
