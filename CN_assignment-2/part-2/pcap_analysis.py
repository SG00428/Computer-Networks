import dpkt
import datetime
import matplotlib.pyplot as plt
import os
from collections import defaultdict
from tqdm import tqdm

def plot_tcp_durations(start_timestamps, connection_times, attack_begin, attack_finish, pcap_filename, output_folder):
    if not start_timestamps:
        print(f"No connection data to plot for {pcap_filename}")
        return

    plt.figure(figsize=(12, 6))
    plt.scatter(start_timestamps, connection_times, s=1)
    plt.xlabel("Connection Start Time (seconds)")
    plt.ylabel("Connection Duration (seconds)")
    plt.title("TCP Connection Durations")
    plt.grid(True)

    plt.axvline(x=attack_begin, color='red', linestyle='--', label='Attack Start')
    plt.axvline(x=attack_finish, color='green', linestyle='--', label='Attack End')
    plt.legend()
    plt.show()

pcap_path = 'syn_attack.pcap'
attack_begin = 20.0  # Attack start time
attack_finish = 120.0  # Attack end time
output_folder_graphs = "tcp_duration_graphs"  

os.makedirs(output_folder_graphs, exist_ok=True)  
tcp_connections = defaultdict(lambda: {'start_timestamp': None, 'close_timestamp': None})  

with open(pcap_path, 'rb') as file:
    pcap_reader = dpkt.pcap.Reader(file)  
    first_pkt_timestamp = None  

    for timestamp, packet_data in tqdm(pcap_reader, desc="Processing packets"):  
        ethernet_frame = dpkt.ethernet.Ethernet(packet_data)  
        
        if isinstance(ethernet_frame.data, dpkt.ip.IP):  
            ip_packet = ethernet_frame.data
            
            if isinstance(ip_packet.data, dpkt.tcp.TCP):  
                tcp_segment = ip_packet.data
                connection_key = (ip_packet.src, ip_packet.dst, tcp_segment.sport, tcp_segment.dport)  

                if first_pkt_timestamp is None:  
                    first_pkt_timestamp = datetime.datetime.utcfromtimestamp(timestamp)  

                current_packet_timestamp = datetime.datetime.utcfromtimestamp(timestamp)  

                if tcp_segment.flags & dpkt.tcp.TH_SYN:  
                    if tcp_connections[connection_key]['start_timestamp'] is None:
                        tcp_connections[connection_key]['start_timestamp'] = current_packet_timestamp

                if tcp_segment.flags & dpkt.tcp.TH_FIN and tcp_segment.flags & dpkt.tcp.TH_ACK:  
                    tcp_connections[connection_key]['fin_ack_timestamp'] = current_packet_timestamp

                if tcp_segment.flags & dpkt.tcp.TH_RST:  
                    tcp_connections[connection_key]['close_timestamp'] = current_packet_timestamp

                if tcp_segment.flags & dpkt.tcp.TH_ACK and 'fin_ack_timestamp' in tcp_connections[connection_key]:  
                    if current_packet_timestamp > tcp_connections[connection_key]['fin_ack_timestamp']:
                        tcp_connections[connection_key]['close_timestamp'] = current_packet_timestamp

    tcp_durations = []
    tcp_start_timestamps = []

    for conn_key, conn_info in tcp_connections.items():  
        if conn_info['start_timestamp'] is None:
            continue
        start_time = conn_info['start_timestamp']  
        close_time = conn_info.get('close_timestamp')  

        if close_time:  
            duration = (close_time - start_time).total_seconds()
        else:
            duration = 100.0  

        tcp_durations.append(duration)  
        tcp_start_timestamps.append((start_time - first_pkt_timestamp).total_seconds())  

    plot_tcp_durations(tcp_start_timestamps, tcp_durations, attack_begin, attack_finish, os.path.basename(pcap_path), output_folder_graphs)
