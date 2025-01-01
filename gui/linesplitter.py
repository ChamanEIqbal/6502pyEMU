class LineSplitter: # This module will use the 2 pass assembler!
    @staticmethod
    def split_lines(text):
        """
        6502 Emulator - v0.0.2: LINE SPLITTER MODULE
        Splits the given text into lines and prints each line.
        
        Args:
            text (str): The input text to split into lines.

        Work Flow Function (*) ==> THIS:
            -*Gives to API, JSON request.
            -API Manages / Assembles the request and returns a JSON response.
            -*Gets Response from API, prints the Assembled Code to Console.
            -Responsed API is put to Memory of CPU at backend.
            -Backend Memory uses Program for Execution / Steps for Debugger or PPU.
        """
        lines = text.splitlines()
        print("Split lines:")
        for i, line in enumerate(lines, start=1):
            print(f"Line {i}: {line}")
