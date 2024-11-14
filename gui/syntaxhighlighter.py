from PyQt5.QtCore import  QRegExp
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QFont
from PyQt5.QtWidgets import QTextEdit


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
    'comment': format('darkGreen', 'italic'),
    'numbers': format('brown'),
    'immediate_address': format('darkOrange')
}


class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for a simple custom 6502 assembly language."""

    # 6502 Instructions and Operators
    instructions = ['LDA', 'LDX', 'LDY', 'STA', 'STX', 'STY', 'ADC', 'SBC', 'CMP', 'CPX', 'CPY']
    operators = ['=', '==', '!=', '<', '>', '<=', '>=', '+', '-', '*', '/', '%']
    braces = ['{', '}', '(', ')', '[', ']']

    def __init__(self, parent: QTextEdit) -> None:
        super().__init__(parent.document())

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword']) for w in SyntaxHighlighter.instructions]
        rules += [(r'%s' % o, 0, STYLES['operator']) for o in SyntaxHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace']) for b in SyntaxHighlighter.braces]

        # Additional rules
        rules += [
            (r'\b#\w+\b', 0, STYLES['immediate_address']),
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
            (r';[^\n]*', 0, STYLES['comment']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)
            while index >= 0:
                # Apply formatting
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)