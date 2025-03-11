from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
import time
import os

# ✅ Choose congestion control algorithm
print("Select congestion control algorithm: 1. Reno  2. BIC  3. HTCP")
cc_choice = int(input("Enter number (1/2/3): "))
congestion_control = {1: "reno", 2: "bic", 3: "htcp"}.get(cc_choice, "reno")

# ✅ Choose experiment case
print("Select experiment case: P, Q, R, S")
experiment_case = input("Enter case (P/Q/R/S): ").upper()

class NetworkTopology(Topo):
    def build(self):
        # ✅ Hosts
        H1 = self.addHost('H1')
        H2 = self.addHost('H2')
        H3 = self.addHost('H3')
        H4 = self.addHost('H4')
        H5 = self.addHost('H5')
        H6 = self.addHost('H6')
        H7 = self.addHost('H7')

        # ✅ Switches
        S1 = self.addSwitch('S1')
        S2 = self.addSwitch('S2')
        S3 = self.addSwitch('S3')
        S4 = self.addSwitch('S4')

        # ✅ Host-to-Switch Links
        self.addLink(H1, S1)
        self.addLink(H2, S1)
        self.addLink(H3, S2)
        self.addLink(H4, S3)
        self.addLink(H5, S3)
        self.addLink(H6, S4)
        self.addLink(H7, S4)

        # ✅ Switch-to-Switch Links with Bandwidth Constraints
        self.addLink(S1, S2, bw=100)
        self.addLink(S2, S3, bw=50)
        self.addLink(S3, S4, bw=100)

def run_experiment():
    setLogLevel('info')
    net = Mininet(topo=NetworkTopology())
    net.start()

    info("*** Starting iperf3 server on H7\n")
    H7 = net.get('H7')
    H7.cmd('iperf3 -s -p 5202 &')

    pcap_folder = "./pcaps_Q1"
    os.system(f'mkdir -p {pcap_folder}')  # ✅ Ensure PCAP folder exists

    # ✅ Define scenarios
    scenarios = {
        "P": ['H3'],  
        "Q": ['H1', 'H2'],  
        "R": ['H1', 'H3'],  
        "S": ['H1', 'H3', 'H4']
    }

    if experiment_case not in scenarios:
        print("Invalid experiment case. Exiting.")
        net.stop()
        return

    clients = scenarios[experiment_case]
    info(f"*** Running experiment {experiment_case} with {congestion_control} ***\n")

    # ✅ Start TCPdump on server and clients
    tcpdump_processes = {}
    for host in clients + ['H7']:  
        h = net.get(host)
        pcap_file = f"{pcap_folder}/{congestion_control}_{experiment_case}.pcap"
        tcpdump_processes[h] = h.popen(f"sudo tcpdump -i {h.defaultIntf()} -w {pcap_file} port 5202 > /tmp/tcpdump_{h}.log 2>&1 &", shell=True)

    
    time.sleep(3)  # ✅ Give TCPdump enough time to start

    # ✅ Start iperf3 clients
    client_processes = {}
    for client in clients:
        h_client = net.get(client)
        client_processes[h_client] = h_client.popen(f'iperf3 -c {H7.IP()} -p 5202 -b 10M -P 10 -t 30 -C {congestion_control}', shell=True)

    # ✅ Wait for all clients to complete execution (timeout increased to 40 sec)
    start_time = time.time()
    while any(p.poll() is None for p in client_processes.values()):
        if time.time() - start_time > 40:  # Max wait 40 sec
            info("*** Timeout reached, terminating clients\n")
            for p in client_processes.values():
                p.terminate()
            break
        time.sleep(1)

    info("*** Stopping TCPdump\n")
    os.system("pkill -f tcpdump")  # ✅ Ensure TCPdump is properly terminated
    
    time.sleep(3)  # ✅ Ensure PCAP files are written before moving

    # ✅ Check if PCAP files exist before moving
    if any(os.path.exists(f"{pcap_folder}/{congestion_control}_{experiment_case}.pcap") for h in clients + ['H7']):
        os.system(f'mv {pcap_folder}/*.pcap {pcap_folder}/')
        info("*** PCAP files moved successfully! ***\n")
    else:
        info("*** Warning: No PCAP files found! Check TCPDump or Iperf3 setup. ***\n")

    info("*** Stopping Network\n")
    net.stop()

# ✅ Start experiment after user input
run_experiment()
