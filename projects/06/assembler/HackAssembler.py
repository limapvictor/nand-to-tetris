import sys

class Translator:
    
    COMP_TRANSLATE_TABLE = {
        '0': '101010',
        '1': '111111',
        '-1': '111010',
        'D': '001100',
        'Y': '110000',
        '!D': '001101',
        '!Y': '110001',
        '-D': '001111',
        '-Y': '110011',
        'D+1': '011111',
        'Y+1': '110111',
        'D-1': '001110',
        'Y-1': '110010',
        'D+Y': '000010',
        'D-Y': '010011',
        'Y-D': '000111',
        'D&Y': '000000',
        'D|Y': '010101',
    }

    JUMP_TRANSLATE_TABLE = {
        '': '000',
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111'
    }
    
    C_INSTRUCTION_BEGIN = '111'

    def __init__(self):
        pass

    def _is_symbol_address(self, address):
        try:
            int(address)
            return False
        except:
            return True

    def translate_A_instruction(self, address):
        return format(int(address), '016b')

    def _translate_dest_bits(self, dest):
        dest_bits = ['0', '0', '0']
        if 'M' in dest:
            dest_bits[2] = '1'
        if 'D' in dest:
            dest_bits[1] = '1'
        if 'A' in dest:
            dest_bits[0] = '1'
        return ''.join(dest_bits)

    def translate_C_instruction(self, computation_register, comp, dest, jmp):
        translated_computation_register = '0' if computation_register == 'A' else '1'
        translated_comp = self.COMP_TRANSLATE_TABLE[comp]
        translated_dest = self._translate_dest_bits(dest)
        translated_jmp = self.JUMP_TRANSLATE_TABLE[jmp]
        return (self.C_INSTRUCTION_BEGIN + translated_computation_register + translated_comp
            + translated_dest + translated_jmp)

class Parser:
    
    A_INSTRUCTION = 0
    C_INSTRUCTION = 1
    LABEL_INSTRUCTION = 2
    
    def __init__(self, filepath):
        self.source = open(filepath, 'r')
        self.assembly_instructions = []
        self.translator = Translator()

    def _remove_spaces_and_comments(self, line):
        formatted_line = line.replace('\n', '').replace(' ', '')
        comments_index = formatted_line.find('//')
        formatted_line = formatted_line[:comments_index] if comments_index != -1 else formatted_line
        return formatted_line

    def _get_instruction_type(self, instruction):
        if instruction[0] == '(':
            return self.LABEL_INSTRUCTION
        return self.A_INSTRUCTION if instruction[0] == '@' else self.C_INSTRUCTION
    
    def _parse_A_instruction(self, instruction):
        return self.translator.translate_A_instruction(instruction[1:])

    def _parse_C_instruction(self, instruction):
        parsed_instruction = instruction.split('=')
        if len(parsed_instruction) > 1 :
            dest = parsed_instruction[0]
            comp = parsed_instruction[1]
        else:
            dest = ''
            comp = parsed_instruction[0]
        parsed_instruction = comp.split(';')
        if len(parsed_instruction) > 1 :
            comp = parsed_instruction[0]
            jmp = parsed_instruction[1]
        else:
            jmp = ''
            comp = parsed_instruction[0]
        computation_register = 'M' if comp.find('M') != -1 else 'A'
        comp = comp.replace('A', 'Y').replace('M', 'Y')
        return self.translator.translate_C_instruction(computation_register, comp, dest, jmp)

    def _parse_Label_instruction(self, instruction):
        return instruction
    
    def first_pass(self):
        for line in self.source:
            instruction = self._remove_spaces_and_comments(line)
            if instruction != '':
                instruction_type = self._get_instruction_type(instruction)
                self.assembly_instructions.append([instruction, instruction_type])
        self.source.close()

    def second_pass(self):
        machine_instructions = []
        parse_functions = [self._parse_A_instruction, self._parse_C_instruction]
        for [instruction, instruction_type] in self.assembly_instructions:
            machine_instruction = parse_functions[instruction_type](instruction)
            machine_instructions.append(machine_instruction)
        return machine_instructions

class HackAssembler:
    def __init__(self, filepath):
        self.filepath = filepath
        self.parser = Parser(filepath)
        self.machine_instructions = []

    def __get_destination_filepath(self):
        extension_index = self.filepath.find('.asm')
        return f'{self.filepath[:extension_index]}.hack'

    def _write_instructions(self):
        destination = open(self.__get_destination_filepath(), 'w')
        for instruction in self.machine_instructions:
            destination.write(instruction + '\n')
        destination.close()
    
    def assemble(self):
        self.parser.first_pass()
        self.machine_instructions = self.parser.second_pass()
        self._write_instructions()

def main():
    filepath = sys.argv[1]
    assembler =  HackAssembler(filepath)
    assembler.assemble()
    return 0

if __name__ == '__main__':
    main()
