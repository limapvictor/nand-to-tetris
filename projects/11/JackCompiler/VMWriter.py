class VMWriter:
    def __init__(self, filepath):
        file = filepath.replace('.jack', '.vm')
        self._outputFile = open(file, 'w')

    def writePush(self, segment, index):
        self._outputFile.write(f'push {segment} {index}')
    
    def writePop(self, segment, index):
        self._outputFile.write(f'pop {segment} {index}')
    
    def writeArithmetic(self, operation):
        self._outputFile.write(operation)

    def writeLabel(self, label):
        self._outputFile.write(f'label {label}')

    def writeGoto(self, label):
        self._outputFile.write(f'goto {label}')
        
    def writeIf(self, label):
        self._outputFile.write(f'if-goto {label}')

    def writeCall(self, funcName, nArgs):
        self._outputFile.write(f'call {funcName} {nArgs}')

    def writeFunction(self, funcName, nLocalVars):
        self._outputFile.write(f'function {funcName} {nLocalVars}')

    def writeReturn(self):
        self._outputFile.write('return')

    def writeCompilationError(self, error):
        self._outputFile.write(f'COMPILATION ERROR -> {error}')

    def close(self):
        self._outputFile.close()