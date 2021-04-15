import sys
import os.path

from CompilationEngine import CompilationEngine

class JackCompiler:
    def __init__(self, path):
        if os.path.isfile(path):
            self._files = [path]
        elif os.path.isdir(path):
            self._files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.jack')]

    def compileJ(self):
        for file in self._files:
            engine = CompilationEngine(file)
            engine.run()

def main():
    path = sys.argv[1]
    compiler = JackCompiler(path)
    compiler.compileJ()
    return 0

if __name__ == '__main__':
    main()