from Constants import *
from JackTokenizer import JackTokenizer

class CompilationEngine:
    def __init__(self, filepath):
        file = filepath.replace('.jack', '.xml')
        self._outputFile = open(file, 'w')
        self._tokenizer = JackTokenizer(filepath) 
        self._openedNonTerminalElements = []
        self._currentToken = None

    def constructParseTree(self):
        self._compileClass()
        self._outputFile.close()

    #compile functions 
    def _compileClass(self):
        self._eatObligatory([T_KEYWORD], [K_CLASS])
        self._openNonTerminalElement(K_CLASS, eraseToken=False)
        self._writeTerminalElement()

        self._eatObligatory([T_IDENTIFIER])
        self._writeTerminalElement()

        self._eatObligatory([T_SYMBOL], ['{'])
        self._writeTerminalElement()

        self._compileClassVarDeclarations()

        self._compileSubroutineDeclarations()

        self._eatObligatory([T_SYMBOL], ['}'])
        self._writeTerminalElement()
        
        self._closeNonTerminalElement(K_CLASS)

    def _compileClassVarDeclarations(self):
        while self._eatExpected([T_KEYWORD], [K_STATIC, K_FIELD]):
            self._openNonTerminalElement(NON_TERMINAL_CLASS_VAR_DEC, eraseToken=False)
            self._writeTerminalElement()

            self._compileTypedVarDeclaration()

            while self._eatExpected([T_SYMBOL], [',']):
                self._writeTerminalElement()
                self._eatObligatory([T_IDENTIFIER])
                self._writeTerminalElement()

            self._eatObligatory([T_SYMBOL], [';'])
            self._writeTerminalElement()

            self._closeNonTerminalElement(NON_TERMINAL_CLASS_VAR_DEC)
        return

    def _compileSubroutineDeclarations(self):
        while self._eatExpected([T_KEYWORD], [K_CONSTRUCTOR, K_FUNCTION, K_METHOD]):
            self._openNonTerminalElement(NON_TERMINAL_SUB_DEC, eraseToken=False)
            self._writeTerminalElement()

            self._eatObligatory([T_KEYWORD, T_IDENTIFIER], [K_INT, K_CHAR, K_BOOLEAN, K_VOID])
            self._writeTerminalElement()

            self._eatObligatory([T_IDENTIFIER])
            self._writeTerminalElement()

            self._eatObligatory([T_SYMBOL], ['('])
            self._writeTerminalElement()
            
            self._compileParameterList()

            self._eatObligatory([T_SYMBOL], [')'])
            self._writeTerminalElement()

            self._compileSubroutineBody()

            self._closeNonTerminalElement(NON_TERMINAL_SUB_DEC)

    def _compileParameterList(self):
        self._openNonTerminalElement(NON_TERMINAL_PARAM_LIST)
        if self._eatExpected([T_KEYWORD, T_IDENTIFIER], [K_INT, K_CHAR, K_BOOLEAN]):
            self._writeTerminalElement()
            
            self._eatObligatory([T_IDENTIFIER])
            self._writeTerminalElement()

            while self._eatExpected([T_SYMBOL], [',']):
                self._writeTerminalElement()
                self._compileTypedVarDeclaration()
        self._closeNonTerminalElement(NON_TERMINAL_PARAM_LIST)
        return

    def _compileSubroutineBody(self):
        self._openNonTerminalElement(NON_TERMINAL_SUB_BODY)
        self._eatObligatory([T_SYMBOL], ['{'])
        self._writeTerminalElement()
        
        self._compileVarDeclaration()

        self._compileStatements()

        self._eatObligatory([T_SYMBOL], ['}'])
        self._writeTerminalElement()
        self._closeNonTerminalElement(NON_TERMINAL_SUB_BODY)

    def _compileVarDeclaration(self):
        while self._eatExpected([T_KEYWORD], [K_VAR]):
            self._openNonTerminalElement(NON_TERMINAL_VAR_DEC, eraseToken=False)
            self._writeTerminalElement()

            self._compileTypedVarDeclaration()

            while self._eatExpected([T_SYMBOL], [',']):
                self._writeTerminalElement()
                self._eatObligatory([T_IDENTIFIER])
                self._writeTerminalElement()

            self._eatObligatory([T_SYMBOL], [';'])
            self._writeTerminalElement()

            self._closeNonTerminalElement(NON_TERMINAL_VAR_DEC)

    def _compileStatements(self):
        self._openNonTerminalElement(NON_TERMINAL_STATEMENTS, eraseToken=False)
        while self._eatExpected([T_KEYWORD], [K_LET, K_IF, K_WHILE, K_DO, K_RETURN]):
            self._compileStatementByKeyword()

        self._closeNonTerminalElement(NON_TERMINAL_STATEMENTS)
        return

    def _compileLetStatement(self):
        self._eatObligatory([T_IDENTIFIER])
        self._writeTerminalElement()

        if self._eatExpected([T_SYMBOL], ['[']):
            self._writeTerminalElement()

            self._compileExpression()

            self._eatObligatory([T_SYMBOL], [']'])
            self._writeTerminalElement()   

        self._eatObligatory([T_SYMBOL], ['='])
        self._writeTerminalElement()

        self._compileExpression()

        self._eatObligatory([T_SYMBOL], [';'])
        self._writeTerminalElement()

    def _compileIfStatement(self):
        self._compileConditionalStatementBody()

        if self._eatExpected([T_KEYWORD], [K_ELSE]):
            self._writeTerminalElement()

            self._eatObligatory([T_SYMBOL], ['{'])
            self._writeTerminalElement()

            self._compileStatements()
            
            self._eatObligatory([T_SYMBOL], ['}'])
            self._writeTerminalElement()

    def _compileWhileStatement(self):
        self._compileConditionalStatementBody()

    def _compileDoStatement(self):
        self._compileSubroutineCall(calledFromDoStatement=True)

        self._eatObligatory([T_SYMBOL], [';'])
        self._writeTerminalElement() 
    
    def _compileReturnStatement(self):
        if self._eatExpected([T_SYMBOL], [';']):
            self._writeTerminalElement()
        else:
            self._compileExpression()

            self._eatObligatory([T_SYMBOL], [';'])
            self._writeTerminalElement()

    def _compileExpression(self):
        self._openNonTerminalElement(NON_TERMINAL_EXPRESSION, eraseToken=False)

        self._compileTerm()
        
        if self._eatExpected([T_SYMBOL], ['+', '-', '*', '/', '&', '|', '<', '>', '=']):
            self._writeTerminalElement()

            self._compileTerm()

        self._closeNonTerminalElement(NON_TERMINAL_EXPRESSION)

    def _compileTerm(self):
        self._openNonTerminalElement(NON_TERMINAL_TERM, eraseToken=False)

        requiredTypes = [T_INTEGER_CONSTANT, T_STRING_CONSTANT, T_KEYWORD, T_IDENTIFIER, T_SYMBOL]
        requiredValues = [K_TRUE, K_FALSE, K_NULL, K_THIS, '(', '-', '~']
        self._eatObligatory(requiredTypes, requiredValues)

        if self._currentToken['type'] in [T_INTEGER_CONSTANT, T_STRING_CONSTANT, T_KEYWORD]:
            self._writeTerminalElement()

        elif self._currentToken['type'] == T_SYMBOL:
            symbol = self._currentToken['value']
            self._writeTerminalElement()

            if symbol == '(':
                self._compileExpression()

                self._eatObligatory([T_SYMBOL], [')'])
                self._writeTerminalElement()
            else:
                self._compileTerm()

        elif self._currentToken['type'] == T_IDENTIFIER:
            self._writeTerminalElement()

            if self._eatExpected([T_SYMBOL], ['[', '.', '(']):
                symbol = self._currentToken['value']
                
                if symbol == '[':
                    self._writeTerminalElement()

                    self._compileExpression()

                    self._eatObligatory([T_SYMBOL], [']'])
                    self._writeTerminalElement()
                else:
                    self._compileSubroutineCall()

        self._closeNonTerminalElement(NON_TERMINAL_TERM)

    def _compileExpressionList(self):
        self._openNonTerminalElement(NON_TERMINAL_EXPRESSION_LIST)

        if not self._eatExpected([T_SYMBOL], [')']):
            self._compileExpression()

            while self._eatExpected([T_SYMBOL], [',']):
                self._writeTerminalElement()

                self._compileExpression()

        self._closeNonTerminalElement(NON_TERMINAL_EXPRESSION_LIST)

    #aux compile functions
    def _compileTypedVarDeclaration(self):
        self._eatObligatory([T_KEYWORD, T_IDENTIFIER], [K_INT, K_CHAR, K_BOOLEAN])
        self._writeTerminalElement()

        self._eatObligatory([T_IDENTIFIER])
        self._writeTerminalElement()

    def _compileStatementByKeyword(self):
        COMPILE_FUNCTION_BY_KEYWORD = {
            K_LET : self._compileLetStatement,
            K_IF : self._compileIfStatement,
            K_WHILE : self._compileWhileStatement,
            K_DO: self._compileDoStatement,
            K_RETURN : self._compileReturnStatement
        }

        keyword = self._currentToken['value']
        self._openNonTerminalElement(keyword + NON_TERMINAL_STATEMENT, eraseToken=False)
        self._writeTerminalElement()
        
        COMPILE_FUNCTION_BY_KEYWORD[keyword]()

        self._closeNonTerminalElement(keyword + NON_TERMINAL_STATEMENT)
        
    def _compileConditionalStatementBody(self):
        self._eatObligatory([T_SYMBOL], ['('])
        self._writeTerminalElement()

        self._compileExpression()
        
        self._eatObligatory([T_SYMBOL], [')'])
        self._writeTerminalElement()
        
        self._eatObligatory([T_SYMBOL], ['{'])
        self._writeTerminalElement()

        self._compileStatements()
        
        self._eatObligatory([T_SYMBOL], ['}'])
        self._writeTerminalElement()

    def _compileSubroutineCall(self, calledFromDoStatement=False):
        if calledFromDoStatement:
            self._eatObligatory([T_IDENTIFIER])
            self._writeTerminalElement()
        
        if self._eatExpected([T_SYMBOL], ['.']):
            self._writeTerminalElement()

            self._eatObligatory([T_IDENTIFIER])
            self._writeTerminalElement()

        self._eatObligatory([T_SYMBOL], ['('])
        self._writeTerminalElement()

        self._compileExpressionList()

        self._eatObligatory([T_SYMBOL], [')'])
        self._writeTerminalElement()

    #aux functions
    def _eatObligatory(self, requiredTokenTypes, requiredTokenValues = []):
        if self._currentToken is None and not self._tokenizer.hasMoreTokens():
            self._outputFile.write('-- COMPILATION ERROR -> MORE TOKENS EXPECTED!! --')
            self._outputFile.close()
            exit(1)

        self._currentToken = self._currentToken or self._tokenizer.advance()
        if (self._currentToken['type'] not in requiredTokenTypes or 
                (self._currentToken['type'] in TOKEN_TYPES_WITH_EXPECTABLE_VALUES and 
                len(requiredTokenValues) > 0 and self._currentToken['value'] not in requiredTokenValues)):
            self._outputFile.write('-- COMPILATION ERROR -> WRONG SYNTAX!! --')
            self._outputFile.close()
            exit(1)

    def _eatExpected(self, expectedTokenTypes, expectedTokenValues = []):
        self._currentToken = self._currentToken or self._tokenizer.advance()

        return (self._currentToken['type'] in expectedTokenTypes and 
                (self._currentToken['type'] not in TOKEN_TYPES_WITH_EXPECTABLE_VALUES or 
                len(expectedTokenValues) == 0 or self._currentToken['value'] in expectedTokenValues)) 

    def _openNonTerminalElement(self, element, isNonTerminalElementUnique = False, eraseToken = True):
        if not isNonTerminalElementUnique or element not in self._openedNonTerminalElements:
            self._outputFile.write(f'<{element}>\n')
            self._openedNonTerminalElements.append(element)
            self._currentToken = None if eraseToken else self._currentToken
        
    def _closeNonTerminalElement(self, element):
        if element in self._openedNonTerminalElements:
            self._outputFile.write(f'</{element}>\n')
            self._openedNonTerminalElements.remove(element)

    def _writeTerminalElement(self):
        XML_TRANSLATOR = {
            '<': '&lt;',
            '>': '&gt;',
            '&': '&amp;',
            '"': '&quot;'
        }

        tokenType, tokenValue = self._currentToken.values()
        tokenValue = XML_TRANSLATOR[tokenValue] if tokenValue in XML_TRANSLATOR else tokenValue.replace('"', '')
        self._outputFile.write(f'<{TERMINAL_ELEMENT_BY_TOKEN_TYPE[tokenType]}>')
        self._outputFile.write(f' {tokenValue} ')
        self._outputFile.write(f'</{TERMINAL_ELEMENT_BY_TOKEN_TYPE[tokenType]}>\n')
        self._currentToken = None