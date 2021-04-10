import re

from Constants import *

class JackTokenizer:
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
        apiCommentRegex = '\/\*\*(.*?)\*\/'
        comments = f'{lineCommentRegex}|{multiLineCommentRegex}|{apiCommentRegex}'

        self._jackCode = re.sub(comments, '', self._jackCode)

    def _splitJackCodeOnTokenValues(self):
        splitters = SYMBOLS + [' ']
        splitters = '|\\'.join(splitters)

        self._jackCode = re.split(f'([{splitters}])', self._jackCode)
        self._jackCode = [tokenValue for tokenValue in self._jackCode if tokenValue != ' ' and tokenValue != '']

    def _getTokenTypeByValue(self, value):
        if value in KEYWORDS:
            return T_KEYWORD

        if value in SYMBOLS:
            return T_SYMBOL

        if re.fullmatch(r'[0-9]{1,5}', value):
            return T_INTEGER_CONSTANT

        if re.fullmatch(r'^\"[^\"\n]*\"$', value):
            return T_STRING_CONSTANT

        if re.fullmatch(r'^[a-zA-Z\_][a-zA-Z0-9\_]*', value):
            return T_IDENTIFIER