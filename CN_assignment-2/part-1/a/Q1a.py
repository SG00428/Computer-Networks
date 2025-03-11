from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
import time
import os

class CustomTopology(Topo):
    def build(self):
        H1 = self.addHost('H1')
        H2 = self.addHost('H2')
        H3 = self.addHost('H3')
        H4 = self.addHost('H4')
        H5 = self.addHost('H5')
        H6 = self.addHost('H6')
        H7 = self.addHost('H7')  # Server

        S1 = self.addSwitch('S1')
        S2 = self.addSwitch('S2')
        S3 = self.addSwitch('S3')
        S4 = self.addSwitch('S4')

        self.addLink(H1, S1)
        self.addLink(H2, S1)
        self.addLink(H3, S2)
        self.addLink(H4, S3)
        self.addLink(H5, S3)
        self.addLink(H6, S4)
        self.addLink(H7, S4)

        self.addLink(S1, S2, bw=100)
        self.addLink(S2, S3, bw=50)
        self.addLink(S3, S4, bw=100)

def run_experiment():
    topo = CustomTopology()
    net = Mininet(topo=topo, controller=Controller, link=TCLink)
    net.start()

    server = net.get('H7')
    client = net.get('H1')

    server.cmd('iperf3 -s -p 5202 &')
    time.sleep(2)  # Wait for the server to start

    congestion_schemes = ['reno', 'bic', 'htcp']
    pcap_files = []

    for cc in congestion_schemes:
        print(f"\nRunning experiment with {cc} congestion control...")
        pcap_file = f"{cc}.pcap"
        pcap_files.append(pcap_file)

        # Start tcpdump on H7 to capture packets
        server.cmd(f'tcpdump -i any -w {pcap_file} port 5202 &')
        time.sleep(1)

        # Run iperf3 client from H1 to H7
        client.cmd(f'iperf3 -c {server.IP()} -p 5202 -b 10M -P 10 -t 50 -C {cc}')
     
        # Stop tcpdump
        server.cmd("pkill -f tcpdump")
        time.sleep(2)  # Ensure capture is saved

    print("\nPCAP files captured. Analyzing data...\n")
    
    # Run PCAP analyzer
    os.system("python3 pcap_analyzer.py")

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_experiment()
