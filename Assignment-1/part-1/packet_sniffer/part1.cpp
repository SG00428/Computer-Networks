#include <iostream>
#include <pcap.h>
#include <vector>
#include <map>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <climits>
#include <csignal>
#include <fstream>

using namespace std;

// Structure to hold packet statistics
struct PacketStats {
    int totalPackets = 0;
    long long totalBytes = 0;
    int minPacketSize = INT_MAX;
    int maxPacketSize = 0;
    vector<int> packetSizes;
    map<int, int> sizeDistribution; // Distribution of packet sizes
    map<string, long long> flowData; // Data transfer per flow
    map<string, int> sourceIPCount; // Count of packets from each source IP
    map<string, int> destIPCount; // Count of packets to each destination IP
};

// Global variables
volatile sig_atomic_t stopCaptureFlag = 0;
pcap_t *pcapHandle = nullptr;

// Signal handler to catch Ctrl+C interrupt
void handleInterruptSignal(int signum) {
    stopCaptureFlag = 1;
    if (pcapHandle) {
        pcap_breakloop(pcapHandle); // Stop packet capture
    }
}

// Callback to process each captured packet
void processPacket(u_char *userData, const struct pcap_pkthdr *pkthdr, const u_char *packet) {
    PacketStats *stats = (PacketStats *)userData;
    
    int packetSize = pkthdr->len;
    stats->totalPackets++;
    stats->totalBytes += packetSize;
    stats->minPacketSize = min(stats->minPacketSize, packetSize);
    stats->maxPacketSize = max(stats->maxPacketSize, packetSize);
    stats->packetSizes.push_back(packetSize);
    stats->sizeDistribution[packetSize]++;

    // Extract IP header
    struct ip *ipHeader = (struct ip *)(packet + 14); // Skip Ethernet header
    char sourceIP[INET_ADDRSTRLEN], destIP[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &ipHeader->ip_src, sourceIP, INET_ADDRSTRLEN);
    inet_ntop(AF_INET, &ipHeader->ip_dst, destIP, INET_ADDRSTRLEN);

    // Extract TCP header (for port numbers)
    struct tcphdr *tcpHeader = (struct tcphdr *)(packet + 14 + (ipHeader->ip_hl << 2));
    uint16_t sourcePort = ntohs(tcpHeader->th_sport);
    uint16_t destPort = ntohs(tcpHeader->th_dport);

    string flowKey = string(sourceIP) + ":" + to_string(sourcePort) + " -> " + string(destIP) + ":" + to_string(destPort);

    // Track flow data
    stats->flowData[flowKey] += packetSize;
    stats->sourceIPCount[sourceIP]++;
    stats->destIPCount[destIP]++;

    cout << "Captured packet! Size: " << packetSize << " bytes | Total packets: " << stats->totalPackets << endl;

    if (stopCaptureFlag) {
        pcap_breakloop(pcapHandle); // Stop capture on signal
    }
}

int main() {
    char errorBuffer[PCAP_ERRBUF_SIZE];

    // Discover available network interfaces
    pcap_if_t *allDevices, *device;
    if (pcap_findalldevs(&allDevices, errorBuffer) == -1) {
        cerr << "Failed to find network interfaces: " << errorBuffer << endl;
        return 1;
    }

    device = allDevices;
    if (!device) {
        cerr << "No network interfaces available!" << endl;
        return 1;
    }
    cout << "Using interface: " << device->name << endl;

    // Open device for live packet capture
    pcapHandle = pcap_open_live(device->name, BUFSIZ, 1, 1000, errorBuffer);
    if (!pcapHandle) {
        cerr << "Failed to open device: " << errorBuffer << endl;
        return 1;
    }

    pcap_freealldevs(allDevices); // Free memory of devices list
    signal(SIGINT, handleInterruptSignal); // Setup signal handler for Ctrl+C

    PacketStats stats;
    cout << "Capturing packets... Press Ctrl+C to stop.\n";

    // Begin packet capture loop
    pcap_loop(pcapHandle, 0, processPacket, (u_char *)&stats);

    pcap_close(pcapHandle); // Close the pcap handle when done

    // Calculate the average packet size
    double avgPacketSize = (stats.totalPackets > 0) ? (double)stats.totalBytes / stats.totalPackets : 0;

    // Save packet size histogram for Python plotting
    ofstream histogramFile("histogram_data.csv");
    for (const auto &[size, frequency] : stats.sizeDistribution) {
        histogramFile << size << "," << frequency << "\n";
    }
    histogramFile.close();

    // Save statistics to a file
    ofstream statsFile("packet_statistics.txt");
    if (!statsFile) {
        cerr << "Failed to open output file" << endl;
        return 1;
    }

    statsFile << "Total Packets: " << stats.totalPackets << endl;
    statsFile << "Total Data Transferred: " << stats.totalBytes << " bytes" << endl;
    statsFile << "Min Packet Size: " << stats.minPacketSize << " bytes" << endl;
    statsFile << "Max Packet Size: " << stats.maxPacketSize << " bytes" << endl;
    statsFile << "Avg Packet Size: " << avgPacketSize << " bytes" << endl;

    // Write flow statistics
    statsFile << "\nUnique Source-Destination Flows:" << endl;
    for (const auto &flow : stats.flowData) {
        statsFile << flow.first << " -> " << flow.second << " bytes transferred" << endl;
    }

    // Write source IP counts
    statsFile << "\nSource IP Flow Counts:" << endl;
    for (const auto &flow : stats.sourceIPCount) {
        statsFile << flow.first << " : " << flow.second << " flows" << endl;
    }

    // Write destination IP counts
    statsFile << "\nDestination IP Flow Counts:" << endl;
    for (const auto &flow : stats.destIPCount) {
        statsFile << flow.first << " : " << flow.second << " flows" << endl;
    }

    // Find the flow with the maximum data transferred
    string maxFlow;
    long long maxDataTransferred = 0;
    for (const auto &flow : stats.flowData) {
        if (flow.second > maxDataTransferred) {
            maxDataTransferred = flow.second;
            maxFlow = flow.first;
        }
    }

    statsFile.close();

    // Display statistics and final summary
    cout << "\nCapture finished.\n";
    cout << "Total Packets: " << stats.totalPackets << endl;
    cout << "Total Data Transferred: " << stats.totalBytes << " bytes" << endl;
    cout << "Min Packet Size: " << stats.minPacketSize << " bytes" << endl;
    cout << "Max Packet Size: " << stats.maxPacketSize << " bytes" << endl;
    cout << "Avg Packet Size: " << avgPacketSize << " bytes" << endl;
    cout << "Flow with most data: " << maxFlow << " with " << maxDataTransferred << " bytes" << endl;
    cout << "Histogram saved as histogram_data.csv." << endl;
    cout << "Source-Destination Pair Analysis & IP Flow Analysis saved to packet_statistics.txt" << endl;

    return 0;
}



