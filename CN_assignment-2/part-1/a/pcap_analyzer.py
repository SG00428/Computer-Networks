import pyshark

def analyze_pcap(pcap_file):
    print(f"\nAnalyzing {pcap_file}...")
    capture = pyshark.FileCapture(pcap_file, display_filter="tcp")

    total_bytes = 0
    packet_count = 0
    lost_packets = 0
    max_window_size = 0
    timestamps = []

    for packet in capture:
        try:
            total_bytes += int(packet.length)
            packet_count += 1

            if hasattr(packet.tcp, 'analysis_lost_segment'):
                lost_packets += 1

            if hasattr(packet.tcp, 'window_size'):
                max_window_size = max(max_window_size, int(packet.tcp.window_size))

            if hasattr(packet, 'sniff_time'):
                timestamps.append(float(packet.sniff_time.timestamp()))

        except AttributeError:
            continue

    capture.close()

    if timestamps:
        duration = timestamps[-1] - timestamps[0]
        throughput = (total_bytes * 8) / (duration * 1000000)  # Mbps
        goodput = ((total_bytes - (lost_packets * 1500)) * 8) / (duration * 1000000)  # Mbps
    else:
        throughput = 0
        goodput = 0

    loss_rate = (lost_packets / packet_count) * 100 if packet_count else 0

    print(f"Throughput: {throughput:.2f} Mbps")
    print(f"Goodput: {goodput:.2f} Mbps")
    print(f"Packet Loss Rate: {loss_rate:.2f}%")
    print(f"Maximum Window Size: {max_window_size} bytes\n")

def main():
    congestion_schemes = ['reno.pcap', 'bic.pcap', 'htcp.pcap']
    for pcap in congestion_schemes:
        analyze_pcap(pcap)

if __name__ == '__main__':
    main()
