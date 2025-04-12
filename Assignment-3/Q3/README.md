# Assignment3 Part3

This part of the repository simulates the **Distance Vector Routing** algorithm using C source files.

## 📦 Requirements

- GCC or any compatible C compiler  
- Operating System:  
  - Linux  
  - Windows (with [WSL](https://learn.microsoft.com/en-us/windows/wsl/) / [MinGW](http://www.mingw.org/) / similar)

## 🛠️ Compilation and Execution

### 🔧 Compilation

To compile the simulation, run:

```bash
gcc -o dvr distance_vector.c node0.c node1.c node2.c node3.c -Wall
This command generates an executable named dvr.

▶️ Running the Simulation
You can run the simulation with or without an optional trace level parameter:

bash
Copy
Edit
./dvr
or, with detailed tracing:

bash
Copy
Edit
./dvr 2
🔍 Trace Levels
Level	Description
0	Minimal output: Final routing tables and key events
1	Basic tracing: Packet transmissions and table updates
2	Detailed tracing: Packet contents and decisions
3	Full debug: Internal steps and queuing details
