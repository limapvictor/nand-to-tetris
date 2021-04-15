from Constants import *

from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable

class CompilationEngine:
    def __init__(self, filepath):
        self._tokenizer = JackTokenizer(filepath) 
        self._writer = VMWriter(filepath)
        self._currentToken = None
        self._classVariables = SymbolTable()
        self._subroutineVariables = SymbolTable()
        self._functionsPrefix = ''
        self._preserveCurrentToken = False

    def run(self):
        self._compileClass()
        self._writer.close()
        return

    #compile functions 
    def _compileClass(self):
        self._eatObligatory([T_KEYWORD], [K_CLASS])
        self._eatObligatory([T_IDENTIFIER])
        className = self._currentToken['value']
        self._functionsPrefix = f'{className}.'
        
        self._eatObligatory([T_SYMBOL], ['{'])
        self._compileClassVarDeclarations()
        self._compileSubroutineDeclarations()
        self._eatObligatory([T_SYMBOL], ['}'])
        return

    def _compileClassVarDeclarations(self):
        self._classVariables.startSubroutine()

        while self._eatExpected([T_KEYWORD], [K_STATIC, K_FIELD]):
            kind = VAR_STATIC if self._currentToken['value'] == K_STATIC else VAR_FIELD
            varType, name = self._compileTypedVarDeclaration()
            self._classVariables.insert(name, varType, kind)

            while self._eatExpected([T_SYMBOL], [',']):
                self._eatObligatory([T_IDENTIFIER])
                name = self._currentToken['value']
                self._classVariables.insert(name, varType, kind)

            self._eatObligatory([T_SYMBOL], [';'])
        return

    def _compileSubroutineDeclarations(self):
        while self._eatExpected([T_KEYWORD], [K_CONSTRUCTOR, K_FUNCTION, K_METHOD]):
            self._subroutineVariables.startSubroutine()

            self._eatObligatory([T_KEYWORD, T_IDENTIFIER], [K_INT, K_CHAR, K_BOOLEAN, K_VOID])
            self._eatObligatory([T_IDENTIFIER])
            self._eatObligatory([T_SYMBOL], ['('])
            self._compileParameterList()
            self._eatObligatory([T_SYMBOL], [')'])
            self._compileSubroutineBody()
        return


    def _compileParameterList(self):
        if self._eatExpected([T_KEYWORD, T_IDENTIFIER], [K_INT, K_CHAR, K_BOOLEAN]):
            varType = self._currentToken['value']
            self._eatObligatory([T_IDENTIFIER])
            name = self._currentToken['value']
            self._subroutineVariables.insert(name, varType, VAR_ARG)
            
            while self._eatExpected([T_SYMBOL], [',']):
                varType, name = self._compileTypedVarDeclaration()
                self._subroutineVariables.insert(name, varType, VAR_ARG)
        return

    def _compileSubroutineBody(self):
        self._eatObligatory([T_SYMBOL], ['{'])
        self._compileVarDeclaration()
        self._compileStatements()
        self._eatObligatory([T_SYMBOL], ['}'])

    def _compileVarDeclaration(self):
        while self._eatExpected([T_KEYWORD], [K_VAR]):
            varType, name = self._compileTypedVarDeclaration()
            self._subroutineVariables.insert(name, varType, VAR_LOCAL)

            while self._eatExpected([T_SYMBOL], [',']):
                self._eatObligatory([T_IDENTIFIER])
                name = self._currentToken['value']
                self._subroutineVariables.insert(name, varType, VAR_LOCAL)

            self._eatObligatory([T_SYMBOL], [';'])


    def _compileStatements(self):
        while self._eatExpected([T_KEYWORD], [K_LET, K_IF, K_WHILE, K_DO, K_RETURN]):
            self._compileStatementByKeyword()
        return

    def _compileLetStatement(self):
        self._eatObligatory([T_IDENTIFIER])

        if self._eatExpected([T_SYMBOL], ['[']):
            self._compileExpression()

            self._eatObligatory([T_SYMBOL], [']'])

        self._eatObligatory([T_SYMBOL], ['='])

        self._compileExpression()

        self._eatObligatory([T_SYMBOL], [';'])

    def _compileIfStatement(self):
        self._compileConditionalStatementBody()

        if self._eatExpected([T_KEYWORD], [K_ELSE]):
            self._eatObligatory([T_SYMBOL], ['{'])

            self._compileStatements()
            
            self._eatObligatory([T_SYMBOL], ['}'])

    def _compileWhileStatement(self):
        self._compileConditionalStatementBody()

    def _compileDoStatement(self):
        self._compileSubroutineCall(calledFromDoStatement=True)

        self._eatObligatory([T_SYMBOL], [';'])
    
    def _compileReturnStatement(self):
        if self._eatExpected([T_SYMBOL], [';']):
            pass
        else:
            self._compileExpression()

            self._eatObligatory([T_SYMBOL], [';'])

    def _compileExpression(self):
        self._compileTerm()
        
        if self._eatExpected([T_SYMBOL], ['+', '-', '*', '/', '&', '|', '<', '>', '=']):

            self._compileTerm()


    def _compileTerm(self):
        requiredTypes = [T_INTEGER_CONSTANT, T_STRING_CONSTANT, T_KEYWORD, T_IDENTIFIER, T_SYMBOL]
        requiredValues = [K_TRUE, K_FALSE, K_NULL, K_THIS, '(', '-', '~']
        self._eatObligatory(requiredTypes, requiredValues)
        
        if self._currentToken['type'] in [T_INTEGER_CONSTANT, T_STRING_CONSTANT, T_KEYWORD]:
            pass
        elif self._currentToken['type'] == T_SYMBOL:
            symbol = self._currentToken['value']

            if symbol == '(':
                self._compileExpression()

                self._eatObligatory([T_SYMBOL], [')'])
            else:
                self._compileTerm()

        elif self._currentToken['type'] == T_IDENTIFIER:
            if self._eatExpected([T_SYMBOL], ['[', '.', '(']):
                self._preserveCurrentToken = True
                symbol = self._currentToken['value']
                
                if symbol == '[':
                    self._compileExpression()

                    self._eatObligatory([T_SYMBOL], [']'])
                else:
                    self._compileSubroutineCall()

    def _compileExpressionList(self):
        if not self._eatExpected([T_SYMBOL], [')']):
            self._compileExpression()

            while self._eatExpected([T_SYMBOL], [',']):

                self._compileExpression()


    #aux compile functions
    def _compileTypedVarDeclaration(self):
        self._eatObligatory([T_KEYWORD, T_IDENTIFIER], [K_INT, K_CHAR, K_BOOLEAN])
        varType = self._currentToken['value']
        self._eatObligatory([T_IDENTIFIER])
        name = self._currentToken['value']
        return varType, name

    def _compileStatementByKeyword(self):
        COMPILE_FUNCTION_BY_KEYWORD = {
            K_LET : self._compileLetStatement,
            K_IF : self._compileIfStatement,
            K_WHILE : self._compileWhileStatement,
            K_DO: self._compileDoStatement,
            K_RETURN : self._compileReturnStatement
        }

        keyword = self._currentToken['value']
        
        COMPILE_FUNCTION_BY_KEYWORD[keyword]()

        
    def _compileConditionalStatementBody(self):
        self._eatObligatory([T_SYMBOL], ['('])

        self._compileExpression()
        
        self._eatObligatory([T_SYMBOL], [')'])
        
        self._eatObligatory([T_SYMBOL], ['{'])

        self._compileStatements()
        
        self._eatObligatory([T_SYMBOL], ['}'])

    def _compileSubroutineCall(self, calledFromDoStatement=False):
        if calledFromDoStatement:
            self._eatObligatory([T_IDENTIFIER])
        
        if self._eatExpected([T_SYMBOL], ['.']):
            self._eatObligatory([T_IDENTIFIER])

        self._eatObligatory([T_SYMBOL], ['('])

        self._compileExpressionList()
        
        self._eatObligatory([T_SYMBOL], [')'])

    #aux functions
    def _eatObligatory(self, requiredTokenTypes, requiredTokenValues = []):
        if not self._preserveCurrentToken and not self._tokenizer.hasMoreTokens():
            self._writer.writeCompilationError('MORE TOKENS EXPECTED!')
            exit(1)
            
        if self._preserveCurrentToken:
            self._preserveCurrentToken = False
        else:
            self._currentToken = self._tokenizer.advance()
        
        if (self._currentToken['type'] not in requiredTokenTypes or 
                (self._currentToken['type'] in TOKEN_TYPES_WITH_EXPECTABLE_VALUES and 
                len(requiredTokenValues) > 0 and self._currentToken['value'] not in requiredTokenValues)):
                self._writer.writeCompilationError('SYNTAX ERROR!')
                exit(1)


    def _eatExpected(self, expectedTokenTypes, expectedTokenValues = []):
        self._currentToken = self._currentToken if self._preserveCurrentToken else self._tokenizer.advance()
        ateExpected = (self._currentToken['type'] in expectedTokenTypes and 
                (self._currentToken['type'] not in TOKEN_TYPES_WITH_EXPECTABLE_VALUES or 
                len(expectedTokenValues) == 0 or self._currentToken['value'] in expectedTokenValues)) 
        self._preserveCurrentToken = not ateExpected
        return ateExpected
