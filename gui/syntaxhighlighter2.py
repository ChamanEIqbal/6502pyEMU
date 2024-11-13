import tkinter as tk
import re

# Syntax styles
STYLES = {
    'keyword': {'foreground': 'blue'},
    'operator': {'foreground': 'red'},
    'brace': {'foreground': 'darkgray'},
    'comment': {'foreground': 'green', 'italic': True},
    'numbers': {'foreground': 'brown'},
}

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget

        # Custom 6502 instructions (keywords)
        self.instructions = ['LDA', 'LDX', 'LDY', 'STA', 'STX', 'STY', 'ADC', 'SBC', 'CMP', 'CPX', 'CPY']
        self.operators = ['=', '==', '!=', '<', '>', '<=', '>=', '+', '-', '*', '/', '%', '**']
        self.braces = ['{', '}', '(', ')', '[', ']']

        # Bind the event to update syntax highlighting as text changes
        self.text_widget.bind("<KeyRelease>", self.on_key_release)

    def on_key_release(self, event=None):
        """Called when a key is released. Reapply syntax highlighting."""
        self.apply_syntax_highlighting()

    def apply_syntax_highlighting(self):
        """Apply syntax highlighting to the entire text."""
        text = self.text_widget.get("1.0", "end-1c")  # Get the text content

        # Remove all previous tags
        self.text_widget.tag_remove("keyword", "1.0", "end")
        self.text_widget.tag_remove("operator", "1.0", "end")
        self.text_widget.tag_remove("brace", "1.0", "end")
        self.text_widget.tag_remove("comment", "1.0", "end")
        self.text_widget.tag_remove("numbers", "1.0", "end")

        # Apply the syntax highlighting rules
        self.highlight_keywords(text)
        self.highlight_operators(text)
        self.highlight_braces(text)
        self.highlight_numbers(text)
        self.highlight_comments(text)

    def highlight_keywords(self, text):
        """Highlight keywords like LDA, STA, etc."""
        for keyword in self.instructions:
            self.apply_tag(text, r'\b' + keyword + r'\b', "keyword")

    def highlight_operators(self, text):
        """Highlight operators like +, -, =, etc."""
        for operator in self.operators:
            self.apply_tag(text, r'\b' + operator + r'\b', "operator")

    def highlight_braces(self, text):
        """Highlight braces like {, }, (, ), [, ]"""
        for brace in self.braces:
            self.apply_tag(text, re.escape(brace), "brace")

    def highlight_numbers(self, text):
        """Highlight numbers (integers or hex)."""
        self.apply_tag(text, r'\b[0-9]+\b', "numbers")
        self.apply_tag(text, r'\b0[xX][0-9A-Fa-f]+\b', "numbers")  # Hex numbers

    def highlight_comments(self, text):
        """Highlight comments that start with '#'."""
        self.apply_tag(text, r'#.*', "comment")

    def apply_tag(self, text, pattern, tag):
        """Apply a tag for matching pattern in the text."""
        start_idx = "1.0"
        matches = re.finditer(pattern, text)
        for match in matches:
            start = match.start()
            end = match.end()

            # Convert start and end to tkinter's text widget indices
            start_idx = self.index_from_char_index(start)
            end_idx = self.index_from_char_index(end)

            self.text_widget.tag_add(tag, start_idx, end_idx)
            self.text_widget.tag_configure(tag, **STYLES[tag])

    def index_from_char_index(self, char_index):
        """Convert character index to tkinter text widget index."""
        line, col = 1, 0
        for i in range(char_index):
            if char_index[i] == '\n':
                line += 1
                col = 0
            else:
                col += 1
        return f"{line}.{col}"


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("6502 Syntax Highlighter")
        self.geometry("800x600")

        # Create the Text widget where the code will be typed
        self.text_widget = tk.Text(self, wrap="word", font=("Courier", 12))
        self.text_widget.pack(expand=True, fill="both")

        # Create the SyntaxHighlighter instance
        self.highlighter = SyntaxHighlighter(self.text_widget)

        # Set the initial example text (you can change this for your own code)
        example_text = """LDA $2000
ADC $3000
STA $4000
LDX $5000
# This is a comment line
"""
        self.text_widget.insert("1.0", example_text)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
