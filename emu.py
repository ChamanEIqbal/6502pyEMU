from typing import NewType
from typing import List

SByte = NewType('SByte', int)
Byte = NewType('Byte', int)
Word = NewType('Word', int)
u32 = NewType('u32', int)
s32 = NewType('s32', int)

# lookup table for instructions

opcode_table = {
    0xA9: lambda cpu, mem: cpu.implement_LDA_IMMEDIATE(mem),
    0x00: lambda cpu, mem: cpu.implement_BRK(mem),
    # ... add more opcodes and their corresponding implementations ... WIP
}


class Mem: # memory class
    MAX_MEM : u32 = 1024 * 64 # 64 kilobytes of memory
    

    def __init__(self):
        self.Data : List[Byte] = [Byte(0)] * self.MAX_MEM

    def resetMem(self):
        self.Data = [Byte(0)] * self.MAX_MEM
    
    def __getitem__(self, address: Word) -> Byte:
        if(address >= self.MAX_MEM):
            raise IndexError(f"Address {address} is out of range...")
        return self.Data[address]
    
    def __setitem__(self, address : Word, value : Byte) -> None:
        if address >= self.MAX_MEM:
            raise IndexError(f"Address {address} is out of range...")
        if not (0 <= value <= 255):
            raise ValueError(f"Invalid byte value: {value}, must be between 0 and 255 (0x00 and 0xFF)")
        self.Data[address] = value


class StatusFlags: # status flags, little endian (C LSB, N MSB) [8 bits, 1 byte]
    def __init__(self):
        self.C = 1  
        self.Z = 1  
        self.I = 1  
        self.D = 1  
        self.B = 1  
        self.Unused = 1  
        self.V = 1  
        self.N = 1  

    def __repr__(self):
        return f"StatusFlags(C={self.C}, Z={self.Z}, I={self.I}, D={self.D}, B={self.B}, Unused={self.Unused}, V={self.V}, N={self.N})"
    
    def to_byte(self) -> Byte:
        return (self.N << 7) | (self.V << 6) | (self.Unused << 5) | (self.B << 4) | (self.D << 3) | (self.I << 2) | (self.Z << 1) | self.C

    def from_byte(self, byte_value: Byte):
        self.C = byte_value & 0x01 
        self.Z = (byte_value >> 1) & 0x01 
        self.I = (byte_value >> 2) & 0x01 
        self.D = (byte_value >> 3) & 0x01 
        self.B = (byte_value >> 4) & 0x01 
        self.Unused = (byte_value >> 5) & 0x01 
        self.V = (byte_value >> 6) & 0x01 
        self.N = (byte_value >> 7) & 0x01 


class CPU:
    def __init__(self):    
        self.PC : Word = Word(0) # program counter
        self.SP : Byte  = Byte(0) # stack pointer

        self.A : Byte  = Byte(0) # register A
        self.X : Byte = Byte(0) # register X
        self.Y : Byte = Byte(0) # register Y

        self.statusFlags = StatusFlags() # status flags
        self.cycles_consumed : s32 = 0
              

    @property
    def PS(self) -> Byte: # processor status (status flags to byte as cpu property (cpu.PS))
        return self.statusFlags.to_byte()

    @PS.setter # cpu.PS = Byte(0bXXXXXXXX)
    def PS(self, p_byte : Byte):
        self.statusFlags.from_byte(p_byte)

    
    def fetchByte(self, mem: Mem, address : Word) -> Byte:
        self.cycles_consumed+=1
        return mem[address]

    def writeByte(self, mem: Mem, address : Word, data : Byte):
        self.cycles_consumed+=1
        mem[address] =  data

    def execute_instruction(self, opcode, mem):
        if opcode in opcode_table:
            opcode_table[opcode](self, mem)
        else:
            raise ValueError(f"Unknown opcode: {opcode}")


    # The reset routine of 6502 takes 7 cycles, and starts from 0xFFFC (reset vector address afterwards...)
    # so if any booting memory (ROM) is connected to 6502 it must be mapped to address 0xFFFC and must have instructions
    # as required.


    ## WIP


if __name__ == "__main__":
    mem = Mem() # can be loaded with .bin files (pre configured memories, emulated BIOS etc)
    cpu = CPU()

    cpu.writeByte(mem, 0xFFFC, 0xA9) # this should not be done this way, this should be done through Instruction Sets
    print(hex(cpu.fetchByte(mem, 0xFFFC))) # expected : 0xa9, test passed
    print(f"no. of cycles consumed throughout: {cpu.cycles_consumed}") # expected : 2 cycles

    cpu.writeByte(mem, 0xFFFD, 0x00)
    cpu.writeByte(mem, 0xFFFE, 0x00)
    cpu.writeByte(mem, 0xFFFF, 0x00)
    cpu.writeByte(mem, 0x0000, 0x00)
    cpu.writeByte(mem, 0x0001, 0x00)
    cpu.writeByte(mem, 0x0002, 0x00)
    cpu.writeByte(mem, 0x0003, 0x00)
    
    print(hex(cpu.fetchByte(mem, 0xFFFD))) # expected : 0x00
    print(hex(cpu.fetchByte(mem, 0xFFFE))) # expected : 0x00
    print(hex(cpu.fetchByte(mem, 0xFFFF))) # expected : 0x00
    print(hex(cpu.fetchByte(mem, 0x0000))) # expected : 0x00
    print(hex(cpu.fetchByte(mem, 0x0001))) # expected : 0x00
    print(hex(cpu.fetchByte(mem, 0x0002))) # expected:  0x00
    print(hex(cpu.fetchByte(mem, 0x0003))) # expected:  0x00
    
    
    print(f"no. of cycles consumed throughout: {cpu.cycles_consumed}")