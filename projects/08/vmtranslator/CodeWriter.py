from Helper import *

class CodeWriter:
    ASSIGN_MEMORY_WITH_D_REGISTER = 'assignment'

    MEMORY_AUX_REGISTER = 'R13'
    RETURN_REGISTER = 'R14'
    ENDFRAME_REGISTER = 'R15'
    
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
        self._current_function_name = ''
        self._n_call_commands_on_current_function = 0
        if is_directory:
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
            C_CALL: self._translate_call,
            C_RETURN: self._translate_return,
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
        self._set_memory_value_with_D_register(self.MEMORY_AUX_REGISTER)

    def _translate_label(self, label, arg2 = None):
        label = f'{self._current_function_name}${label}'

        self._set_assembly_label(label)

    def _translate_goto(self, label, arg2 = None):
        label = f'{self._current_function_name}${label}'

        self._jump_to_address(label, '0', 'JMP')

    def _translate_if(self, label, arg2 = None):
        label = f'{self._current_function_name}${label}'
        
        self._decrement_SP()
        self._pop_on_D_register()
        self._jump_to_address(label, 'D', 'JNE')

    def _translate_func(self, function_name, n_local_vars):
        self._current_function_name = function_name
        self._n_call_commands_on_current_function = 0

        self._set_assembly_label(function_name)
        for i in range(n_local_vars):
            self._translate_push('constant', 0)

    def _translate_call(self, function_name, n_function_args):
        return_label = f'{self._current_function_name}$ret.{self._n_call_commands_on_current_function}'
        self._n_call_commands_on_current_function += 1

        self._translate_push('constant', return_label)
        for pointer in self.ASSEMBLY_POINTER_BY_SEGMENT.values():
            self._set_D_register_with_pointer(pointer)
            self._push_operation_result(self.ASSIGN_MEMORY_WITH_D_REGISTER)
            self._increment_SP()
        self._update_ARG_after_call_command(n_function_args)
        self._update_LCL_after_call_command()
        self._jump_to_address(function_name, '0', 'JMP');
        self._set_assembly_label(return_label)

    def _translate_return(self, arg1 = None, arg2 = None):
        self._set_endframe_with_LCL()
        self._reset_pointer_in_endframe(self.RETURN_REGISTER, 5)
        self._decrement_SP()
        self._pop_on_D_register()
        self._set_memory_value_with_D_register('ARG')
        self._set_aux_register_with_memory_address('argument', 1)
        self._set_D_register_with_pointer(self.MEMORY_AUX_REGISTER)
        self._set_pointer_with_D_register('SP')
        offset = 4
        for pointer in self.ASSEMBLY_POINTER_BY_SEGMENT.values():
            self._reset_pointer_in_endframe(pointer, offset)
            offset -= 1
        self._goto_return_address()

    #aux functions
    def _get_output_filepath(self, path, is_directory):
        directory_index = path.rfind('/')
        extension_index = path.rfind('.')
        if is_directory:
            return f'{path}/{path[directory_index + 1 :]}.asm'
        return f'{path[: extension_index]}.asm'

    def _write_init(self):
        self._current_assembly_instructions += [
            '//Bootstrap code',
            '//SP = 256',
            '@256',
            'D=A',
            '@SP',
            'M=D',
        ]
        self._translate_call('Sys.init', 0)

        bootstrap_code = '\n'.join(self._current_assembly_instructions)
        self.output_file.write(bootstrap_code + '\n')

        self._current_assembly_instructions = []

    
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
                f'@{self.MEMORY_AUX_REGISTER}',
                'M=D',
            ]

        if segment in self.ASSEMBLY_POINTER_BY_SEGMENT:
            pointer = self.ASSEMBLY_POINTER_BY_SEGMENT[segment]
            
            self._current_assembly_instructions += [
                f'@{index}',
                'D=A',
                f'@{pointer}',
                'D=M+D',
                f'@{self.MEMORY_AUX_REGISTER}',
                'M=D',
            ]

    def _set_memory_value_with_D_register(self, pointer):
        self._current_assembly_instructions += [
            f'@{pointer}',
            'A=M',
            'M=D',
        ]

    def _set_D_register_with_pointer(self, pointer):
        self._current_assembly_instructions += [
            f'@{pointer}',
            'D=M',
        ]

    def _set_pointer_with_D_register(self, pointer):
        self._current_assembly_instructions += [
            f'@{pointer}',
            'M=D',
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

    def _update_ARG_after_call_command(self, n_function_args):
        self._current_assembly_instructions += [
            '@5',
            'D=A',
            f'@{n_function_args}',
            'D=D+A',
            f'@{self.MEMORY_AUX_REGISTER}',
            'M=D',
            '@SP',
            'D=M',
            f'@{self.MEMORY_AUX_REGISTER}',
            'D=D-M',
            '@ARG',
            'M=D',
        ]
        
    def _update_LCL_after_call_command(self):
        self._set_D_register_with_pointer('SP')
        self._set_pointer_with_D_register('LCL')

    def _set_endframe_with_LCL(self):
        self._set_D_register_with_pointer('LCL')
        self._set_pointer_with_D_register(self.ENDFRAME_REGISTER)

    def _reset_pointer_in_endframe(self, pointer, offset):
        self._current_assembly_instructions += [
            f'@{offset}',
            'D=A',
            f'@{self.ENDFRAME_REGISTER}',
            'A=M-D',
            'D=M',
            f'@{pointer}',
            'M=D',
        ]

    def _goto_return_address(self):
        self._current_assembly_instructions += [
            f'@{self.RETURN_REGISTER}',
            'A=M',
            '0;JMP',
        ]