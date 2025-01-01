class LineSplitter: # This module will use the 2 pass assembler!
    @staticmethod
    def split_lines(text):
        """
        Splits the given text into lines and prints each line.
        
        Args:
            text (str): The input text to split into lines.
        """
        lines = text.splitlines()
        print("Split lines:")
        for i, line in enumerate(lines, start=1):
            print(f"Line {i}: {line}")
