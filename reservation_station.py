class ReservationStation:
    def __init__(self, name, id, cyclesPerExec, cyclesPerAddress):
        self.id = id
        self.name = name
        self.busy = False
        self.op = None
        self.vj = 0
        self.vk = 0
        self.qj = 0
        self.qk = 0
        self.addr = 0
        self.cycles_per_exec = cyclesPerExec
        self.cycles_per_addr = cyclesPerAddress
        self.rem_cycles_exec = 0
        self.rem_cycles_addr = 0
        self.inst_index = 0
        self.result = 0 