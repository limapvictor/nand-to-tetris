import sys

C_ARITHMETIC = 0
C_PUSH = 1
C_POP = 2

class CodeWriter:
    ASSIGN_MEMORY_WITH_D_REGISTER = 'assignment'

    AUX_REGISTER_A_COMMAND = '@R13'
    
    ASSEMBLY_OPERATION_BY_VM_OPERATION = {
        'add': 'M+D',
        'sub': 'M-D',
        'neg': '-M',
        'eq': 'M-D',
        'gt': 'M-D',
        'lt': 'M-D',
        'and': 'M&D',
        'or': 'M|D',
        'not': '!M', 
        ASSIGN_MEMORY_WITH_D_REGISTER: 'D'        
    }

    ASSEMBLY_JUMP_BY_VM_OPERATION = {
        'eq': 'JEQ',
        'gt': 'JGT',
        'lt': 'JLT',
    }

    ASSEMBLY_POINTER_BY_SEGMENT = {
        'local': 'LCL',
        'argument': 'ARG',
        'this': 'THIS',
        'that': 'THAT',
    }

    def __init__(self, filepath):
        output_filepath = self._get_output_filepath(filepath)
        self.output_file = open(output_filepath, 'w')
        self._current_assembly_instructions = []
        self._comparisons_made = 0

    def write(self, command_type, arg1, arg2, vm_command):
        TRANSLATE_FUNCTIONS_BY_COMMAND_TYPE = {
            C_ARITHMETIC: self._translate_arithmetic,
            C_PUSH: self._translate_push,
            C_POP: self._translate_pop,
        }
        TRANSLATE_FUNCTIONS_BY_COMMAND_TYPE[command_type](arg1, arg2)
        assembly_code = '\n'.join(self._current_assembly_instructions)
        
        self.output_file.write(f'//{vm_command}\n')
        self.output_file.write(assembly_code + '\n')
        
        self._current_assembly_instructions = []
    
    def close(self):
        self.output_file.close()

    #translate functions
    def _translate_arithmetic(self, operation, arg2 = None):
        self._decrement_SP()
        if not self._is_unary(operation):
            self._pop_on_D_register()
            self._decrement_SP()
        self._push_operation_result(operation)
        if self._is_comparison(operation):
            self._put_comparison_result_on_D_register(operation)
            self._push_operation_result(self.ASSIGN_MEMORY_WITH_D_REGISTER)
        self._increment_SP()
    
    def _translate_push(self, segment, index):
        self._set_D_register_with_memory_value(segment, index)
        self._push_operation_result(self.ASSIGN_MEMORY_WITH_D_REGISTER)
        self._increment_SP()
    
    def _translate_pop(self, segment, index):
        self._set_aux_register_with_memory_address(segment, index)
        self._decrement_SP()
        self._pop_on_D_register()
        self._set_memory_address_with_D_register()

    #aux functions
    def _get_output_filepath(self, filepath):
        extension_index = filepath.rfind('.')
        directory_index = filepath.rfind('/')
        self._class_name = filepath[directory_index + 1 : extension_index]
        return f'{filepath[:extension_index]}.asm'
    
    def _get_address_by_segment_and_index(self, segment, index):
        if segment == 'temp':
            return str(5 + int(index))
        if segment == 'static':
            return f'{self._class_name}.{index}'
        if segment == 'pointer':
            return 'THIS' if index == 0 else 'THAT'

    def _is_unary(self, operation):
        return operation in ['neg', 'not']

    def _is_comparison(self, operation):
        return operation in ['eq', 'gt', 'lt']

    #assembly commands
    def _increment_SP(self):
        self._current_assembly_instructions += [
            '@SP',
            'M=M+1',
        ]

    def _decrement_SP(self):
        self._current_assembly_instructions += [
            '@SP',
            'M=M-1',
        ]

    def _pop_on_D_register(self):
        self._current_assembly_instructions += [
            '@SP',
            'A=M',
            'D=M',
        ]

    def _push_operation_result(self, operation):
        assembly_operation = self.ASSEMBLY_OPERATION_BY_VM_OPERATION[operation]

        self._current_assembly_instructions += [
            '@SP',
            'A=M',
            f'MD={assembly_operation}'
        ]

    def _put_comparison_result_on_D_register(self, operation):
        assembly_jump = self.ASSEMBLY_JUMP_BY_VM_OPERATION[operation]
        comparison_label = f'COMPARISON_TRUE_{self._comparisons_made}'
        end_label = f'END_OF_COMPARISON_{self._comparisons_made}'
        self._comparisons_made += 1

        self._current_assembly_instructions += [
            f'@{comparison_label}',
            f'D;{assembly_jump}',
            'D=0',
            f'@{end_label}',
            '0;JMP',
            f'({comparison_label})',
            'D=-1',
            f'({end_label})',
        ]

    def _set_D_register_with_memory_value(self, segment, index):
        if segment == 'constant':
            self._current_assembly_instructions += [
                f'@{index}',
                'D=A',
            ]

        if segment in ['temp', 'pointer', 'static']:
            address = self._get_address_by_segment_and_index(segment, index)
            
            self._current_assembly_instructions += [
                f'@{address}',
                'D=M',
            ]

        if segment in self.ASSEMBLY_POINTER_BY_SEGMENT:
            pointer = self.ASSEMBLY_POINTER_BY_SEGMENT[segment]
            
            self._current_assembly_instructions += [
                f'@{index}',
                'D=A',
                f'@{pointer}',
                'A=M+D',
                'D=M',
            ]

    def _set_aux_register_with_memory_address(self, segment, index):
        if segment in ['temp', 'pointer', 'static']:
            address = self._get_address_by_segment_and_index(segment, index)
            
            self._current_assembly_instructions += [
                f'@{address}',
                'D=A',
                self.AUX_REGISTER_A_COMMAND,
                'M=D',
            ]

        if segment in self.ASSEMBLY_POINTER_BY_SEGMENT:
            pointer = self.ASSEMBLY_POINTER_BY_SEGMENT[segment]
            
            self._current_assembly_instructions += [
                f'@{index}',
                'D=A',
                f'@{pointer}',
                'D=M+D',
                self.AUX_REGISTER_A_COMMAND,
                'M=D',
            ]

    def _set_memory_address_with_D_register(self):
        self._current_assembly_instructions += [
            self.AUX_REGISTER_A_COMMAND,
            'A=M',
            'M=D',
        ]

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
        else:
            return self._current_command[1]
    
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

class VMTranslator:
    def __init__(self, filepath):
        self.filepath = filepath
        self.parser = Parser(filepath)
        self.writer = CodeWriter(filepath)
    
    def translate(self):
        while self.parser.has_more_commands():
            self.parser.advance()
            self.writer.write(self.parser.command_type(), self.parser.arg1(), self.parser.arg2(), self.parser.vm_command())
        self._close_files()

    def _close_files(self):
        self.parser.close()
        self.writer.close()

def main():
    filepath = sys.argv[1]
    translator = VMTranslator(filepath)
    translator.translate()
    return 0

if __name__ == '__main__':
    main()