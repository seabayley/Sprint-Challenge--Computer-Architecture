"""CPU functionality."""

import sys

SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256

        self.reg = [0,  # R0
                    0,  # R1
                    0,  # R2
                    0,  # R3
                    0,  # R4
                    0,  # R5 - Interrupt Mask
                    0,  # R6 - Interrupt Status
                    0xf4]  # R7 - Stack Pointer

        self.flags = 0b00000000

        self.pc = 0
        self.running = False

        self.instruction_set = {
            0b10000010: self.ins_ldi,
            0b01000111: self.ins_prn,
            0b10100010: self.ins_mul,
            0b00000001: self.ins_hlt,
            0b01000101: self.ins_push,
            0b01000110: self.ins_pop,
            0b10100111: self.ins_cmp,
            0b01010110: self.ins_jne,
            0b01010101: self.ins_jeq,
            0b01010100: self.ins_jmp


        }

    def load(self):
        """Load a program into memory."""

        address = 0
        program = []
        filename = sys.argv[1]
        with open(f"examples/{filename}") as f:
            for line in f:
                line = line.split('#')
                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue
                program.append(v)

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flags = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flags = 0b10000010
            else:
                self.flags = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        if address > 256 or address < 0:
            print(
                f"Invalid memory address: {address} - Must be between 0 and 256.")
        else:
            return self.ram[address]

    def ram_write(self, address, value):
        if address > 256 or address < 0:
            print(
                f"Invalid memory address: {address} - Must be between 0 and 256.")
        else:
            self.ram[address] = value

    def ins_ldi(self):
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)
        self.pc += 3

    def ins_prn(self):
        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2

    def ins_mul(self):
        self.reg[0] *= self.reg[1]
        self.pc += 3

    def ins_hlt(self):
        self.running = False

    def ins_push(self):
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2

    def ins_pop(self):
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        self.pc += 2

    def ins_cmp(self):
        self.alu('CMP', self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
        self.pc += 3

    def ins_jne(self):
        if (self.flags & 0b00000001) == 0:
            self.ins_jmp()
        else:
            self.pc += 2

    def ins_jeq(self):
        if (self.flags & 0b00000001) == 1:
            self.ins_jmp()
        else:
            self.pc += 2

    def ins_jmp(self):
        self.pc = self.reg[self.ram_read(self.pc + 1)]

    def run(self):
        self.running = True
        while self.running:
            instruction = self.ram[self.pc]

            if instruction in self.instruction_set:
                self.instruction_set[instruction]()
            else:
                print("That is not a valid instruction.")
