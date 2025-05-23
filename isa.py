from enum import Enum, auto

class InstCateg(Enum):
    LOAD = auto()
    STORE = auto()
    BEQ = auto()
    CALL = auto()
    RET = auto()
    ADD = auto()
    SUB = auto()
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
    def __init__(self, pc, operation, rs, rt, rd, imm, inst):
        self.pc = pc
        self.operation = operation
        self.rs = rs
        self.rt = rt
        self.rd = rd
        self.imm = imm
        self.inst = inst
        self.issue = self.execSt = self.execEnd = self.write = 0
        self.categ = None
        self.operationStr = ""
        tokens = inst.strip().replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
        if not tokens:
            raise ValueError("Empty instruction string")
        operation = tokens[0].lower()
        self.operationStr = operation
        try:
            if operation == "load":
                self.categ = InstCateg.LOAD
                self.operation = InstOp.LOAD
                self.rd = int(tokens[1][1:])
                self.imm = int(tokens[2])
                self.rs = int(tokens[3][1:])
                if not (0 <= self.rd <= 15 and 0 <= self.rs <= 15):
                    raise ValueError(f"Register number out of range (0-15) in instruction: {inst}")
                if not (-64 <= self.imm <= 63):
                    raise ValueError(f"Load offset out of range (-64 to 63) in instruction: {inst}")
            elif operation == "store":
                self.categ = InstCateg.STORE
                self.operation = InstOp.STORE
                self.rt = int(tokens[1][1:])
                self.imm = int(tokens[2])
                self.rs = int(tokens[3][1:])
                if not (0 <= self.rt <= 15 and 0 <= self.rs <= 15):
                    raise ValueError(f"Register number out of range (0-15) in instruction: {inst}")
                if not (-64 <= self.imm <= 63):
                    raise ValueError(f"Store offset out of range (-64 to 63) in instruction: {inst}")
            elif operation == "beq":
                self.categ = InstCateg.BEQ
                self.operation = InstOp.BEQ
                self.rs = int(tokens[1][1:])
                self.rt = int(tokens[2][1:])
                self.imm = int(tokens[3])
                self.addr = self.imm
                if not (0 <= self.rs <= 15 and 0 <= self.rt <= 15):
                    raise ValueError(f"Register number out of range (0-15) in instruction: {inst}")
                if not (-64 <= self.imm <= 63):
                    raise ValueError(f"Branch offset out of range (-64 to 63) in instruction: {inst}")
            elif operation == "call":
                self.categ = InstCateg.CALL
                self.operation = InstOp.CALL
                self.imm = int(tokens[1])
                self.addr = self.imm
                if not (-64 <= self.imm <= 63):
                    raise ValueError(f"Call target out of range (-64 to 63) in instruction: {inst}")
            elif operation == "ret":
                self.categ = InstCateg.RET
                self.operation = InstOp.RET
            elif operation == "add":
                self.categ = InstCateg.ADD
                self.operation = InstOp.ADD
                self.rd = int(tokens[1][1:])
                self.rs = int(tokens[2][1:])
                self.rt = int(tokens[3][1:])
                if not (0 <= self.rd <= 15 and 0 <= self.rs <= 15 and 0 <= self.rt <= 15):
                    raise ValueError(f"Register number out of range (0-15) in instruction: {inst}")
            elif operation == "sub":
                self.categ = InstCateg.SUB
                self.operation = InstOp.SUB
                self.rd = int(tokens[1][1:])
                self.rs = int(tokens[2][1:])
                self.rt = int(tokens[3][1:])
                if not (0 <= self.rd <= 15 and 0 <= self.rs <= 15 and 0 <= self.rt <= 15):
                    raise ValueError(f"Register number out of range (0-15) in instruction: {inst}")
            elif operation == "nor":
                self.categ = InstCateg.NOR
                self.operation = InstOp.NOR
                self.rd = int(tokens[1][1:])
                self.rs = int(tokens[2][1:])
                self.rt = int(tokens[3][1:])
                if not (0 <= self.rd <= 15 and 0 <= self.rs <= 15 and 0 <= self.rt <= 15):
                    raise ValueError(f"Register number out of range (0-15) in instruction: {inst}")
            elif operation == "mul":
                self.categ = InstCateg.MUL
                self.operation = InstOp.MUL
                self.rd = int(tokens[1][1:])
                self.rs = int(tokens[2][1:])
                self.rt = int(tokens[3][1:])
                if not (0 <= self.rd <= 15 and 0 <= self.rs <= 15 and 0 <= self.rt <= 15):
                    raise ValueError(f"Register number out of range (0-15) in instruction: {inst}")
            else:
                raise ValueError(f"Unsupported instruction: {inst}")
                
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid instruction format: {inst} - {str(e)}")