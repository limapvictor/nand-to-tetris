import sys

class SymbolTable:
    def __init__(self):
        self.table = {
            'SCREEN': 16384,
            'KBD': 24576,
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
        }
        for i in range(16):
            self.table[f'R{i}'] = i
        self.first_free_address = 16

    def get_or_insert_symbol(self, symbol):
        if symbol not in self.table:
           self.table[symbol] = self.first_free_address
           self.first_free_address += 1
        return self.table[symbol]
   
    def insert_label(self, label, address):
        self.table[label] = address

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
        self.symbol_table = SymbolTable()

    def _is_symbol_address(self, address):
        try:
            int(address)
            return False
        except:
            return True

    def translate_A_instruction(self, address):
        if (self._is_symbol_address(address)):
            address = self.symbol_table.get_or_insert_symbol(address)
        return format(int(address), '016b')

    def _translate_dest_bits(self, dest):
        dest_bits = ['0', '0', '0']
        for index, register in enumerate(['A', 'D', 'M']):
            if register in dest:
                dest_bits[index] = '1'
        return ''.join(dest_bits)

    def translate_C_instruction(self, computation_register, comp, dest, jmp):
        translated_computation_register = '0' if computation_register == 'A' else '1'
        translated_comp = self.COMP_TRANSLATE_TABLE[comp]
        translated_dest = self._translate_dest_bits(dest)
        translated_jmp = self.JUMP_TRANSLATE_TABLE[jmp]
        return (self.C_INSTRUCTION_BEGIN + translated_computation_register + translated_comp
            + translated_dest + translated_jmp)
    
    def insert_label(self, label, address):
        self.symbol_table.insert_label(label, address)

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
        attrib_index = instruction.find('=')
        comma_index = instruction.find(';')
        dest = instruction[:attrib_index] if attrib_index != -1 else ''
        comp = instruction[attrib_index + 1 : comma_index] if comma_index != -1 else instruction[attrib_index + 1 :]
        jmp = instruction[comma_index + 1:] if comma_index != -1 else ''
        computation_register = 'M' if comp.find('M') != -1 else 'A'
        comp = comp.replace('A', 'Y').replace('M', 'Y')
        return self.translator.translate_C_instruction(computation_register, comp, dest, jmp)

    def _parse_Label_instruction(self, instruction):
        label = instruction.replace('(', '').replace(')', '')
        label_address = len(self.assembly_instructions)
        self.translator.insert_label(label, label_address)
    
    def first_pass(self):
        for line in self.source:
            instruction = self._remove_spaces_and_comments(line)
            if instruction != '':
                instruction_type = self._get_instruction_type(instruction)
                if instruction_type == self.LABEL_INSTRUCTION:
                    self._parse_Label_instruction(instruction)
                else:
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
