import re

from Constants import *

class JackTokenizer:
    KEYWORD_REGEX = '|'.join(KEYWORDS)
    SYMBOL_REGEX = '[' + re.escape(''.join(SYMBOLS)) + ']'
    INT_REGEX = r'[0-9]{1,5}'
    STRING_REGEX = r'"[^"\n]*"'
    IDENTIFIER_REGEX = r'[\w\-]+'
    
    def __init__(self, filepath):
        self._jackCode = ''
        self._readJackFile(filepath)
        self._tokens = []
        self._tokenize()

    def hasMoreTokens(self):
        return len(self._tokens) > 0
    
    def advance(self):
        return self._tokens.pop(0)

    def _tokenize(self):
        self._removeCommentsFromJackCode()
        self._jackCode = self._jackCode.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        self._splitJackCodeOnTokenValues()

        for tokenValue in self._jackCode:
            tokenType = self._getTokenTypeByValue(tokenValue)
            token = dict()
            token['type'] = tokenType
            token['value'] = tokenValue
            self._tokens.append(token)
    
    def _readJackFile(self, filepath):
        file = open(filepath, 'r')
        self._jackCode = file.read()
        file.close()

    def _removeCommentsFromJackCode(self):
        lineCommentRegex = '\/\/(.*?)\n'
        multiLineCommentRegex = '\/\*(.*?)\*\/'
        apiCommentRegex = '\/\*\*((.|\n)*?)\*\/'
        comments = f'{lineCommentRegex}|{multiLineCommentRegex}|{apiCommentRegex}'

        self._jackCode = re.sub(comments, '', self._jackCode)

    def _splitJackCodeOnTokenValues(self):
        tokenFinder = re.compile(f'{self.KEYWORD_REGEX}|{self.SYMBOL_REGEX}|{self.INT_REGEX}|{self.STRING_REGEX}|{self.IDENTIFIER_REGEX}')
        self._jackCode = tokenFinder.findall(self._jackCode)

    def _getTokenTypeByValue(self, value):
        if re.fullmatch(self.KEYWORD_REGEX, value):
            return T_KEYWORD

        if re.fullmatch(self.SYMBOL_REGEX, value):
            return T_SYMBOL

        if re.fullmatch(self.INT_REGEX, value):
            return T_INTEGER_CONSTANT

        if re.fullmatch(self.STRING_REGEX, value):
            return T_STRING_CONSTANT

        if re.fullmatch(self.IDENTIFIER_REGEX, value):
            return T_IDENTIFIER