from mininet.net import Mininet
from mininet.node import OVSController, OVSKernelSwitch
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.cli import CLI
import time
import os

# Clean previous Mininet state
os.system('mn -c')

class NATTopology(Topo):
    def build(self):
        s1 = self.addSwitch('s1', stp=True)
        s2 = self.addSwitch('s2', stp=True)
        s3 = self.addSwitch('s3', stp=True)
        s4 = self.addSwitch('s4', stp=True)

        h1 = self.addHost('h1', ip='10.1.1.2/24')
        h2 = self.addHost('h2', ip='10.1.1.3/24')
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')
        h9 = self.addHost('h9')  # NAT Gateway

        self.addLink(h1, h9, delay='5ms')
        self.addLink(h2, h9, delay='5ms')
        self.addLink(h9, s1, delay='5ms')

        self.addLink(h4, s2, delay='5ms')
        self.addLink(h3, s2, delay='5ms')
        self.addLink(h6, s3, delay='5ms')
        self.addLink(h5, s3, delay='5ms')
        self.addLink(h7, s4, delay='5ms')
        self.addLink(h8, s4, delay='5ms')

        self.addLink(s1, s2, delay='7ms')
        self.addLink(s3, s2, delay='7ms')
        self.addLink(s1, s3, delay='7ms')
        self.addLink(s1, s4, delay='7ms')
        self.addLink(s4, s3, delay='7ms')

def launch_network():
    net = Mininet(topo=NATTopology(), controller=OVSController,
                  switch=OVSKernelSwitch, link=TCLink)
    net.start()

    h1, h2, h9, h4, h3, h5, h6, h7, h8 = net.get('h1', 'h2', 'h9', 'h4', 'h3', 'h5', 'h6', 'h7', 'h8')

    for sw in ['s1', 's2', 's3', 's4']:
        net.get(sw).cmd(f'ovs-vsctl set Bridge {sw} stp_enable=true')

    # NAT setup
    h9.cmd('ip link add name br0 type bridge')
    h9.cmd('ip link set br0 up')
    h9.cmd('ip link set h9-eth0 master br0')
    h9.cmd('ip link set h9-eth1 master br0')
    h9.cmd('ip addr add 10.1.1.1/24 dev br0')

    h1.cmd('ip route add default via 10.1.1.1')
    h2.cmd('ip route add default via 10.1.1.1')

    for host in [h3, h4, h5, h6, h7, h8]:
        host.cmd('ip route add default via 10.0.0.1')

    h9.cmd('sysctl -w net.ipv4.ip_forward=1')
    h9.cmd('iptables -t nat -F')
    h9.cmd('iptables -t nat -A POSTROUTING -s 10.1.1.0/24 -o h9-eth2 -j MASQUERADE')

    h9.cmd("ip addr flush dev h9-eth0")
    h9.cmd("ip addr flush dev h9-eth1")
    h9.cmd("ip addr flush dev h9-eth2")

    h9.cmd('ip link add name br0 type bridge')
    h9.cmd('ip link set br0 up')
    h9.cmd('ip link set h9-eth0 master br0')
    h9.cmd('ip link set h9-eth1 master br0')
    h9.cmd('ip addr add 10.1.1.1/24 dev br0')

    h9.setIP('10.0.0.1/24', intf='h9-eth2')
    h9.cmd('ip addr add 172.16.10.10/24 dev h9-eth2')

    print("\n[Info] Waiting 30s for network stabilization...")
    time.sleep(30)

    net.pingAll()

    # Test A: Internal to External
    test_a_log = ""
    for i in range(3):
        test_a_log += f"\nRun {i+1}: h1 -> h5\n{h1.cmd('ping -c 4 10.0.0.6')}"
        test_a_log += f"\nRun {i+1}: h2 -> h3\n{h2.cmd('ping -c 4 10.0.0.4')}"

    with open('test_a_results.txt', 'w') as f:
        f.write(test_a_log)
    print("Results for Test A saved to test_a_results.txt")

    # Test B: External to Internal
    test_b_log = ""
    for i in range(3):
        test_b_log += f"\nRun {i+1}: h8 -> h1\n{h8.cmd('ping -c 4 10.1.1.2')}"
        test_b_log += f"\nRun {i+1}: h6 -> h2\n{h6.cmd('ping -c 4 10.1.1.3')}"

    with open('test_b_results.txt', 'w') as f:
        f.write(test_b_log)
    print("Results for Test B saved to test_b_results.txt")

    # Test C: iPerf3 Bandwidth Tests
    test_c_log = ""

    h1.cmd('iperf3 -s -D')
    time.sleep(2)
    for i in range(3):
        test_c_log += f"\niPerf3 Test {i+1}: h6 -> h1\n{h6.cmd('iperf3 -c 10.1.1.2 -t 120')}"
        time.sleep(3)
    h1.cmd('pkill iperf3')

    h8.cmd('iperf3 -s -D')
    time.sleep(2)
    for i in range(3):
        test_c_log += f"\niPerf3 Test {i+1}: h2 -> h8\n{h2.cmd('iperf3 -c 10.0.0.9 -t 120')}"
        time.sleep(3)
    h8.cmd('pkill iperf3')

    with open('test_c_results.txt', 'w') as f:
        f.write(test_c_log)
    print("Results for Test C saved to test_c_results.txt")

    print("\n[Shutdown] Tests completed. Cleaning up the network.")
    net.stop()

if __name__ == '__main__':
    launch_network()
