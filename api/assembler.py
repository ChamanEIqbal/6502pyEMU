OPCODES = {
    'LDA': {'immediate': 0xA9, 'zeropage': 0xA5, 'absolute': 0xAD},
    'STA': {'zeropage': 0x85, 'absolute': 0x8D},
    'JMP': {'absolute': 0x4C},
    'TAY': {'implied': 0xA8},  
    'TAX': {'implied': 0xAA},  
    'INC': {'zeropage': 0xE6, 'absolute': 0xEE},
    'INX': {'implied': 0xE8},
    'INY': {'implied': 0xC8},
    'LDX': {'immediate': 0xA2, 'zeropage': 0xA6, 'absolute': 0xAE},
    'LDY': {'immediate': 0xA0, 'zeropage': 0xA4, 'absolute': 0xAC},
}


class Assembler:
    @staticmethod
    def get_addressing_mode(mnemonic, operand=None):
        # Handle implied addressing for TAY and TAX
        if mnemonic in ['TAY', 'TAX', 'INX', 'INY']:
            return 'implied'
        elif operand and operand.startswith("#"):
            return 'immediate'
        elif operand and operand.startswith("$"):
            return 'absolute' if len(operand) > 3 else 'zeropage'
        else:
            return 'absolute'

    @staticmethod
    def first_pass(source):
        symbol_table = {}
        address = 0x0000
        for line in source:
            line = line.split(";")[0].strip()  # Ignore comments
            if not line:
                continue
            parts = line.split()
            if len(parts) == 1 and line.endswith(":"):
                # Label definition
                label = parts[0][:-1]
                symbol_table[label] = address
            else:
                if parts[0].endswith(":"):
                    # Label followed by instruction
                    label = parts[0][:-1]
                    symbol_table[label] = address
                    parts = parts[1:]  # Remove label from instruction parts
                
                mnemonic = parts[0]
                operand = parts[1] if len(parts) > 1 else None
                mode = Assembler.get_addressing_mode(mnemonic, operand) if operand else Assembler.get_addressing_mode(mnemonic)
                
                # Increase address based on addressing mode
                address += 2 if mode in ['immediate', 'zeropage', 'implied'] else 3
        return symbol_table

    @staticmethod
    def second_pass(source, symbol_table):
        machine_code = []
        for line in source:
            line = line.split(";")[0].strip()  # Ignore comments
            if not line or line.endswith(":"):
                continue  # Skip labels and empty lines
            parts = line.split()
            if parts[0].endswith(":"):
                parts = parts[1:]  # Remove label part
                
            mnemonic = parts[0]
            operand = parts[1] if len(parts) > 1 else None
            mode = Assembler.get_addressing_mode(mnemonic, operand) if operand else Assembler.get_addressing_mode(mnemonic)

            if mnemonic in OPCODES and mode in OPCODES[mnemonic]:
                # Append the opcode to machine code
                opcode = OPCODES[mnemonic][mode]
                machine_code.append(opcode)
                
                if mode == 'immediate':
                    value = int(operand[2:], 16)  # Convert hexadecimal operand to value
                    machine_code.append(value)
                elif mode in ['zeropage', 'absolute']:
                    if operand.startswith("$"):
                        address_value = int(operand[1:], 16)  # Convert hex address to value
                    else:
                        address_value = symbol_table.get(operand, 0)  # Look up symbol in symbol table
                    machine_code.append(address_value & 0xFF)  # Lower byte
                    if mode == 'absolute':
                        machine_code.append((address_value >> 8) & 0xFF)  # Higher byte (for absolute addresses)
        print(machine_code)
        return machine_code