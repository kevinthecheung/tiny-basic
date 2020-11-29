"""Tiny BASIC IL interpreter.

This file contains an interpreter for the Tiny BASIC interpretive language
(IL), as described in Dr Dobb's Journal, Vol.1, No.1 (Jan 1976). The IL, in
turn, is used to implement Tiny BASIC, a limited subset of BASIC intended to
run on low-memory (2-4K) machines. See `tinybasic.il` for the BASIC interpreter
written in IL.

Run this file with the `-f` option to load a BASIC program on startup.
"""
import re


class TinyBasicInterpreter:

    def __init__(self, il_code='tinybasic.il', max_lines=256, autoload=[]):
        self.pc = 0
        self.il_program = []
        self.il_labels = {}

        self.line_buffer = ''
        self.line_buffer_buffer = autoload
        self.max_lines = max_lines
        self.basic_linenum = 0
        self.basic_program = ['' for _ in range(max_lines)]
        self.basic_var_data = [0 for _ in range(26)]

        self.expression_stack = []
        self.control_stack = []
        self.subroutine_stack = []

        self.user_quit = False

        with open(il_code, 'r') as f:
            self.load_interpreter(f.readlines())

        self.il_ops = {}
        self.il_ops['ADD'] = self.il_add
        self.il_ops['CMPR'] = self.il_cmpr
        self.il_ops['DIV'] = self.il_div
        self.il_ops['DONE'] = self.il_done
        self.il_ops['FIN'] = self.il_fin
        self.il_ops['GETLN'] = self.il_getln
        self.il_ops['HOP'] = self.il_ijmp
        self.il_ops['ICALL'] = self.il_icall
        self.il_ops['IJMP'] = self.il_ijmp
        self.il_ops['IND'] = self.il_ind
        self.il_ops['INIT'] = self.il_init
        self.il_ops['INNUM'] = self.il_innum
        self.il_ops['INSRT'] = self.il_insrt
        self.il_ops['LIT'] = self.il_lit
        self.il_ops['LST'] = self.il_lst
        self.il_ops['MPY'] = self.il_mpy
        self.il_ops['NEG'] = self.il_neg
        self.il_ops['NXT'] = self.il_nxt
        self.il_ops['NLINE'] = self.il_nline
        self.il_ops['PRN'] = self.il_prn
        self.il_ops['PRS'] = self.il_prs
        self.il_ops['RSTR'] = self.il_rstr
        self.il_ops['RTN'] = self.il_rtn
        self.il_ops['SAV'] = self.il_sav
        self.il_ops['SPC'] = self.il_spc
        self.il_ops['STORE'] = self.il_store
        self.il_ops['SUB'] = self.il_sub
        self.il_ops['TST'] = self.il_tst
        self.il_ops['TSTL'] = self.il_tstl
        self.il_ops['TSTN'] = self.il_tstn
        self.il_ops['TSTV'] = self.il_tstv
        self.il_ops['XINIT'] = self.il_xinit
        self.il_ops['XFER'] = self.il_xfer


    def load_interpreter(self, lines):
        for ln in lines:
            match = re.fullmatch(r'\s*(?P<label>\w+:)?\s*(?P<statement>[^;]*)(?P<comment>;.*)?\s*', ln)
            label = match.group('label')
            statement = match.group('statement').strip()
            comment = match.group('comment')
            if statement != '':
                stm = statement.split()
                if stm[0] == 'DB':
                    db_arg = stm[1]
                    db_arg = ',' if db_arg == "','" else db_arg.replace(',', '').replace("'", '')  # TODO: sketchy
                    self.il_program[-1].append(db_arg)
                else:
                    self.il_program.append(stm)
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
        if self.line_buffer.strip() != '':
            print(f'Syntax error at line {self.basic_linenum}.')
            self.pc = self.il_labels['ERRENT']


    def il_tst(self, dest_label, test_str):
        self.line_buffer = self.line_buffer.strip()
        if self.line_buffer.upper().startswith(test_str):
            self.line_buffer = self.line_buffer[len(test_str):]
        else:
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


    def il_nxt(self):
        if self.basic_linenum == 0:
            self.pc = self.il_labels['CO']
        else:
            self.line_buffer = self.basic_program[self.basic_linenum]
            self.basic_linenum += 1
            while (self.basic_linenum < self.max_lines
                   and self.basic_program[self.basic_linenum].strip() == ''):
                self.basic_linenum += 1
            if self.basic_linenum == self.max_lines:
                self.basic_linenum = 0
            self.pc = self.il_labels['XEC']


    def il_xfer(self):
        loc = self.expression_stack.pop(0)

        # Special case for 'RUN' command: find first line
        if loc == 1:
            while self.basic_program[loc] == '':
                loc += 1

        if 1 <= loc < self.max_lines:
            if self.basic_program[loc] != '':
                self.basic_linenum = loc
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


    def il_sub(self):
        operand2 = self.expression_stack.pop(0)
        operand1 = self.expression_stack.pop(0)
        self.expression_stack.insert(0, operand1 - operand2)

    #
    # Terminal I/O instructions
    #

    def il_getln(self):
        if len(self.line_buffer_buffer) > 0:
            self.line_buffer = self.line_buffer_buffer.pop(0)
            print(f'? {self.line_buffer}', end='')
        else:
            try:
                self.line_buffer = input('? ')
            except EOFError:
                self.user_quit = True


    def il_innum(self):
        n = None
        while n is None:
            try:
                n = int(input('# '))
            except ValueError:
                print('Type a number.')
            except EOFError:
                self.user_quit = True
                return
        self.expression_stack.insert(0, n)


    def il_lst(self):
        for linenum, line in enumerate(self.basic_program):
            if line.strip() != '':
                print(f'{linenum:>3} {line}')


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

    #
    # Init instructions
    #

    def il_init(self):
        self.line_buffer = ''
        self.basic_program = ['' for _ in range(self.max_lines)]
        self.basic_var_data = [0 for _ in range(26)]

        self.expression_stack = []
        self.control_stack = []
        self.subroutine_stack = []


    def il_xinit(self):
        self.expression_stack = []

    #########################################################################$

    def fail_test(self, dest_label):
        if self.pc - 1 == self.il_labels[dest_label]:
            print(f'Syntax error at line {self.basic_linenum}.')
            self.pc = self.il_labels['ERRENT']
        else:
            self.pc = self.il_labels[dest_label]


    def start(self):
        print('\nTiny BASIC')
        print('As published in Dr Dobb\'s Journal, Vol.1, No.1 (Jan 1976).\n')
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

    parser = argparse.ArgumentParser(description='Tiny BASIC')
    parser.add_argument('-f', '--file', default=None,
                        help='BASIC program to load')
    args = parser.parse_args()

    autoload = []
    if args.file is not None:
        with open(args.file) as f:
            autoload = list(f.readlines())
    tb = TinyBasicInterpreter(autoload=autoload)
    tb.start()
