import sys
from tomasulo import Tomasulo
from gui import TomasuloGUI
import tkinter as tk

def runSimulation(instructionFile: str, isDefaultHardware: bool, hardwareFile: str, pc: int):
    simulator = Tomasulo(instructionFile, isDefaultHardware, hardwareFile, pc)
    simulator.initiateRunning()

def runGUI(instructionFile: str, isDefaultHardware: bool, hardwareFile: str, pc: int):
    root = tk.Tk()
    app = TomasuloGUI(root, instructionFile, isDefaultHardware, hardwareFile, pc)
    root.mainloop()

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [--gui] <instruction_file> [--hardware <hardware_file>] [--pc <pc_value>]")
        sys.exit(1)

    isGui = False
    instructionFile = None
    hardwareFile = "hardware.txt"
    pc = 0
    isDefaultHardware = True

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--gui":
            isGui = True
            i += 1
        elif sys.argv[i] == "--hardware":
            if i + 1 < len(sys.argv):
                hardwareFile = sys.argv[i + 1]
                isDefaultHardware = False
                i += 2
            else:
                print("Error: --hardware requires a file path")
                sys.exit(1)
        elif sys.argv[i] == "--pc":
            if i + 1 < len(sys.argv):
                try:
                    pc = int(sys.argv[i + 1])
                    i += 2
                except ValueError:
                    print("Error: PC value must be an integer")
                    sys.exit(1)
            else:
                print("Error: --pc requires a value")
                sys.exit(1)
        else:
            instructionFile = sys.argv[i]
            i += 1

    if not instructionFile:
        print("Error: Instruction file is required")
        sys.exit(1)

    if isGui:
        runGUI(instructionFile, isDefaultHardware, hardwareFile, pc)
    else:
        runSimulation(instructionFile, isDefaultHardware, hardwareFile, pc)

if __name__ == "__main__":
    main() 