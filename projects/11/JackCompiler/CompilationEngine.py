from Constants import *

from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable

class CompilationEngine:
    def __init__(self, filepath):
        self._tokenizer = JackTokenizer(filepath) 
        self._writer = VMWriter(filepath)
        self._classVariables = SymbolTable()
        self._subroutineVariables = SymbolTable()
        self._currentToken = None
        self._preserveCurrentToken = False
        self._className = ''
        self._currentCompilingFunction = {'kind': '', 'name': ''}
        self._numberConditionalsStatementsCurrentFunction = 0

    def run(self):
        self._compileClass()
        self._writer.close()
        return

    #compile functions 
    def _compileClass(self):
        self._eatObligatory([T_KEYWORD], [K_CLASS])
        self._eatObligatory([T_IDENTIFIER])
        self._className = self._currentToken['value']

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
            self._currentCompilingFunction['kind'] = self._currentToken['value']
            self._subroutineVariables.startSubroutine()

            self._eatObligatory([T_KEYWORD, T_IDENTIFIER], [K_INT, K_CHAR, K_BOOLEAN, K_VOID])
            self._eatObligatory([T_IDENTIFIER])
            self._currentCompilingFunction['name'] = self._currentToken['value']

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

        funcName = self._className + '.' + self._currentCompilingFunction['name']
        nLocalVars = self._subroutineVariables.getVarCountByKind(VAR_LOCAL)
        self._writer.writeFunction(funcName, nLocalVars)

        self._numberConditionalsStatementsCurrentFunction = 0
        if self._currentCompilingFunction['kind'] == K_CONSTRUCTOR: self._compileConstructorCode()
        elif self._currentCompilingFunction['kind'] == K_METHOD: self._compileMethodCode()
        self._compileStatements()
        self._eatObligatory([T_SYMBOL], ['}'])
        return

    def _compileVarDeclaration(self):
        while self._eatExpected([T_KEYWORD], [K_VAR]):
            varType, name = self._compileTypedVarDeclaration()
            self._subroutineVariables.insert(name, varType, VAR_LOCAL)
            while self._eatExpected([T_SYMBOL], [',']):
                self._eatObligatory([T_IDENTIFIER])
                name = self._currentToken['value']
                self._subroutineVariables.insert(name, varType, VAR_LOCAL)
            self._eatObligatory([T_SYMBOL], [';'])
        return


    def _compileStatements(self):
        while self._eatExpected([T_KEYWORD], [K_LET, K_IF, K_WHILE, K_DO, K_RETURN]):
            self._compileStatementByKeyword()
        return

    def _compileLetStatement(self):
        self._eatObligatory([T_IDENTIFIER])
        name = self._currentToken['value']
        segment, index = self._searchVariableByName(name)
        
        isArrayAssignment = False
        if self._eatExpected([T_SYMBOL], ['[']):
            self._compileArrayPosition(name)
            isArrayAssignment = True

        self._eatObligatory([T_SYMBOL], ['='])
        self._compileExpression()
        if isArrayAssignment:
            self._writer.writePop(SEGMENT_TEMP, 0)
            self._writer.writePop(SEGMENT_POINTER, 1)
            self._writer.writePush(SEGMENT_TEMP, 0)
            self._writer.writePop(SEGMENT_THAT, 0)
        else:
            self._writer.writePop(segment, index)
        self._eatObligatory([T_SYMBOL], [';'])
        return

    def _compileIfStatement(self):
        funcName = self._className + '.' + self._currentCompilingFunction['name']
        notIfLabel = f'{funcName}_NOT_IF_{self._numberConditionalsStatementsCurrentFunction}' 
        endComparisonLabel = f'{funcName}_END_COMPARISON_BLOCK_{self._numberConditionalsStatementsCurrentFunction}'
        self._numberConditionalsStatementsCurrentFunction += 1
        
        self._eatObligatory([T_SYMBOL], ['('])
        self._compileExpression()
        self._writer.writeArithmetic('not')
        self._eatObligatory([T_SYMBOL], [')'])
        self._writer.writeIf(notIfLabel)

        self._eatObligatory([T_SYMBOL], ['{'])
        self._compileStatements()
        self._eatObligatory([T_SYMBOL], ['}'])
        self._writer.writeGoto(endComparisonLabel)

        self._writer.writeLabel(notIfLabel)
        if self._eatExpected([T_KEYWORD], [K_ELSE]):
            self._eatObligatory([T_SYMBOL], ['{'])
            self._compileStatements()
            self._eatObligatory([T_SYMBOL], ['}'])
        self._writer.writeLabel(endComparisonLabel)
        return

    def _compileWhileStatement(self):
        funcName = self._className + '.' + self._currentCompilingFunction['name']
        loopLabel = f'{funcName}_LOOP_{self._numberConditionalsStatementsCurrentFunction}' 
        endLoopLabel = f'{funcName}_END_LOOP_{self._numberConditionalsStatementsCurrentFunction}' 
        self._numberConditionalsStatementsCurrentFunction += 1

        self._writer.writeLabel(loopLabel)
        self._eatObligatory([T_SYMBOL], ['('])
        self._compileExpression()
        self._writer.writeArithmetic('not')
        self._eatObligatory([T_SYMBOL], [')'])
        self._writer.writeIf(endLoopLabel)

        self._eatObligatory([T_SYMBOL], ['{'])
        self._compileStatements()
        self._eatObligatory([T_SYMBOL], ['}'])
        self._writer.writeGoto(loopLabel)
        self._writer.writeLabel(endLoopLabel)
        return

    def _compileDoStatement(self):
        self._compileSubroutineCall()
        self._writer.writePop(SEGMENT_TEMP, 0)
        self._eatObligatory([T_SYMBOL], [';'])
        return
    
    def _compileReturnStatement(self):
        if self._eatExpected([T_SYMBOL], [';']):
            self._writer.writePush(SEGMENT_CONST, 0)
        else:
            self._compileExpression()
            self._eatObligatory([T_SYMBOL], [';'])
        self._writer.writeReturn()
        return

    def _compileExpression(self):
        self._compileTerm()
        if self._eatExpected([T_SYMBOL], ['+', '-', '*', '/', '&', '|', '<', '>', '=']):
            operator = self._currentToken['value']
            self._compileTerm()
            self._writer.writeArithmetic(VM_COMMAND_BY_JACK_OPERATOR[operator])
        return

    def _compileTerm(self):
        requiredTypes = [T_INTEGER_CONSTANT, T_STRING_CONSTANT, T_KEYWORD, T_IDENTIFIER, T_SYMBOL]
        requiredValues = [K_TRUE, K_FALSE, K_NULL, K_THIS, '(', '-', '~']
        self._eatObligatory(requiredTypes, requiredValues)
        tokenType = self._currentToken['type']
        
        if tokenType == T_INTEGER_CONSTANT:
            integer = self._currentToken['value']
            self._writer.writePush(SEGMENT_CONST, integer)

        elif tokenType == T_STRING_CONSTANT:
            stringConst = self._currentToken['value'].replace('"', '')
            self._writer.writePush(SEGMENT_CONST, len(stringConst))
            self._writer.writeCall('String.new', 1)
            for char in stringConst:
                self._writer.writePush(SEGMENT_CONST, ord(char))
                self._writer.writeCall('String.appendChar', 2)
        
        elif tokenType == T_KEYWORD:
            constant = self._currentToken['value']
            if constant == K_FALSE or constant == K_NULL:
                self._writer.writePush(SEGMENT_CONST, 0)
            elif constant == K_TRUE:
                self._writer.writePush(SEGMENT_CONST, 1)
                self._writer.writeArithmetic('neg')
            else:
                self._writer.writePush(SEGMENT_POINTER, 0)

        elif tokenType == T_SYMBOL:
            symbol = self._currentToken['value']
            if symbol == '(':
                self._compileExpression()
                self._eatObligatory([T_SYMBOL], [')'])
            else:
                unaryOperation = 'neg' if symbol == '-' else 'not'
                self._compileTerm()
                self._writer.writeArithmetic(unaryOperation)

        elif tokenType == T_IDENTIFIER:
            name = self._currentToken['value']
            if self._eatExpected([T_SYMBOL], ['[', '.', '(']):
                symbol = self._currentToken['value']

                if symbol == '[':
                    self._compileArrayPosition(name)
                    self._writer.writePop(SEGMENT_POINTER, 1)
                    self._writer.writePush(SEGMENT_THAT, 0)
                else:
                    self._preserveCurrentToken = True
                    self._compileSubroutineCall(name)
            else:
                segment, index = self._searchVariableByName(name)
                self._writer.writePush(segment, index)
        return

    def _compileExpressionList(self):
        nArgs = 0
        if not self._eatExpected([T_SYMBOL], [')']):
            self._compileExpression()
            nArgs += 1
            while self._eatExpected([T_SYMBOL], [',']):
                self._compileExpression()
                nArgs += 1
        self._preserveCurrentToken = True
        return nArgs

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
        return

    def _compileSubroutineCall(self, name = None):
        if name is None:
            self._eatObligatory([T_IDENTIFIER])
            name = self._currentToken['value']
        
        nArgs = 0
        if self._eatExpected([T_SYMBOL], ['.']):
            self._eatObligatory([T_IDENTIFIER])
            funcName = self._currentToken["value"]
            varInfo = self._searchVariableByName(name)
            if varInfo is not None:
                segment, index = varInfo
                self._writer.writePush(segment, index)
                nArgs += 1
            else: 
                funcName = f'{name}.{funcName}'
        else:
            funcName = name
                
        self._eatObligatory([T_SYMBOL], ['('])
        nArgs += self._compileExpressionList()
        self._eatObligatory([T_SYMBOL], [')'])
        self._writer.writeCall(funcName, nArgs)
        return

    def _compileConstructorCode(self):
        nArgs = self._subroutineVariables.getVarCountByKind(VAR_ARG)
        self._writer.writePush(SEGMENT_CONST, nArgs)
        self._writer.writeCall('Memory.alloc', 1)
        self._writer.writePop(SEGMENT_POINTER, 0)
        return

    def _compileMethodCode(self):
        self._writer.writePush(SEGMENT_ARG, 0)
        self._writer.writePop(SEGMENT_POINTER, 0)
        return

    def _compileArrayPosition(self, arrName):
        arrayBaseAddr = self._searchVariableByName(arrName)
        segment, index = arrayBaseAddr

        self._writer.writePush(segment, index)
        self._compileExpression()
        self._writer.writeArithmetic('add')

        self._eatObligatory([T_SYMBOL], [']'])
        return

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
                self._writer.writeCompilationError(f'SYNTAX ERROR!')
                self._writer.writeCompilationError(f'TOKEN GIVEN: {self._currentToken}')
                self._writer.writeCompilationError(f'EXPECTED: {requiredTokenValues} in {requiredTokenTypes}')
                exit(1)
        return

    def _eatExpected(self, expectedTokenTypes, expectedTokenValues = []):
        self._currentToken = self._currentToken if self._preserveCurrentToken else self._tokenizer.advance()
        ateExpected = (self._currentToken['type'] in expectedTokenTypes and 
                (self._currentToken['type'] not in TOKEN_TYPES_WITH_EXPECTABLE_VALUES or 
                len(expectedTokenValues) == 0 or self._currentToken['value'] in expectedTokenValues)) 
        self._preserveCurrentToken = not ateExpected
        return ateExpected

    def _searchVariableByName(self, name):
        subroutineVar = self._subroutineVariables.getByName(name)
        if subroutineVar is not None:
            return subroutineVar['segment'], subroutineVar['index']
        classVar = self._classVariables.getByName(name)
        if classVar is not None:
            return classVar['segment'], classVar['index']
        return None 