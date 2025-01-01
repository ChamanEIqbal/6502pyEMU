
OPCODES = {
    'LDA': {'immediate': 0xA9, 'zeropage': 0xA5, 'absolute': 0xAD},
    'STA': {'zeropage': 0x85, 'absolute': 0x8D},
    'JMP': {'absolute': 0x4C},
    # Add other instructions as needed
}

class Assembler:
    @staticmethod
    def get_addressing_mode(operand):
        
        if operand.startswith("#"):
            return 'immediate'
        elif operand.startswith("$"):
            return 'absolute' if len(operand) > 3 else 'zeropage'
        else:
            return 'absolute'

    @staticmethod
    def first_pass(source):
        symbol_table = {}
        address = 0x0600
        for line in source:
            line = line.split(";")[0].strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 1 and line.endswith(":"):
                label = parts[0][:-1]
                symbol_table[label] = address
            else:
                if parts[0].endswith(":"):
                    label = parts[0][:-1]
                    symbol_table[label] = address
                    parts = parts[1:]
                mnemonic = parts[0]
                operand = parts[1] if len(parts) > 1 else None
                mode = Assembler.get_addressing_mode(operand) if operand else None
                address += 2 if mode in ['immediate', 'zeropage'] else 3
        return symbol_table

    @staticmethod
    def second_pass(source, symbol_table):
        machine_code = []
        for line in source:
            line = line.split(";")[0].strip()
            if not line or line.endswith(":"):
                continue
            parts = line.split()
            if parts[0].endswith(":"):
                parts = parts[1:]
            mnemonic = parts[0]
            operand = parts[1] if len(parts) > 1 else None
            mode = Assembler.get_addressing_mode(operand) if operand else None

            if mnemonic in OPCODES and mode in OPCODES[mnemonic]:
                opcode = OPCODES[mnemonic][mode]
                machine_code.append(opcode)
                if mode == 'immediate':
                    value = int(operand[2:], 16)
                    machine_code.append(value)
                elif mode in ['zeropage', 'absolute']:
                    if operand.startswith("$"):
                        address_value = int(operand[1:], 16)
                    else:
                        address_value = symbol_table.get(operand, 0)
                    machine_code.append(address_value & 0xFF)
                    if mode == 'absolute':
                        machine_code.append((address_value >> 8) & 0xFF)
        print(machine_code)
        return machine_code
