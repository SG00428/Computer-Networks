from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
import time
import os

# ✅ Configurations (Automated Execution)
congestion_algorithms = ["reno", "bic", "htcp"]
experiment_cases = ["P", "Q", "R", "S"]
loss_values = [1, 5]
pcap_folder = "./pcaps_Q1d"
os.system(f'mkdir -p {pcap_folder}')  # ✅ Ensure PCAP folder exists

class NetworkTopology(Topo):
    def __init__(self, loss_percent):
        self.loss_percent = loss_percent  # ✅ Store loss percentage
        super().__init__()

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

        # ✅ Switch-to-Switch Links with Bandwidth & Loss
        self.addLink(S1, S2, bw=100)
        self.addLink(S2, S3, bw=50, loss=self.loss_percent)  # ✅ Loss introduced here
        self.addLink(S3, S4, bw=100)

def run_experiment(congestion_control, experiment_case, loss):
    setLogLevel('info')
    info(f"*** Running {congestion_control} with {loss}% packet loss ({experiment_case}) ***\n")
    net = Mininet(topo=NetworkTopology(loss))
    net.start()

    info("*** Starting iperf3 server on H7\n")
    H7 = net.get('H7')
    H7.cmd('iperf3 -s -p 5202 &')

    # ✅ Define scenarios
    scenarios = {
        "P": ['H3'],  
        "Q": ['H1', 'H2'],  
        "R": ['H1', 'H3'],  
        "S": ['H1', 'H3', 'H4']
    }
    clients = scenarios[experiment_case]
    info(f"*** Running experiment {experiment_case} with {congestion_control} ***\n")

    # ✅ Start TCPdump
    tcpdump_processes = {}
    for host in clients + ['H7']:  
        h = net.get(host)
        pcap_file = f"{pcap_folder}/{congestion_control}_{experiment_case}_loss{loss}.pcap"
        tcpdump_processes[h] = h.popen(f"sudo tcpdump -i {h.defaultIntf()} -w {pcap_file} port 5202 > /tmp/tcpdump_{h}.log 2>&1 &", shell=True)

    time.sleep(3)  # ✅ Give TCPdump time to start

    # ✅ Start iperf3 clients
    client_processes = {}
    for client in clients:
        h_client = net.get(client)
        client_processes[h_client] = h_client.popen(f'iperf3 -c {H7.IP()} -p 5202 -b 10M -P 10 -t 30 -C {congestion_control}', shell=True)

    # ✅ Wait for completion
    start_time = time.time()
    while any(p.poll() is None for p in client_processes.values()):
        if time.time() - start_time > 40:  # Max wait 40 sec
            info("*** Timeout reached, terminating clients\n")
            for p in client_processes.values():
                p.terminate()
            break
        time.sleep(1)

    info("*** Stopping TCPdump\n")
    os.system("pkill -f tcpdump")  # ✅ Ensure TCPdump is terminated
    time.sleep(3)  # ✅ Ensure PCAP files are written

    info("*** Stopping Network\n")
    net.stop()

# ✅ Run all combinations
total_runs = len(congestion_algorithms) * len(experiment_cases) * len(loss_values)
current_run = 1

for cc in congestion_algorithms:
    for case in experiment_cases:
        for loss in loss_values:
            info(f"\n*** Running Experiment {current_run}/{total_runs}: {cc} - {case} - {loss}% loss ***\n")
            run_experiment(cc, case, loss)
            current_run += 1

info("\n*** All experiments completed! PCAPs stored in pcaps_Q1d. ***\n")
