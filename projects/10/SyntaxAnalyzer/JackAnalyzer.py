import sys
import os.path

from CompilationEngine import CompilationEngine

class JackAnalyzer:
    def __init__(self, path):
        if os.path.isfile(path):
            self._files = [path]
        elif os.path.isdir(path):
            self._files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.jack')]

    def analyze(self):
        for file in self._files:
            engine = CompilationEngine(file)
            engine.constructParseTree()

def main():
    path = sys.argv[1]
    analyzer = JackAnalyzer(path)
    analyzer.analyze()
    return 0

if __name__ == '__main__':
    main()