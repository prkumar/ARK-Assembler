"""
ARK Assembler

TODO: Move parser and lexer into classes.
"""
import ark
import os
import sys
import ply.lex as lex
import ply.yacc as yacc

FILE_OUT = sys.stdout
tokens = ('COMMAND', 'REGISTER', 'IMMEDIATE')

t_COMMAND = '[a-zA-Z_][a-zA-Z0-9_]*'
t_REGISTER = r'\$\w+'


def assemble(opcode, *operands):
    """Write machine code to output file."""
    return "{}_{}".format(opcode, "".join(operands))

def t_IMMEDIATE(t):
    r'(0b(0|1)+|0x([0-9]|[A-F])|-?\d+)'
    if t.value.startswith("0b"):
        # Binary
        t.value = int(t.value[2:], 2)
    elif t.value.startswith("0x"):
        # Hex
        t.value = int(t.value[2:], 16)
    else:
        # Decimal
        t.value = int(t.value)
    return t

# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    raise Exception("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lex.lex()


def get_register_bits(bounds, register):
    if not (bounds.start <= ark.REGISTERS[register] <= bounds.end):
        raise Exception("Register {} is out of bounds for this instruction.".format(register))
    before = '{0:b}'.format(ark.REGISTERS[register] - bounds.start)
    return ("0" * (int(bounds.bits) - len(before))) + before


def find_opcode(instruction, *formats):
    for f in formats:
        try:
            format_ = ark.FORMATS[f]
            return format_[instruction], format_
        except KeyError:
            continue

    raise KeyError(
        "'{}' is not a valid instruction of this ISA.".format(instruction)
    )


def p_instruction_reg(p):
    'instruction : COMMAND REGISTER'

    opcode, format_ = find_opcode(p[1], "A", "R")
    bounds = format_.operand(0)
    register_bits = get_register_bits(bounds, p[2])
    p[0] = assemble(opcode, register_bits)


def p_instruction_reg_reg(p):
    'instruction : COMMAND REGISTER REGISTER'
    opcode, format_ = find_opcode(p[1], "K", "AA")
    register_bits1 = get_register_bits(format_.operand(0), p[2])
    register_bits2 = get_register_bits(format_.operand(1), p[3])
    p[0] = assemble(opcode, register_bits1, register_bits2)


def p_instruction_imm(p):
    'instruction : COMMAND IMMEDIATE'
    opcode, format_ = find_opcode(p[1], "RR", "KK")
    imm_bounds = format_.operand(0)
    if imm_bounds.signed:
        bounds = (-(2**(imm_bounds.bits - 1)), 2**(imm_bounds.bits - 1))
    else:
        bounds = (0, 2**imm_bounds.bits)

    if not (bounds[0] <= p[2] <= bounds[1]):
        print(
            "Warning at {}: number exceeds bounds of {}-bit{}"
            "immediate: [{}, {}): overflow bits will be ignored.".format(
                " ".join(map(str, p)),
                imm_bounds.bits,
                " signed " if imm_bounds.signed else " ",
                bounds[0],
                bounds[1],
            )
        )

    imm_code = bin(p[2] & ((2 ** imm_bounds.bits) - 1))[2:]
    imm_buffer = "0" if p[2] >= 0 else "1"
    imm_code = imm_buffer * (imm_bounds.bits - len(imm_code)) + imm_code
    p[0] = assemble(opcode, imm_code)


def p_instruction_spc(p):
    'instruction : COMMAND'
    opcode, _ = find_opcode(p[1], "SPC")
    p[0] = assemble(opcode, "111")


def p_error(p):
    raise Exception("Syntax error at '%s'" % p.value)

yacc.yacc()


if __name__ == "__main__":

    if len(sys.argv) <= 1:
        print("Starting the ARK interpreter... (Enter CTR + C to exit)")
        while True:
            try:
                s = raw_input('>>> ')
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            else:
                try:
                    if s:
                        print(yacc.parse(s))
                except Exception as e:
                    print("Error: " + str(e))
        exit(0)

    try:
        lines = []
        print("Reading instructions from '{}' ...".format(os.path.relpath(sys.argv[1]))),
        with open(sys.argv[1], "r") as stream:
            try:
                for i, line in enumerate(stream):
                    lines.append(yacc.parse(line) + " // " + line.rstrip())
            except Exception as e:
                raise Exception("Parser error at line {}: {}".format(i + 1, e))
        print("Done!")
        if len(sys.argv) > 2:
            print("Writing machine code output to '{}' ...".format(os.path.relpath(sys.argv[2]))),
            with open(sys.argv[2], "w") as fout:
                fout.write(os.linesep.join(lines))
            print("Done!")
        else:
            print("Machine Code:")
            print(os.linesep.join(lines))
    except Exception as e:
        print("\nFatal Error: " + str(e))

