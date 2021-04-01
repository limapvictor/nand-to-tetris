import sys
import os.path

from Parser import Parser
from CodeWriter import CodeWriter

class VMTranslator:
    def __init__(self, path):
        is_directory = False
        if os.path.isfile(path):
            self.files = [path]
        elif os.path.isdir(path):
            self.files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.vm')]
            is_directory = True

        self.parser = None
        self.writer = CodeWriter(path, is_directory)
    
    def translate(self):
        for file in self.files:
            self.parser = Parser(file)
            self.writer.update_classname_by_filename(file)
            while self.parser.has_more_commands():
                self.parser.advance()
                self.writer.write(self.parser.command_type(), self.parser.arg1(), self.parser.arg2(), self.parser.vm_command())
            self.parser.close()
        self.writer.close()

def main():
    path = sys.argv[1]
    translator = VMTranslator(path)
    translator.translate()
    return 0

if __name__ == '__main__':
    main()