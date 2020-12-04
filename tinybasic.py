"""Tiny BASIC IL interpreter.

This file contains an interpreter for the Tiny BASIC interpretive language
(IL), as described in Dr Dobb's Journal, Vol.1, No.1 (Jan 1976). The IL, in
turn, is used to implement Tiny BASIC, a limited subset of BASIC intended to
run on low-memory (2-4K) machines. See `tinybasic.il` and `tbx.il` for BASIC
interpreters written in IL.

Run this file with the `-x` option for Tiny BASIC Extended (TBX).
Run this file with the `-f` option to load a BASIC program on startup.
"""
import random
import re


class TinyBasicInterpreter:

    def __init__(self, il_code='tinybasic.il', max_lines=256,
                 greeting='Tiny BASIC\n\n',
                 command_prompt='? ', input_prompt='> ',
                 enable_multistatement=False, autoload=[]):
        self.pc = 0
        self.il_program = []
        self.il_labels = {}

        self.line_buffer = ''
        self.line_buffer_buffer = autoload
        self.innum_buffer = []
        self.max_lines = max_lines
        self.basic_linenum = 0
        self.basic_program = ['' for _ in range(max_lines)]
        self.basic_var_data = [0 for _ in range(26)]
        self.basic_array_widths = [0 for _ in range(26)]
        self.listing_range = [n for n in range(max_lines)]

        self.expression_stack = []
        self.control_stack = []
        self.subroutine_stack = []

        self.user_quit = False

        with open(il_code, 'r') as f:
            self.load_interpreter(f.readlines())

        self.greeting = greeting
        self.command_prompt = command_prompt
        self.input_prompt = input_prompt

        self.il_ops = {}
        self.il_ops['ADD'] = self.il_add
        self.il_ops['ARRAY1'] = self.il_array1      # TBX
        self.il_ops['ARRAY2'] = self.il_array2      # TBX
        self.il_ops['CMPR'] = self.il_cmpr
        self.il_ops['DIM1'] = self.il_dim1          # TBX
        self.il_ops['DIM2'] = self.il_dim2          # TBX
        self.il_ops['DIV'] = self.il_div
        self.il_ops['DONE'] = self.il_done_tbx if enable_multistatement else self.il_done
        self.il_ops['DONEX'] = self.il_donex        # TBX
        self.il_ops['ERR'] = self.il_err
        self.il_ops['FIN'] = self.il_fin
        self.il_ops['FOR'] = self.il_for            # TBX
        self.il_ops['GETLN'] = self.il_getln
        self.il_ops['HOP'] = self.il_ijmp
        self.il_ops['ICALL'] = self.il_icall
        self.il_ops['IJMP'] = self.il_ijmp
        self.il_ops['IND'] = self.il_ind
        self.il_ops['INIT'] = self.il_init
        self.il_ops['INNUM'] = self.il_innum
        self.il_ops['INSRT'] = self.il_insrt
        self.il_ops['LIT'] = self.il_lit
        self.il_ops['LIST0'] = self.il_list0        # TBX
        self.il_ops['LIST1'] = self.il_list1        # TBX
        self.il_ops['LIST2'] = self.il_list2        # TBX
        self.il_ops['LST'] = self.il_lst
        self.il_ops['MPY'] = self.il_mpy
        self.il_ops['NEG'] = self.il_neg
        self.il_ops['NEXT'] = self.il_fornext       # TBX
        self.il_ops['NXT'] = self.il_nxt
        self.il_ops['NXTX'] = self.il_nxtx          # TBX
        self.il_ops['NLINE'] = self.il_nline
        self.il_ops['PRN'] = self.il_prn
        self.il_ops['PRS'] = self.il_prs
        self.il_ops['RANDOM'] = self.il_random      # TBX
        self.il_ops['RSTR'] = self.il_rstr
        self.il_ops['RTN'] = self.il_rtn
        self.il_ops['SAV'] = self.il_sav
        self.il_ops['SIZE'] = self.il_size          # TBX
        self.il_ops['SPC'] = self.il_spc
        self.il_ops['SPCONE'] = self.il_spcone      # TBX
        self.il_ops['STORE'] = self.il_store
        self.il_ops['SUB'] = self.il_sub
        self.il_ops['TAB'] = self.il_tab            # TBX
        self.il_ops['TST'] = self.il_tst
        self.il_ops['TSTA'] = self.il_tsta          # TBX
        self.il_ops['TSTF'] = self.il_tstf          # TBX
        self.il_ops['TSTL'] = self.il_tstl
        self.il_ops['TSTN'] = self.il_tstn
        self.il_ops['TSTV'] = self.il_tstv
        self.il_ops['XINIT'] = self.il_xinit
        self.il_ops['XFER'] = self.il_xfer


    def load_interpreter(self, lines):
        for ln in lines:
            bareln = ln.split(';', maxsplit=1)[0].strip()
            match = re.fullmatch(r'(?P<label>\w+:)?\s*(?P<instr>\w+)?\s*(?P<op1>[^,]+)?,?(?P<op2>.+)?', bareln)
            label = match.group('label')
            instr = match.group('instr')
            op1 = match.group('op1')
            op2 = match.group('op2')
            if instr is not None:
                stmt = [instr]
                if op1 is not None:
                    stmt.append(op1)
                if op1 is not None and op2 is not None:
                    stmt.append(op2.strip("'"))
                self.il_program.append(stmt)
                if label is not None:
                    label = label.strip(':')
                    if label in self.il_labels:
                        raise Exception
                    self.il_labels[label] = len(self.il_program) - 1
            pass

    #
    # Syntax parsing instructions
    #

    def il_done(self):
        self.line_buffer = self.line_buffer.strip()
        if self.line_buffer != '':
            print(f'Syntax error at line {self.basic_linenum - 1}.')
            self.pc = self.il_labels['ERRENT']


    def il_done_tbx(self):
        """Used only in TBX."""
        self.line_buffer = self.line_buffer.strip()
        if self.line_buffer.startswith('$'):        
            self.line_buffer = self.line_buffer[1:] 
            self.pc = self.il_labels['XEC']     
        elif self.line_buffer != '':
            print(f'Syntax error at line {self.basic_linenum - 1}.')
            self.pc = self.il_labels['ERRENT']


    def il_donex(self):
        """Used only in TBX."""
        self.il_done()


    def il_tst(self, dest_label, test_str):
        self.line_buffer = self.line_buffer.strip()
        if test_str.isdigit():
            ch = int(test_str)
            test_str = bytes([ch]).decode(encoding='ascii')
        if test_str == '\r' and self.line_buffer == '':
            pass
        elif self.line_buffer.upper().startswith(test_str):
            self.line_buffer = self.line_buffer[len(test_str):]
        else:
            self.fail_test(dest_label)


    def il_tsta(self, dest_label):
        """Used only in TBX."""
        self.line_buffer = self.line_buffer.strip()
        v = self.line_buffer[:1]
        if v.isalpha() and len(self.line_buffer) >= 2 and self.line_buffer[1] == '(':
            self.expression_stack.insert(0, ord(v.upper()) - ord('A'))
            self.line_buffer = self.line_buffer[1:]
        else:
            self.fail_test(dest_label)


    def il_tstf(self, dest_label):
        """Used only in TBX."""
        self.line_buffer = self.line_buffer.strip()
        if len(self.line_buffer) < 2 or not self.line_buffer[0:2].isalpha():
            self.fail_test(dest_label)


    def il_tstl(self, dest_label):
        head, _, _ = self.line_buffer.strip().partition(' ')
        try:
            line_num = int(head)
            if 1 <= line_num < self.max_lines:
                pass
            else:
                print('Invalid line number.')
                self.pc = self.il_labels['ERRENT']
        except ValueError:
            self.fail_test(dest_label)


    def il_tstn(self, dest_label):
        self.line_buffer = self.line_buffer.strip()
        n = ''
        while self.line_buffer[:1].isdigit():
            n += self.line_buffer[:1]
            self.line_buffer = self.line_buffer[1:]
        if len(n) > 0:
            self.expression_stack.insert(0, int(n))
        else:
            self.fail_test(dest_label)


    def il_tstv(self, dest_label):
        self.line_buffer = self.line_buffer.strip()
        v = self.line_buffer[:1]
        if v.isalpha():
            self.expression_stack.insert(0, ord(v.upper()) - ord('A'))
            self.line_buffer = self.line_buffer[1:]
        else:
            self.fail_test(dest_label)

    #
    # IL flow control instructions
    #

    def il_icall(self, dest_label):
        self.control_stack.insert(0, self.pc)
        self.pc = self.il_labels[dest_label]


    def il_ijmp(self, dest_label):
        self.pc = self.il_labels[dest_label]


    def il_rtn(self):
        self.pc = self.control_stack.pop(0)

    #
    # BASIC flow control instructions
    #

    def il_cmpr(self):
        operand2 = self.expression_stack.pop(0)
        operator = self.expression_stack.pop(0)
        operand1 = self.expression_stack.pop(0)
        if operator == 0:
            cmpr = operand1 == operand2
        elif operator == 1:
            cmpr = operand1 < operand2
        elif operator == 2:
            cmpr = operand1 <= operand2
        elif operator == 3:
            cmpr = operand1 != operand2
        elif operator == 4:
            cmpr = operand1 > operand2
        elif operator == 5:
            cmpr = operand1 >= operand2
        else:
            raise Exception
        if not cmpr:
            self.il_nxt()
    

    def il_for(self):
        """Used only in TBX."""
        next_line = self.basic_linenum
        while self.basic_program[next_line].strip() == '':
            next_line += 1
        self.expression_stack.insert(0, next_line)
    

    def il_fornext(self):
        """Used only in TBX."""
        var = self.expression_stack.pop(0)
        end_cond = self.expression_stack.pop(0)
        for_body = self.expression_stack.pop(0)
        if self.basic_var_data[var] < end_cond:
            self.basic_linenum = for_body
            self.expression_stack.insert(0, for_body)
            self.expression_stack.insert(0, end_cond)
        self.expression_stack.insert(0, var)
        self.expression_stack.insert(0, self.basic_var_data[var] + 1)


    def il_fin(self):
        self.basic_linenum = 0
        self.pc = self.il_labels['CO']


    def il_insrt(self):
        self.line_buffer = self.line_buffer.strip()
        line_num = ''
        while self.line_buffer[:1].isdigit():
            line_num += self.line_buffer[:1]
            self.line_buffer = self.line_buffer[1:]
        self.basic_program[int(line_num)] = self.line_buffer.strip()
        self.line_buffer = ''


    def il_nxt(self):
        if self.basic_linenum == 0:
            self.pc = self.il_labels['CO']
        else:
            while (self.basic_linenum < self.max_lines
                   and self.basic_program[self.basic_linenum].strip() == ''):
                self.basic_linenum += 1
            if self.basic_linenum == self.max_lines:
                self.basic_linenum = 0
                self.pc = self.il_labels['CO']
            else:
                self.line_buffer = self.basic_program[self.basic_linenum]
                self.basic_linenum += 1
                self.pc = self.il_labels['XEC']


    def il_nxtx(self):
        """Used only in TBX."""
        self.pc = self.il_labels['XEC']


    def il_xfer(self):
        loc = self.expression_stack.pop(0)

        if 1 <= loc < self.max_lines:
            if self.basic_program[loc] != '':
                self.basic_linenum = loc
                self.il_nxt()
            else:
                print('Invalid line number.')
                self.pc = self.il_labels['ERRENT']
        else:
            print('Invalid line number.')
            self.pc = self.il_labels['ERRENT']

    #
    # BASIC variable & stack instructions
    #

    def il_ind(self):
        i = self.expression_stack.pop(0)
        self.expression_stack.insert(0, self.basic_var_data[i])


    def il_lit(self, val):
        self.expression_stack.insert(0, int(val))


    def il_rstr(self):
        self.basic_linenum = self.subroutine_stack.pop(0)


    def il_sav(self):
        self.subroutine_stack.insert(0, self.basic_linenum)


    def il_store(self):
        value = self.expression_stack.pop(0)
        var_index = self.expression_stack.pop(0)
        self.basic_var_data[var_index] = value

    #
    # Arithmetic instructions
    #

    def il_add(self):
        operand2 = self.expression_stack.pop(0)
        operand1 = self.expression_stack.pop(0)
        self.expression_stack.insert(0, operand1 + operand2)


    def il_div(self):
        operand2 = self.expression_stack.pop(0)
        operand1 = self.expression_stack.pop(0)
        self.expression_stack.insert(0, operand1 // operand2)


    def il_mpy(self):
        operand2 = self.expression_stack.pop(0)
        operand1 = self.expression_stack.pop(0)
        self.expression_stack.insert(0, operand1 * operand2)


    def il_neg(self):
        operand = self.expression_stack.pop(0)
        self.expression_stack.insert(0, 0 - operand)
    

    def il_random(self):
        """Used only in TBX."""
        self.expression_stack.insert(0, random.randint(0, 10000))


    def il_sub(self):
        operand2 = self.expression_stack.pop(0)
        operand1 = self.expression_stack.pop(0)
        self.expression_stack.insert(0, operand1 - operand2)
    
    #
    # TBX array instructions
    #

    def il_array1(self):
        """Used only in TBX."""
        offset = self.expression_stack.pop(0)
        idx = self.basic_var_data[self.expression_stack.pop(0)]
        self.expression_stack.insert(0, idx + offset)


    def il_array2(self):
        """Used only in TBX."""
        y = self.expression_stack.pop(0)
        x = self.expression_stack.pop(0)
        v = self.expression_stack.pop(0)
        base_idx = self.basic_var_data[v]
        width = self.basic_array_widths[v]
        idx = base_idx + (y * width) + x
        self.expression_stack.insert(0, idx)


    def il_dim1(self):
        """Used only in TBX."""
        size = self.expression_stack.pop(0) + 1
        var = self.expression_stack.pop(0)
        idx = len(self.basic_var_data)
        self.basic_var_data[var] = idx
        self.basic_var_data += [0 for _ in range(size)]


    def il_dim2(self):
        """Used only in TBX."""
        y_size = self.expression_stack.pop(0) + 1
        x_size = self.expression_stack.pop(0) + 1
        var = self.expression_stack.pop(0)
        idx = len(self.basic_var_data)
        self.basic_var_data[var] = idx
        self.basic_var_data += [0 for _ in range(y_size * x_size)]
        self.basic_array_widths[var] = x_size

    #
    # Terminal I/O instructions
    #

    def il_getln(self):
        if len(self.line_buffer_buffer) > 0:
            self.line_buffer = self.line_buffer_buffer.pop(0)
            print(f'{self.command_prompt}{self.line_buffer}', end='')
        else:
            self.line_buffer = ''
            try:
                while len(self.line_buffer) < 1:
                    self.line_buffer = input(self.command_prompt)
            except EOFError:
                self.user_quit = True


    def il_innum(self):
        while len(self.innum_buffer) == 0:
            try:
                user_input = input(self.input_prompt)
                self.innum_buffer = [int(n) for n in user_input.split(',')]
            except ValueError:
                print('Type a number.')
            except EOFError:
                self.user_quit = True
                return
        self.expression_stack.insert(0, self.innum_buffer.pop(0))


    def il_nline(self):
        print()


    def il_prn(self):
        n = self.expression_stack.pop(0)
        print(n, end='')


    def il_prs(self):
        pr_str, _, tail = self.line_buffer.partition('"')
        print(pr_str, end='')
        self.line_buffer = tail


    def il_spc(self):
        print('\t', end='')


    def il_spcone(self):
        """Used only in TBX."""
        print(' ', end='')


    def il_tab(self):
        """Used only in TBX."""
        for _ in range(self.expression_stack.pop(0)):
            print(' ', end='')
        self.control_stack[2] += 1  # Skip printing the "result"
    
    #
    # Program listing commands
    #    

    def il_list0(self):
        """Used only in TBX."""
        self.listing_range = [n for n in range(self.max_lines)]
    

    def il_list1(self):
        """Used only in TBX."""
        n = self.expression_stack.pop(0)
        if 1 <= n < self.max_lines:
            self.listing_range = [n]
        else:
            self.il_err('7')
    

    def il_list2(self):
        """Used only in TBX."""
        m = self.expression_stack.pop(0)
        n = self.expression_stack.pop(0)
        if (1 <= n < self.max_lines) and (1 <= m < self.max_lines):
            self.listing_range = [i for i in range(n, m + 1)]
        else:
            self.il_err('7')


    def il_lst(self):
        for linenum in self.listing_range:
            line = self.basic_program[linenum].strip()
            if line != '':
                print(f'{linenum:>3} {line}')
    

    def il_size(self):
        """Used only in TBX."""
        lines = [0 for line in self.basic_program if line.strip() != '']
        print(f'The program currently has {len(lines)} lines.')
        print('I know that\'s not what you asked, but there it is!')

    #
    # Misc instructions
    #

    def il_err(self, code):
        """Used only in TBX."""
        if code == '1':
            print('Line too long.')
        elif code == '2':
            print('Numeric overflow.')
        elif code == '3':
            print('Illegal character.')
        elif code == '4':
            print('Unclosed quote.')
        elif code == '5':
            print('Expression too complex.')
        elif code == '6':
            print('Illegal expression.')
        elif code == '7':
            print('Invalid line number.')
        elif code == '8':
            print('Division by zero.')
        elif code == '9':
            print('Subroutines nested too deep.')
        elif code == '10':
            print('RET without GOSUB.')
        elif code == '11':
            print('Illegal variable.')
        elif code == '12':
            print('Bad command or statement name.')
        elif code == '13':
            print('Unmatched parentheses.')
        elif code == '14':
            print('OOM')
        else:
            raise Exception
        self.pc = self.il_labels['ERRENT']

    def il_init(self):
        self.line_buffer = ''
        self.innum_buffer = []
        self.basic_program = ['' for _ in range(self.max_lines)]
        self.basic_var_data = [0 for _ in range(26)]

        self.expression_stack = []
        self.control_stack = []
        self.subroutine_stack = []


    def il_xinit(self):
        self.innum_buffer = []

        # If line buffer is empty, 'RUN' command was issued
        if len(self.line_buffer.strip()) < 1:
            self.expression_stack = []
            self.control_stack = []
            self.subroutine_stack = []
            self.basic_linenum = 1
            self.il_nxt()

    #########################################################################$

    def fail_test(self, dest_label):
        if self.pc - 1 == self.il_labels[dest_label]:
            print(f'Syntax error at line {self.basic_linenum - 1}.')
            self.pc = self.il_labels['ERRENT']
        else:
            self.pc = self.il_labels[dest_label]


    def start(self):
        print()
        print(self.greeting)
        print()
        print('Press ^C to break and ^D to quit.')
        while not self.user_quit:
            try:
                op = self.il_program[self.pc][0]
                args = self.il_program[self.pc][1:]
                self.pc += 1
                self.il_ops[op](*args)
            except KeyboardInterrupt:
                self.pc = self.il_labels['ERRENT']
                self.basic_linenum = 0


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Tiny BASIC in Python')
    parser.add_argument('-x', '--extended', action='store_true', default=False,
                        help='use Tiny BASIC Extended (TBX)')
    parser.add_argument('-f', '--file', default=None,
                        help='a BASIC program to load on start')
    args = parser.parse_args()

    autoload = []
    if args.file is not None:
        with open(args.file) as f:
            autoload = list(f.readlines())

    if args.extended:
        kwargs = {
            'il_code': 'tbx.il',
            'max_lines': 2**16,
            'greeting': '''Tiny BASIC Extended (TBX)

As published in Dr Dobb's Journal of Computer Calisthenics
    and Orthodontia, Vol.1, Nos.1-2 (1976).''',
            'command_prompt': ': ',
            'input_prompt': '? ',
            'enable_multistatement': True,
            'autoload': autoload
        }
    else:
        kwargs = {
            'il_code': 'tinybasic.il',
            'max_lines': 2**8,
            'greeting': '''Tiny BASIC

As published in Dr Dobb's Journal of Computer Calisthenics
    and Orthodontia, Vol.1, No.1 (1976).''',
            'command_prompt': '? ',
            'input_prompt': '# ',
            'enable_multistatement': False,
            'autoload': autoload
        }

    tb = TinyBasicInterpreter(**kwargs)
    tb.start()
