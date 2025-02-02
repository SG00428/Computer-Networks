from scapy.all import sniff, IP, UDP, TCP, IPv6, Raw
from collections import defaultdict
import json
from pprint import pprint

# Global variables for metrics
port_packets = []
unique_conn_to_ims = defaultdict(int)
all_ims_packets = []
ims_dst_packets = []
super_users = 0
total_packets = 0
total_data = 0
course_names = []  # List to store course names


def traffic_packet(packet):
    """Filters out localhost and multicast traffic"""
    if IP in packet and (packet[IP].src == "127.0.0.1" or packet[IP].dst == "127.0.0.1"):
        return True
    if IPv6 in packet and (packet[IPv6].src == "::1" or packet[IPv6].dst == "::1"):
        return True
    if (IP in packet and packet[IP].dst == "224.0.0.251") or (IPv6 in packet and packet[IPv6].dst == "ff02::fb"):
        return True
    if UDP in packet and packet[UDP].dport == 5353:
        return True
    return False


def question_2(packet):
    """Packet handler for IMS traffic analysis."""
    global port_packets, unique_conn_to_ims, all_ims_packets, ims_dst_packets, super_users, total_packets, total_data, course_names

    if traffic_packet(packet):
        return

    total_packets += 1
    total_data += len(packet)

    ims_ip = "10.0.137.79"

    IPv = IP if IP in packet else IPv6 if IPv6 in packet else None
    if IPv:
        src_ip = packet[IPv].src
        dst_ip = packet[IPv].dst

        if dst_ip == ims_ip:
            ims_dst_packets.append(packet)
            all_ims_packets.append(packet)

        if src_ip == ims_ip:
            all_ims_packets.append(packet)

        protocol = TCP if TCP in packet else UDP if UDP in packet else None
        if protocol:
            src_port = packet[protocol].sport
            dst_port = packet[protocol].dport
            if dst_ip == ims_ip:
                unique_conn_to_ims[f"{src_ip}:{src_port} -> {dst_ip}:{dst_port}"] += 1

        if protocol and (packet[protocol].sport == 4321 or packet[protocol].dport == 4321):
            port_packets.append(packet)

        if Raw in packet:
            payload = packet[Raw].load.decode(errors="ignore")
            super_users += payload.lower().count("superuser")

            # Extract course registration packet
            if b"course" in bytes(packet[Raw].load):  # Check if "course" is in the raw payload
                course_name = payload.split("course")[1].split()[0]  # This is a basic extraction, adjust as needed
                course_names.append(course_name)
                print(f"Course Registration Packet: {packet[Raw].load}")

    print(packet.summary())


def log_question2_metrics():
    """Logs the results from question 2 packet capture"""
    global port_packets, unique_conn_to_ims, all_ims_packets, ims_dst_packets, super_users, total_packets, total_data, course_names

    print("\n--- IMS Packet Metrics ---")

    print("\nPackets Destined to IMS Server:")
    for packet in ims_dst_packets:
        print(packet.summary())

    print("\nUnique Connections to IMS Server:")
    pprint(unique_conn_to_ims)

    print("\nPackets Transferred on Port 4321:")
    for packet in port_packets:
        print(packet.summary())

    print("\nSummary:")
    print(f"Total IMS Packets: {len(all_ims_packets)}")
    print(f"Total Data Transferred on Port 4321: {sum(len(pkt) for pkt in port_packets)} bytes")
    print(f"Total SuperUser References: {super_users}")
    
    # Print all course names at the end
    print("\nCourse Names Registered:")
    for course in set(course_names):  # Using set to avoid duplicate course names
        print(course)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Packet capture and IMS analysis")
    parser.add_argument("-f", "--file", type=str, required=True, help="PCAP file to read")
    args = parser.parse_args()

    try:
        print("Starting packet sniffing from PCAP file...")
        sniff(offline=args.file, prn=question_2, store=False)
        log_question2_metrics()
    except KeyboardInterrupt:
        print("Packet capture interrupted.")


if __name__ == "__main__":
    main()
