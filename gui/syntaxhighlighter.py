import sys
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit

def format(color, style=''):
    """Return a QTextCharFormat with the given attributes."""
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format

# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('blue'),
    'operator': format('red'),
    'brace': format('darkGray'),
    'defclass': format('black', 'bold'),
    'string': format('magenta'),
    'string2': format('darkMagenta'),
    'comment': format('darkGreen', 'italic'),
    'self': format('black', 'italic'),
    'numbers': format('brown'),
}

class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for a simple custom language."""
    # Custom 6502 instructions
    instructions = ['LDA', 'LDX', 'LDY', 'STA', 'STX', 'STY', 'ADC', 'SBC', 'CMP', 'CPX', 'CPY']
    operators = ['=', '==', '!=', '<', '>', '<=', '>=', '+', '-', '*', '/', '%', '**']
    braces = ['{', '}', '(', ')', '[', ']']
    
    def __init__(self, parent: QTextEdit) -> None:
        super().__init__(parent.document())

        # Multi-line strings (expression, flag, style)
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in SyntaxHighlighter.instructions]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in SyntaxHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in SyntaxHighlighter.braces]

        # Additional rules
        rules += [
            (r'\bself\b', 0, STYLES['self']),
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),
            (r'#[^\n]*', 0, STYLES['comment']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        self.tripleQuoutesWithinStrings = []

        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)
            while index >= 0:
                if expression.pattern() in [r'"[^"\\]*(\\.[^"\\]*)*"', r"'[^'\\]*(\\.[^'\\]*)*'"]:
                    innerIndex = self.tri_single[0].indexIn(text, index + 1)
                    if innerIndex == -1:
                        innerIndex = self.tri_double[0].indexIn(text, index + 1)

                    if innerIndex != -1:
                        tripleQuoteIndexes = range(innerIndex, innerIndex + 3)
                        self.tripleQuoutesWithinStrings.extend(tripleQuoteIndexes)

                # Apply formatting
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings."""
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:
            start = delimiter.indexIn(text)
            if start in self.tripleQuoutesWithinStrings:
                return False
            add = delimiter.matchedLength()

        while start >= 0:
            end = delimiter.indexIn(text, start + add)
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            self.setFormat(start, length, style)
            start = delimiter.indexIn(text, start + length)

        return self.currentBlockState() == in_state


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("6502 Syntax Highlighter")
        self.setGeometry(100, 100, 800, 600)

        # Create a QTextEdit widget
        self.textEdit = QTextEdit(self)
        self.setCentralWidget(self.textEdit)

        # Create a SyntaxHighlighter instance for the QTextEdit
        self.highlighter = SyntaxHighlighter(self.textEdit)

        # Set the initial example text (you can change this for your own code)
        example_text = """LDA $2000
ADC $3000
STA $4000
LDX $5000
# Comment line
"""
        self.textEdit.setPlainText(example_text)

        # Enable live syntax highlighting on word completion (when space is typed)
        self.textEdit.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        """Trigger highlighting when a word finishes typing (space typed)."""
        cursor = self.textEdit.textCursor()
        cursor.movePosition(cursor.PreviousCharacter)  # Move cursor back to previous character
        word = cursor.selectedText()

        # Check if the word is valid (non-empty)
        if word and word[-1] in [' ', '\n', '\t', '.', ',', ';']:  # Trigger when space or punctuation follows word
            # Reapply syntax highlighting on the current block
            self.highlighter.rehighlight()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
