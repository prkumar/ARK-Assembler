import collections
import math

FORMATS = {}

REGISTERS = {
    "$accumulator": 0b000,
    "$at": 0b001,
    "$t0": 0b010,
    "$t1": 0b011,
    "$s0": 0b100,
    "$s1": 0b101,
    "$s2": 0b110,
    "$s3": 0b111
}

Registers = collections.namedtuple(
    "Registers",
    field_names="start end bits"
)

Immediate = collections.namedtuple(
    "Immediate",
    field_names="bits signed"
)

DontCare = collections.namedtuple(
    "DontCare",
    field_names="bits"
)


def register(start=0, end=len(REGISTERS) - 1):
    assert(
        start >= 0 and
        end < len(REGISTERS) and
        (end > start) and
        (end - start + 1) % 2 == 0
    )
    return Registers(start, end, math.log(end - start + 1, 2))


def immediate(bits, signed=True):
    assert(bits > 0)
    return Immediate(bits, signed)


def dontcare(bits):
    assert(bits > 0)
    return DontCare(bits)


class OpcodeBit(object):

    def __init__(self, key, instruction=None):
        self.parent = None
        self.key = key
        self.instruction = instruction
        self.children = {"0": None, "1": None}

    def add_child(self, key):
        assert(key in ["0", "1"])
        if self.children[key] is not None:
                if self.children[key].instruction is not None:
                    raise Exception(
                        "Opcode {} preserved for instruction: {}".format(
                            str(self.children[key]), self.instruction
                        ))
        else:
            self.children[key] = OpcodeBit(key)
        self.children[key].parent = self

    def __getitem__(self, item):
        return self.children[item]

    def __str__(self):
        if self.parent is None:
            return self.key
        else:
            return str(self.parent) + self.key

    def inorder_traversal(self):
        if self.children["0"] is not None:
            self.children["0"].inorder_traversal()
        if self.instruction is not None:
            print(self.instruction + ": " + str(self))
        if self.children["1"] is not None:
            self.children["1"].inorder_traversal()


class Format(collections.MutableMapping):
    INSTRUCTION_BITS = 9
    ROOT_NODE = OpcodeBit("")

    def __init__(self, name, *operands):
        self.instructions = {}
        operand_bits = sum((o.bits for o in operands))
        self.operands = operands
        self.opcode_length = self.INSTRUCTION_BITS - operand_bits
        assert (self.opcode_length >= 0)
        FORMATS[name] = self

    def operand(self, index):
        return self.operands[index]

    def __setitem__(self, name, opcode):
        if name in self.instructions:
            raise ValueError("Instruction `{}` already exists!".format(name))
        assert(len(opcode) == self.opcode_length)
        node = Format.ROOT_NODE
        for bit in opcode:
            node.add_child(bit)
            node = node[bit]
        node.instruction = name
        self.instructions[name] = opcode

    def __getitem__(self, key):
        return self.instructions[key]

    def __delitem__(self, key):
        del self.instructions[key]

    def __len__(self):
        return len(self.instructions)

    def __iter__(self):
        return iter(self.instructions)


# -- Formats -- #
# Add a parser function for each format here
# TODO: Can we define the parser functions here instead?

A = Format("A", register(4, 7))
R = Format("R", register(0, 7))
K = Format("K", register(0, 7), register(0, 7))
AA = Format("AA", register(4, 7), register(4, 7))
RR = Format("RR", immediate(4, signed=False))
KK = Format("KK", immediate(7))
SPC = Format("SPC", dontcare(3))

# -- Instructions -- #

A.update({
    "load": "1000000",
    "store": "1000001",
    "parallel_comp": "0000000",
    "addo": "0000010",
    "is_zero": "0000011"
})


R.update({
    "copy": "100010",
    "paste": "100011",
    "inc": "100100",
    "dec": "100101",
    "clear": "100110",
    "sub": "100111",
    "shiftl": "101000",
    "shiftr": "101001",
    "shifto": "101010"
})

K.update({
    "add": "001"
})

AA.update({
    "str_match": "10111"
})

RR.update({
    "high": "11000",
    "low": "11001"
})

KK.update({
    "boz": "01"
})

SPC.update({
    "halt": "000110",
    "TBD": "000111"
})

