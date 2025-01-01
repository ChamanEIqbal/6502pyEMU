from flask import Flask, request, jsonify
from assembler import Assembler

# Memory and CPU constants
MAX_MEM = 64 * 1024  # 64 KB of memory

# Flask app
app = Flask(__name__)

# Memory and CPU state
memory = [0] * MAX_MEM  # Memory array
cpu_state = {
    "PC": 0x0000,  # Program Counter
    "A": 0x00,     # Accumulator
    "X": 0x00,     # X Register
    "Y": 0x00,     # Y Register
    "SP": 0x1FFF,  # Stack Pointer
    "PS": 0x00,    # Status Flags
    "cycles": 0    # Cycle count
}

# Opcodes for simple operations
opcode_table = {
    0xA9: "LDA_IMMEDIATE",
    0x00: "BRK"
}


# Helper functions
def reset_memory():
    global memory
    memory = [0] * MAX_MEM

def execute_opcode(opcode):
    global cpu_state
    if opcode == 0xA9:  # LDA Immediate
        cpu_state["A"] = memory[cpu_state["PC"] + 1]
        cpu_state["PC"] += 2
        cpu_state["cycles"] += 2
        update_status_flags()
    elif opcode == 0x00:  # BRK
        cpu_state["PC"] = 0xFFFF
        cpu_state["cycles"] += 7
    else:
        raise ValueError(f"Unknown opcode: {opcode}")

def update_status_flags():
    cpu_state["PS"] = (cpu_state["A"] == 0) << 1  # Set Zero Flag

# API Endpoints
@app.route('/reset', methods=['POST'])
def reset():
    reset_memory()
    return jsonify({"message": "Memory reset successfully", "cpu_state": cpu_state})

@app.route('/load', methods=['POST'])
def load_memory():
    data = request.json
    address = data.get('address')
    values = data.get('values')
    if not (isinstance(address, int) and isinstance(values, list)):
        return jsonify({"error": "Invalid input"}), 400
    try:
        for i, value in enumerate(values):
            memory[address + i] = value
        return jsonify({"message": "Memory loaded successfully"})
    except IndexError:
        return jsonify({"error": "Memory address out of range"}), 400

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    opcode = data.get('opcode')
    if not isinstance(opcode, int):
        return jsonify({"error": "Invalid opcode"}), 400
    try:
        execute_opcode(opcode)
        return jsonify({"message": "Instruction executed", "cpu_state": cpu_state})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/state', methods=['GET'])
def state():
    return jsonify(cpu_state)

@app.route('/memory', methods=['GET'])
def memory_dump():
    memory_hex = {f"{addr:04X}": f"{value:02X}" for addr, value in enumerate(memory)}
    return jsonify({"memory": memory_hex})

@app.route('/memory', methods=['POST'])
def memory_at_address():
    """
    Returns the value at a specific memory address.
    Expected JSON payload: { "address": "0000" }
    """
    data = request.json
    hex_address = data.get("address")

    if not hex_address:
        return jsonify({"error": "Address is required"}), 400

    try:
        # Convert the hex address to an integer
        address = int(hex_address, 16)

        # Validate address range
        if address < 0 or address >= len(memory):
            return jsonify({"error": "Address out of range"}), 400

        # Fetch the value at the specified address
        value = memory[address]
        return jsonify({"address": f"{address:04X}", "value": f"{value:02X}"})
    except ValueError:
        return jsonify({"error": "Invalid address format. Must be a valid hexadecimal value."}), 400


@app.route('/assemble', methods=['POST'])
def assemble():
    data = request.json
    source_code = data.get("source_code")
    if not isinstance(source_code, list):
        return jsonify({"error": "Invalid source code format. Must be a list of strings."}), 400
    try:
        symbol_table = Assembler.first_pass(source_code)
        machine_code = Assembler.second_pass(source_code, symbol_table)
        return jsonify({
            "symbol_table": symbol_table,
            "machine_code": [f"{byte:02X}" for byte in machine_code]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
