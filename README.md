# Tomasulo Algorithm Simulator

A simulation of Tomasulo's algorithm for a simplified RISC architecture without speculation. Developed as part of a Computer Architecture course project.

## 👥 Authors

- Eman AbdElHady  
- Ebram Thabet

## 📌 Project Overview

This project implements a backend and frontend simulation of Tomasulo’s algorithm, focusing on dynamic instruction scheduling and out-of-order execution. The simulator models instruction issue, execution, and write-back stages, while managing data hazards and branch prediction.

---

## ✅ Assumptions

- **Single Issue**: One instruction is issued per cycle.
- **No Syntax Errors**: The simulator assumes all input instructions are syntactically valid.
- **Cycle Indexing**: Simulation begins at **cycle 1** (not cycle 0).

---

## ✔️ Features & Functionality

- ✅ Accurate execution of all supported instructions  
- ✅ Correct handling of structural, data, and control hazards  
- ✅ Accurate **misprediction rate** computation  
- ✅ Precise calculation of **total cycles** taken  
- ✅ Reliable **IPC (Instructions Per Cycle)** metric  

---

## 🚀 Getting Started

### 🧱 Prerequisites

- C++17 or later
- A C++ compiler (e.g., `g++`)
- GUI is provided by PyQt

### 🛠️ Build and Run (Console Version)

```bash
# Clone the repository
git clone https://github.com/yourusername/tomasulo-simulator.git
cd tomasulo-simulator

# Compile the code
g++ -std=c++17 -o tomasulo_simulator main.cpp simulator.cpp instruction.cpp

# Run the simulator with input file
./tomasulo_simulator input.txt
