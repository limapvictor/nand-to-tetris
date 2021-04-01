from Helper import *

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

    def __init__(self, path, is_directory):
        output_filepath = self._get_output_filepath(path, is_directory)
        self.output_file = open(output_filepath, 'w')
        self._current_assembly_instructions = []
        self._comparisons_made = 0
        self._write_init()

    def write(self, command_type, arg1, arg2, vm_command):
        TRANSLATE_FUNCTIONS_BY_COMMAND_TYPE = {
            C_ARITHMETIC: self._translate_arithmetic,
            C_PUSH: self._translate_push,
            C_POP: self._translate_pop,
            C_LABEL: self._translate_label,
            C_GOTO: self._translate_goto,
            C_IF: self._translate_if,
            C_FUNC: self._translate_func,
        }
        TRANSLATE_FUNCTIONS_BY_COMMAND_TYPE[command_type](arg1, arg2)
        assembly_code = '\n'.join(self._current_assembly_instructions)
        
        self.output_file.write(f'//{vm_command}\n')
        self.output_file.write(assembly_code + '\n')
        
        self._current_assembly_instructions = []
    
    def close(self):
        self.output_file.close()

    def update_classname_by_filename(self, filepath):
        directory_index = filepath.rfind('/')
        extension_index = filepath.rfind('.')
        self._class_name = filepath[directory_index + 1 : extension_index]

    #translate functions
    def _translate_arithmetic(self, operation, arg2 = None):
        self._decrement_SP()
        if not self._is_unary(operation):
            self._pop_on_D_register()
            self._decrement_SP()
        self._push_operation_result(operation)
        if self._is_comparison(operation):
            self._set_D_register_with_comparion_result(operation)
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

    def _translate_label(self, label, arg2 = None):
        self._set_assembly_label(label)

    def _translate_goto(self, label, arg2 = None):
        self._jump_to_address(label, '0', 'JMP')

    def _translate_if(self, label, arg2 = None):
        self._decrement_SP()
        self._pop_on_D_register()
        self._jump_to_address(label, 'D', 'JNE')

    #aux functions
    def _get_output_filepath(self, path, is_directory):
        directory_index = path.rfind('/')
        extension_index = path.rfind('.')
        if is_directory:
            return f'{path}/{path[directory_index + 1 :]}.asm'
        return f'{path[: extension_index]}.asm'

    def _write_init(self):
        bootstrap_code = [
            '//Bootstrap code',
            'SP=256',
            'Call Sys.init'
        ]
        bootstrap_code = '\n'.join(bootstrap_code)
        self.output_file.write(bootstrap_code + '\n')
    
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

    def _set_D_register_with_comparion_result(self, operation):
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

    def _set_D_register_with_pointer(self, pointer):
        self._current_assembly_instructions += [
            f'@{pointer}',
            'D=M',
        ]

    def _set_assembly_label(self, label):
        self._current_assembly_instructions += [
            f'({label})'
        ]

    def _jump_to_address(self, address, computation, condition):
        self._current_assembly_instructions += [
            f'@{address}',
            f'{computation};{condition}',
        ]