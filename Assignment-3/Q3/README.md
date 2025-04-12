# Question 3

It simulates the **Distance Vector Routing** algorithm using C source files.

## Requirements

- GCC or compatible C compiler  
- Linux or Windows (with WSL, MinGW, or similar)

## Compilation and Execution

### Compilation

To compile the simulation:

```bash
gcc distance_vector.c node0.c node1.c node2.c node3.c -o distance_vector
```
This creates an executable named distance_vector.

Running the Simulation
You can run the simulation with an optional trace level parameter:

```bash
./distance_vector
```
Trace Levels

0	Minimal output: Final routing tables and key events
1	Basic tracing: Packet transmissions and table updates
2	Detailed tracing: Packet contents and decisions
3	Full debug: Internal steps and queuing details
