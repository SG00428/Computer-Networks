from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from mininet.clean import cleanup
import os

class LoopTopo(Topo):
    def build(self):
        # Add switches
        s1, s2, s3, s4 = [self.addSwitch(f's{i}') for i in range(1, 5)]
        
        # Add hosts
        hosts = {}
        for i in range(1, 9):
            ip = f"10.0.0.{i}/24"
            hosts[f'h{i}'] = self.addHost(f'h{i}', ip=ip)
        
        # Host-Switch links with 5ms delay
        self.addLink(hosts['h1'], s1, delay='5ms')
        self.addLink(hosts['h2'], s1, delay='5ms')
        self.addLink(hosts['h3'], s2, delay='5ms')
        self.addLink(hosts['h4'], s2, delay='5ms')
        self.addLink(hosts['h5'], s3, delay='5ms')
        self.addLink(hosts['h6'], s3, delay='5ms')
        self.addLink(hosts['h7'], s4, delay='5ms')
        self.addLink(hosts['h8'], s4, delay='5ms')
        
        # Inter-switch links with 7ms delay
        self.addLink(s1, s2, delay='7ms')
        self.addLink(s2, s3, delay='7ms')
        self.addLink(s3, s4, delay='7ms')
        self.addLink(s4, s1, delay='7ms')
        self.addLink(s1, s3, delay='7ms')  # This creates a loop in the network

def ensure_clean_environment():
    """Make sure we start with a clean environment"""
    print("*** Cleaning up any previous Mininet resources...")
    cleanup()
    os.system('sudo mn -c')  # Additional cleanup
    os.system('sudo killall -9 controller')  # Kill any running controller

def run_part_a():
    """Part A: Demonstrate the network loop problem"""
    topo = LoopTopo()
    # Use OVSSwitch with failMode='standalone' to work without a controller
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, controller=None)
    
    net.start()
    
    # Configure switches to operate in standalone mode
    for switch in net.switches:
        switch.cmd('ovs-vsctl set bridge {} fail-mode=standalone'.format(switch.name))
    
    print("*** Dumping network connections:")
    dumpNodeConnections(net.hosts)
    
    print("\n*** Testing network connectivity (with loops - expect issues):")
    print("Testing h3 -> h1:")
    h3, h1 = net.get('h3', 'h1')
    print(h3.cmd('ping -c 3 ' + h1.IP()))
    
    print("\nTesting h5 -> h7:")
    h5, h7 = net.get('h5', 'h7')
    print(h5.cmd('ping -c 3 ' + h7.IP()))
    
    print("\nTesting h8 -> h2:")
    h8, h2 = net.get('h8', 'h2')
    print(h8.cmd('ping -c 3 ' + h2.IP()))
    
    print("\n*** Starting CLI:")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    
    # Make sure we start with a clean environment
    ensure_clean_environment()
    
    print("Running Part A: Demonstrating network loop problem")
    run_part_a()
    
    # Final cleanup
    ensure_clean_environment()
