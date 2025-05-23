from enum import Enum, auto
from typing import List, Dict, Tuple, Deque, Optional
from collections import deque, defaultdict
import sys

class InstCategory(Enum):
    LOAD = auto()
    STORE = auto()
    BEQ = auto()
    CALL = auto()
    ADDITION = auto()
    SUBTRACTION = auto()
    NOR = auto()
    MUL = auto()

class InstOp(Enum):
    LOAD = auto()
    STORE = auto()
    BEQ = auto()
    CALL = auto()
    RET = auto()
    ADD = auto()
    SUB = auto()
    NOR = auto()
    MUL = auto()

class Instruction:
    def __init__(self, inst_str: str, index: int):
        self.issue = 0
        self.exec_st = 0
        self.exec_end = 0
        self.wb = 0
        self.rd = 0
        self.rs = 0
        self.rt = 0
        self.imm = 0
        self.addr = 0
        self.category: Optional[InstCategory] = None
        self.oper: Optional[InstOp] = None
        self.index = index
        self.inst = inst_str
        self.op_str = ""
        
        tokens = inst_str.strip().replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
        if not tokens:
            raise ValueError("Empty instruction string")
        
        oper = tokens[0].lower()
        self.op_str = oper
        
        try:
            if oper == "load":
                self.category = InstCategory.LOAD
                self.oper = InstOp.LOAD
                self.rd = int(tokens[1][1:])
                self.imm = int(tokens[2])
                self.rs = int(tokens[3][1:])
            elif oper == "store":
                self.category = InstCategory.STORE
                self.oper = InstOp.STORE
                self.rt = int(tokens[1][1:])
                self.imm = int(tokens[2])
                self.rs = int(tokens[3][1:])
            elif oper == "beq":
                self.category = InstCategory.BEQ
                self.oper = InstOp.BEQ
                self.rs = int(tokens[1][1:])
                self.rt = int(tokens[2][1:])
                self.imm = int(tokens[3])
                self.addr = self.imm
            elif oper == "call":
                self.category = InstCategory.CALL
                self.oper = InstOp.CALL
                self.imm = int(tokens[1])
                self.addr = self.imm
            elif oper == "ret":
                self.category = InstCategory.CALL
                self.oper = InstOp.RET
            elif oper == "add":
                self.category = InstCategory.ADDITION
                self.oper = InstOp.ADD
                self.rd = int(tokens[1][1:])
                self.rs = int(tokens[2][1:])
                self.rt = int(tokens[3][1:])
            elif oper == "sub":
                self.category = InstCategory.SUBTRACTION
                self.oper = InstOp.SUB
                self.rd = int(tokens[1][1:])
                self.rs = int(tokens[2][1:])
                self.rt = int(tokens[3][1:])
            elif oper == "nor":
                self.category = InstCategory.NOR
                self.oper = InstOp.NOR
                self.rd = int(tokens[1][1:])
                self.rs = int(tokens[2][1:])
                self.rt = int(tokens[3][1:])
            elif oper == "mul":
                self.category = InstCategory.MUL
                self.oper = InstOp.MUL
                self.rd = int(tokens[1][1:])
                self.rs = int(tokens[2][1:])
                self.rt = int(tokens[3][1:])
            else:
                raise ValueError(f"Unsupported instruction: {inst_str}")
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid instruction format: {inst_str} - {str(e)}")

class ReservationStation:
    def __init__(self, name: str, id: int, cycles_per_exec: int, cycles_per_addr: int):
        self.id = id
        self.name = name
        self.busy = False
        self.oper: Optional[InstOp] = None
        self.vj = 0
        self.vk = 0
        self.qj = 0
        self.qk = 0
        self.addr = 0
        self.cycles_per_exec = cycles_per_exec
        self.cycles_per_addr = cycles_per_addr
        self.rem_cycles_exec = 0
        self.rem_cycles_addr = 0
        self.instIndex = 0
        self.result = 0

class SystemState:
    def __init__(self, issue: int, register_stat: List[int]):
        self.issue = issue
        self.register_stat = register_stat.copy()

class Tomasulo:
    nStationTypes = 8
    nRegisters = 8

    def __init__(self, instructionFile: str, isDefaultHardware: bool, hardwareFile: str, pc: int):
        self.mem = [0] * (1 << 16)  # word addressable with word size of 16 bits
        self.registers = [0] * self.nRegisters
        self.program: List[Instruction] = []
        self.stations: List[List[ReservationStation]] = [[] for _ in range(self.nStationTypes)]
        self.idToRs: Dict[int, Tuple[int, int]] = {}
        self.registerStatusTable = [0] * self.nRegisters
        self.loadStoreQueue: Deque[int] = deque()
        self.states: Deque[SystemState] = deque()
        self.pc = pc  # Initial PC value
        self.cycle = 1
        self.numBne = 0
        self.misprediction = 0
        self.wbInsts = 0
        
        self.readInstFile(instructionFile)
        self.readHardware(isDefaultHardware, hardwareFile)

    def readInstFile(self, instFile: str):
        with open(instFile) as f:
            for idx, line in enumerate(f):
                if line.replace('\u00A0', ' ').replace('Â', ' ').strip():
                    inst = Instruction(line.strip(), idx)
                    self.program.append(inst)

    def readHardware(self, isDefault: bool, hardwareFile: str):
        st = ["load", "store", "beq", "call", "add", "sub", "nor", "mul"]

        if isDefault:
            default = [
                [2, 2, 1],  # load: 2 units, 2 cycles (1 addr + 1 mem), 1 addr cycle
                [2, 2, 1],  # store: 2 units, 2 cycles (1 addr + 1 mem), 1 addr cycle
                [1, 1],     # beq: 1 unit, 1 cycle
                [1, 1],     # call/ret: 1 unit, 1 cycle
                [3, 2],     # add: 3 units, 2 cycles
                [1, 2],     # sub: 1 unit, 2 cycles (shares with add)
                [1, 1],     # nor: 1 unit, 1 cycle (shares with add)
                [2, 10]     # mul: 2 units, 10 cycles
            ]
            
            rsId = 0
            for i in range(self.nStationTypes):
                nUnits = default[i][0]
                execCycles = default[i][1]
                addrCycles = default[i][2] if i < 2 else 0

                for j in range(nUnits):
                    name = st[i] + (str(j + 1) if nUnits > 1 else "")
                    rs = ReservationStation(name, rsId + 1, execCycles, addrCycles)
                    self.stations[i].append(rs)
                    self.idToRs[rsId + 1] = (i, len(self.stations[i]) - 1)
                    rsId += 1
        else:
            with open(hardwareFile) as f:
                rsId = 0
                for i in range(self.nStationTypes):
                    line = f.readline().strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                        
                    nUnits = int(parts[0])
                    execCycles = int(parts[1])
                    addrCycles = int(parts[2]) if i < 2 and len(parts) > 2 else 0

                    for j in range(nUnits):
                        name = st[i] + (str(j + 1) if nUnits > 1 else "")
                        rs = ReservationStation(name, rsId + 1, execCycles, addrCycles)
                        self.stations[i].append(rs)
                        self.idToRs[rsId + 1] = (i, len(self.stations[i]) - 1)
                        rsId += 1

    def readMem(self, memFile: str):
        with open(memFile) as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) == 2:
                        address = int(parts[0])
                        value = int(parts[1])
                        self.mem[address] = value

    def issue(self):
        if self.pc >= len(self.program):
            return

        inst = self.program[self.pc]
        stationType = None
        
        if inst.category == InstCategory.LOAD:
            stationType = 0
        elif inst.category == InstCategory.STORE:
            stationType = 1
        elif inst.category == InstCategory.BEQ:
            stationType = 2
        elif inst.category == InstCategory.CALL:
            stationType = 3
        elif inst.category == InstCategory.ADDITION:
            stationType = 4
        elif inst.category == InstCategory.SUBTRACTION:
            stationType = 5
        elif inst.category == InstCategory.NOR:
            stationType = 6
        elif inst.category == InstCategory.MUL:
            stationType = 7

        if stationType is None:
            return

        for s in self.stations[stationType]:
            if not s.busy:
                inst.issue = self.cycle
                s.busy = True
                s.addr = inst.imm
                s.oper = inst.oper
                s.remCyclesAddr = s.cycles_per_addr
                s.remCyclesExec = s.cycles_per_exec
                s.instIndex = self.pc

                if self.registerStatusTable[inst.rs] != 0:
                    s.qj = self.registerStatusTable[inst.rs]
                else:
                    s.vj = self.registers[inst.rs]
                    s.qj = 0

                if inst.category != InstCategory.LOAD and inst.category != InstCategory.CALL:
                    if self.registerStatusTable[inst.rt] != 0:
                        s.qk = self.registerStatusTable[inst.rt]
                    else:
                        s.vk = self.registers[inst.rt]
                        s.qk = 0

                    if inst.rd != 0:
                        if not self.states:
                            self.registerStatusTable[inst.rd] = s.id
                        else:
                            self.states[-1].register_stat[inst.rd] = s.id

                if inst.category in (InstCategory.LOAD, InstCategory.STORE):
                    self.loadStoreQueue.append(self.pc)

                if inst.category in (InstCategory.BEQ, InstCategory.CALL):
                    if not self.states:
                        self.states.append(SystemState(self.cycle, self.registerStatusTable))
                    else:
                        self.states.append(SystemState(self.cycle, self.states[-1].register_stat))

                # Only increment PC for non-CALL instructions
                if inst.category != InstCategory.CALL:
                    self.pc += 1
                print(f"Cycle {self.cycle}: Issued {inst.inst}")
                break

    def Instructions_logic(self, category: int, station: ReservationStation):
        inst = self.program[station.instIndex]
        
        if category == 0:  # LOAD
            station.result = self.mem[station.addr]
        elif category == 2:  # BEQ
            station.result = int(station.vj == station.vk)  # Changed from != to == for BEQ
            print(f"Cycle {self.cycle}: BEQ comparison: R{inst.rs}={station.vj}, R{inst.rt}={station.vk}, result={station.result}")
        elif category == 3:  # CALL
            if station.oper == InstOp.CALL:
                station.result = station.instIndex + 1
            else:  # RET
                station.result = station.vj
        elif category == 4:  # ADDITION
            station.result = station.vj + station.vk
        elif category == 5:  # SUBTRACTION
            station.result = station.vj - station.vk
        elif category == 6:  # NOR
            station.result = ~(station.vj | station.vk) & 0xFFFF  # Ensure 16-bit result
        elif category == 7:  # MUL
            station.result = (station.vj * station.vk) & 0xFFFF  # Ensure 16-bit result

    def execute(self):
        # Non-Load and Non-Store stations
        for i in range(2, self.nStationTypes):
            for s in self.stations[i]:
                if s.busy and self.program[s.instIndex].issue < self.cycle:
                    if self.states and self.program[s.instIndex].issue > self.states[0].issue:
                        continue

                    if s.qj == 0 and s.qk == 0 and self.program[s.instIndex].issue < self.cycle and s.remCyclesExec:
                        if s.remCyclesExec == s.cycles_per_exec:
                            self.program[s.instIndex].execSt = self.cycle
                            print(f"Cycle {self.cycle}: Starting execution of {self.program[s.instIndex].inst}")
                        s.remCyclesExec -= 1
                        if s.remCyclesExec == 0:
                            self.Instructions_logic(i, s)
                            self.program[s.instIndex].execEnd = self.cycle
                            print(f"Cycle {self.cycle}: Instruction {self.program[s.instIndex].inst} completed execution")

        # Load and Store stations
        queuePop = False
        for i in range(2):
            for s in self.stations[i]:
                if s.busy and self.program[s.instIndex].issue < self.cycle:
                    if self.states and self.program[s.instIndex].issue > self.states[0].issue:
                        continue

                    # Address calculation phase
                    if s.remCyclesAddr:
                        if s.qj == 0 and self.loadStoreQueue and self.loadStoreQueue[0] == s.instIndex:
                            if s.remCyclesAddr == s.cycles_per_addr:
                                self.program[s.instIndex].execSt = self.cycle
                            s.remCyclesAddr -= 1
                            if s.remCyclesAddr == 0:
                                s.addr = (s.addr + s.vj) & 0xFFFF  # 16-bit address
                                queuePop = True
                                print(f"Cycle {self.cycle}: Load address calculation complete for {self.program[s.instIndex].inst}")
                    # Memory access phase
                    elif s.remCyclesExec:
                        if i == 1:  # STORE
                            war = False  # Write After Read Hazard
                            for loadS in self.stations[0]:
                                if (loadS.busy and loadS.remCyclesExec != 0 and
                                    self.program[loadS.instIndex].issue < self.program[s.instIndex].issue and
                                    loadS.addr == s.addr):
                                    war = True
                                    break
                            
                            if not war:
                                s.remCyclesExec -= 1
                                if s.remCyclesExec == 0:
                                    self.program[s.instIndex].execEnd = self.cycle
                                    print(f"Cycle {self.cycle}: Store complete for {self.program[s.instIndex].inst}")
                        else:  # LOAD
                            s.remCyclesExec -= 1
                            if s.remCyclesExec == 0:
                                self.program[s.instIndex].execEnd = self.cycle
                                s.result = self.mem[s.addr] & 0xFFFF  # 16-bit result
                                print(f"Cycle {self.cycle}: Load complete for {self.program[s.instIndex].inst}")

        if queuePop and self.loadStoreQueue:
            self.loadStoreQueue.popleft()

    def writeBack(self):
        writeSId = -1
        writeStoreId = -1
        minIssueTime = sys.maxsize
        minStoreIssueTime = sys.maxsize

        # Find the earliest completed instruction for write-back
        for i in range(self.nStationTypes):
            for s in self.stations[i]:
                if s.busy and s.remCyclesExec == 0 and self.program[s.instIndex].execEnd < self.cycle:
                    if i == 1 and s.qk != 0:  # STORE with unready value
                        continue
                    
                    if self.program[s.instIndex].issue < minIssueTime:
                        if i == 1:  # STORE
                            minStoreIssueTime = self.program[s.instIndex].issue
                            writeStoreId = s.id
                        else:
                            minIssueTime = self.program[s.instIndex].issue
                            writeSId = s.id

        # Handle STORE write-back first (1 cycle)
        if writeStoreId != -1:
            self.wbInsts += 1
            stationType, stationIdx = self.idToRs[writeStoreId]
            writeS = self.stations[stationType][stationIdx]
            writeS.busy = False
            self.program[writeS.instIndex].write = self.cycle
            self.mem[writeS.addr] = writeS.vk & 0xFFFF  # 16-bit result
            print(f"Cycle {self.cycle}: Writeback STORE {self.program[writeS.instIndex].inst}")

        # Handle other instruction write-back (1 cycle)
        if writeSId != -1:
            self.wbInsts += 1
            stationType, stationIdx = self.idToRs[writeSId]
            writeS = self.stations[stationType][stationIdx]
            writeS.busy = False
            self.program[writeS.instIndex].write = self.cycle
            print(f"Cycle {self.cycle}: Writeback {self.program[writeS.instIndex].inst}")

            if stationType == 3:  # CALL/RET
                if writeS.oper == InstOp.CALL:
                    # Store PC+1 in R1
                    self.registers[1] = writeS.instIndex + 1
                    # Branch to the label address (PC + offset)
                    self.pc = writeS.instIndex + 1 + writeS.addr
                else:  # RET
                    # Branch to the address stored in R1
                    self.pc = self.registers[1]

                # Clear system states
                while self.states:
                    self.states.popleft()

                # Flush instructions issued after this CALL/RET
                for i in range(self.nStationTypes):
                    for s in self.stations[i]:
                        if s.busy and self.program[s.instIndex].issue > self.program[writeS.instIndex].issue:
                            s.busy = False
                            for j in range(self.nRegisters):
                                if self.registerStatusTable[j] == s.id:
                                    self.registerStatusTable[j] = 0

                # Flush load/store queue
                while (self.loadStoreQueue and
                       self.program[self.loadStoreQueue[-1]].issue > self.program[writeS.instIndex].issue):
                    self.loadStoreQueue.pop()

            elif stationType == 2:  # BEQ
                self.numBne += 1
                if writeS.result:  # Branch taken
                    self.pc = writeS.instIndex + 1 + writeS.addr
                    self.misprediction += 1

                    # Clear system states
                    while self.states:
                        self.states.popleft()

                    # Flush instructions issued after this BEQ
                    for i in range(self.nStationTypes):
                        for s in self.stations[i]:
                            if s.busy and self.program[s.instIndex].issue > self.program[writeS.instIndex].issue:
                                s.busy = False
                                for j in range(self.nRegisters):
                                    if self.registerStatusTable[j] == s.id:
                                        self.registerStatusTable[j] = 0

                    # Flush load/store queue
                    while (self.loadStoreQueue and
                           self.program[self.loadStoreQueue[-1]].issue > self.program[writeS.instIndex].issue):
                        self.loadStoreQueue.pop()
                else:  # Branch not taken
                    if self.states:
                        for i in range(self.nRegisters):
                            self.registerStatusTable[i] = self.states[0].register_stat[i]
                        self.states.popleft()
                    self.pc = writeS.instIndex + 1

            # Update registers and broadcast results
            if stationType not in (1, 2):  # Not STORE or BEQ
                for i in range(self.nRegisters):
                    if i != 0 and self.registerStatusTable[i] == writeS.id:
                        self.registers[i] = writeS.result & 0xFFFF
                        self.registerStatusTable[i] = 0

                # Forward result to dependent instructions and start their execution
                for i in range(self.nStationTypes):
                    for s in self.stations[i]:
                        if s.busy and (s.qj == writeS.id or s.qk == writeS.id):
                            if s.qj == writeS.id:
                                s.vj = writeS.result & 0xFFFF
                                s.qj = 0
                            if s.qk == writeS.id:
                                s.vk = writeS.result & 0xFFFF
                                s.qk = 0
                            # If all dependencies are resolved, start execution immediately
                            if s.qj == 0 and s.qk == 0:
                                s.remCyclesExec = s.cycles_per_exec
                                self.program[s.instIndex].execSt = self.cycle
                                print(f"Cycle {self.cycle}: Starting execution of {self.program[s.instIndex].inst}")

            # Update instruction timing
            self.program[writeS.instIndex].write = self.cycle

    def nextCycle(self):
        if self.pc < len(self.program):
            self.issue()
        self.writeBack()  # Do writeback first
        self.execute()    # Then execute
        self.cycle += 1

    def printReservationStations(self):
        print("\n" + "="*80)
        print(f'<span style="color: #00b4d8; font-weight: bold;">Cycle {self.cycle - 1}</span>')
        print("="*80)
        
        # Print Reservation Stations
        print('\n<span style="color: #ffd700; font-weight: bold;">Reservation Stations:</span>')
        print("-"*80)
        print(f'<span style="color: #00ff00;">{"Name":<8} {"Busy":<6} {"oper":<8} {"Vj":<8} {"Vk":<8} {"Qj":<8} {"Qk":<8} {"Addr":<8}</span>')
        print("-"*80)
        
        for i in range(self.nStationTypes):
            for s in self.stations[i]:
                if s.busy:
                    opStr = self.program[s.instIndex].op_str if s.oper else ""
                    print(f'<span style="color: #ff69b4;">{s.name:<8} {str(s.busy):<6} {opStr:<8} {s.vj:<8} {s.vk:<8} {s.qj:<8} {s.qk:<8} {s.addr:<8}</span>')
                else:
                    print(f'<span style="color: #666666;">{s.name:<8} {str(s.busy):<6} {"":<8} {"":<8} {"":<8} {"":<8} {"":<8} {"":<8}</span>')

        # Print Register Status
        print('\n<span style="color: #ffd700; font-weight: bold;">Register Status:</span>')
        print("-"*80)
        print(f'<span style="color: #00ff00;">{"Register":<10} {"Status":<10} {"Value":<10}</span>')
        print("-"*80)
        
        for i in range(self.nRegisters):
            status = f"RS{self.registerStatusTable[i]}" if self.registerStatusTable[i] else "Ready"
            statusColor = "#ff69b4" if self.registerStatusTable[i] else "#00ff00"
            print(f'<span style="color: {statusColor};">R{i:<9} {status:<10} {self.registers[i]:<10}</span>')

    def printFinalInstructionsDetails(self):
        print("\n" + "="*80)
        print('<span style="color: #ffd700; font-weight: bold;">Instruction Execution Details</span>')
        print("="*80)
        print(f'<span style="color: #00ff00;">{"Instruction":<20} {"Issue":<8} {"Exec Start":<12} {"Exec End":<10} {"Write Back":<12}</span>')
        print("-"*80)
        
        for inst in self.program:
            print(f'<span style="color: #ff69b4;">{inst.inst:<20} {inst.issue:<8} {inst.execSt:<12} {inst.execEnd:<10} {inst.wb:<12}</span>')

    def printCalculations(self):
        print("\n" + "="*80)
        print('<span style="color: #ffd700; font-weight: bold;">Performance Metrics</span>')
        print("="*80)
        
        mispredictionRate = self.misprediction / self.numBne if self.numBne else 0
        ipc = self.wbInsts / (self.cycle - 1) if self.cycle > 1 else 0
        
        print(f'<span style="color: #00ff00;">Total Cycles: </span><span style="color: #ff69b4;">{self.cycle - 1}</span>')
        print(f'<span style="color: #00ff00;">Instructions Completed: </span><span style="color: #ff69b4;">{self.wbInsts}</span>')
        print(f'<span style="color: #00ff00;">IPC (Instructions per Cycle): </span><span style="color: #ff69b4;">{ipc:.2f}</span>')
        if self.numBne > 0:
            print(f'<span style="color: #00ff00;">Branch Instructions: </span><span style="color: #ff69b4;">{self.numBne}</span>')
            print(f'<span style="color: #00ff00;">Misprediction Rate: </span><span style="color: #ff69b4;">{mispredictionRate:.2%}</span>')

    def cleanup(self):
        # Reset all state variables
        self.cycle = 1
        # Don't reset PC here, it will be restored in initiateRunning
        self.numBne = 0
        self.misprediction = 0
        self.wbInsts = 0
        self.loadStoreQueue.clear()
        self.states.clear()
        
        # Reset all reservation stations
        for stationType in self.stations:
            for s in stationType:
                s.busy = False
                s.oper = None
                s.vj = 0
                s.vk = 0
                s.qj = 0
                s.qk = 0
                s.addr = 0
                s.remCyclesExec = 0
                s.remCyclesAddr = 0
                s.instIndex = 0
                s.result = 0
        
        # Reset register status
        self.registerStatusTable = [0] * self.nRegisters
        
        # Reset instruction timing
        for inst in self.program:
            inst.issue = 0
            inst.execSt = 0
            inst.execEnd = 0
            inst.wb = 0
            inst.write = 0

    def initiateRunning(self):
        initialPc = self.pc  # Save the initial PC value
        self.cleanup()  # Clean up before starting
        self.pc = initialPc  # Restore the initial PC value after cleanup
        stationsBusy = True
        maxCycles = 1000  # Add a safety limit
        cycleCount = 0

        while (stationsBusy or self.pc < len(self.program)) and cycleCount < maxCycles:
            self.nextCycle()
            cycleCount += 1

            # Debug information
            if cycleCount % 100 == 0:
                print(f"\nDebug - Cycle {cycleCount}:")
                print(f"PC: {self.pc}, Program Length: {len(self.program)}")
                print(f"Stations Busy: {stationsBusy}")
                print(f"Instructions Completed: {self.wbInsts}")

            stationsBusy = False
            for stationType in self.stations:
                for s in stationType:
                    if s.busy:
                        stationsBusy = True
                        break
                if stationsBusy:
                    break

        if cycleCount >= maxCycles:
            print("\nWarning: Simulation reached maximum cycle limit")
            print("Current state:")
            self.printReservationStations()
            print("\nDebug Information:")
            print(f"PC: {self.pc}, Program Length: {len(self.program)}")
            print(f"Instructions Completed: {self.wbInsts}")
            print(f"Stations Busy: {stationsBusy}")

        self.printFinalInstructionsDetails()
        self.printCalculations()