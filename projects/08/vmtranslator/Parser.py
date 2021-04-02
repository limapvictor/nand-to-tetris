from Helper import *

class Parser:
    COMMAND_TYPE = {
        'add': C_ARITHMETIC,
        'sub': C_ARITHMETIC,
        'neg': C_ARITHMETIC,
        'eq': C_ARITHMETIC,
        'gt': C_ARITHMETIC,
        'lt': C_ARITHMETIC,
        'and': C_ARITHMETIC,
        'or': C_ARITHMETIC,
        'not': C_ARITHMETIC,
        'push': C_PUSH,
        'pop': C_POP,
        'label': C_LABEL,
        'goto': C_GOTO,
        'if-goto': C_IF,
        'function': C_FUNC,
        'call': C_CALL,
        'return': C_RETURN,
    }
    
    def __init__(self, filepath):
        self._input_file = open(filepath, 'r')
        self._current_line = self._input_file.readline()
        self._current_command = []
        self._vm_current_command = ''

    def has_more_commands(self):
        return self._current_line != ''
    
    def advance(self):
        while True:
            line = self._remove_chars_and_comments(self._current_line)
            self._current_command = line.split()
            self._vm_current_command = line
            self._current_line = self._input_file.readline()
            if len(self._current_command) > 0:
                break

    def command_type(self):
        command = self._current_command[0]
        return self.COMMAND_TYPE[command]

    def arg1(self):
        if self.command_type() == C_ARITHMETIC:
            return self._current_command[0]
        if self.command_type() != C_RETURN:
            return self._current_command[1]
        return None
    
    def arg2(self):
        if len(self._current_command) >= 3:
            return int(self._current_command[2])
        return None

    def vm_command(self):
        return self._vm_current_command

    def close(self):
        self._input_file.close()

    def _remove_chars_and_comments(self, line):
        formatted_line = line.replace('\n', '').replace('\r', '')
        formatted_line = formatted_line.split('//')[0]
        return formatted_line