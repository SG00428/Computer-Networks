# Packet Sniffer

## Overview:
- **Part 1**: A network packet sniffer written in C++ using `libpcap`.
- **Part 2**: IMS traffic analysis using Python and `scapy`.

## Prerequisites
Ensure you have the following installed before running the code:
- **Part 1:**
  - `g++`
  - `libpcap` (Install using `sudo apt-get install libpcap-dev` on Linux)
- **Part 2:**
  - Python 3
  - Required Python packages: Install using `pip install scapy`
  - `tcpreplay` (Install using `sudo apt-get install tcpreplay` on Linux)

## Setup & Execution

### Part 1: Packet Sniffer (C++)

#### Step 1: Compile and Run Packet Sniffer
**In Terminal 1:**
```sh
cd packet_sniffer
g++ -o part1 part1.cpp -lpcap
sudo ./part1
```

#### Step 2: Replay Network Packets
**In Terminal 2:**
```sh
cd packet_replayer
sudo tcpreplay -i eth0 --topspeed 0.pcap
```

#### Step 3: Process Packets (Optional)
**In Terminal 1:**
```sh
python part1.py
```
This will store the png format histogram

---

### Part 2: IMS Traffic Analysis (Python)

#### Step 1: Start Packet Sniffing
**In Terminal 1:**
```sh
cd sniffer
sudo python3 part-2.py -f "0.pcap"
```

#### Step 2: Replay Network Packets
**In Terminal 2:**
```sh
cd replayer
sudo tcpreplay --intf1=eth0 0.pcap
```

## Output & Logs
- **Part 1:** Outputs packet statistics including packet size distribution and flow analysis. Results are stored in `packet_statistics.txt` and `histogram_data.csv`.
- **Part 2:** Logs IMS traffic metrics, including unique connections, packet details, and course registrations.

## Notes
- Ensure you have `sudo` privileges to capture packets and replay traffic.
- Modify `eth0` to match your network interface if needed (Use `ifconfig` or `ip a` to check interfaces).

