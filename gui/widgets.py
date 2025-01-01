import requests

class Widgets:
    api_url = "http://localhost:5000"  # Basic Flask API URL

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

    @staticmethod
    def assemble(text):
        """
        Sends the source code to the API for assembly and handles the response.

        Args:
            text (str): Source code to be assembled.

        Returns:
            bool: True if the assembly was successful, False otherwise.
        """
        try:
            lines = text.splitlines()
            response = requests.post(
                f"{Widgets.api_url}/assemble",
                json={"source_code": lines}
            )

            if response.status_code == 200:
                # Print the assembled program's details (symbol table, opcodes, etc.)
                response_data = response.json()
                print("Assembly successful!")
                print("Symbol Table:")
                print(response_data.get("symbol_table", "No symbol table provided."))
                print("Opcodes:")
                print(response_data.get("machine_code", "No opcodes provided."))
                return True
            else:
                print(f"Assembly failed. Status Code: {response.status_code}")
                print(f"Error: {response.text}")
                return False
        except requests.RequestException as e:
            print(f"An error occurred while connecting to the API: {e}")
            return False
