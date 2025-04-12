# Question 2

## Instructions:
   
Run the topology with integrated NAT and automatic testing by executing:
   ```bash
   sudo python3 Q2.py

## Output Files

After each test set completes, the results are written to separate text files:

- **`output_a.txt`**: This file contains the results for **internal to external traffic**:
    - Ping results from **H1 to H5**.
    - Ping results from **H2 to H3**.

- **`output_b.txt`**: This file contains the results for **external to internal traffic**:
    - Ping results from **H8 to H1**.
    - Ping results from **H6 to H2**.

- **`output_c.txt`**: This file contains the **bandwidth measurements** from the iPerf3 tests:
    - The file includes the results of **3 separate tests**, each lasting **120 seconds**:
        - iPerf3 tests from **H6 (client)** to **H1 (server)**.
        - iPerf3 tests from **H2 (client)** to **H8 (server)**.

Each of these files will be automatically updated with the respective results after the tests are executed.

