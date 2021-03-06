# `ark`: the ARK Assembler

`ark` is an assembler for [ARK](https://github.com/prkumar/ARK-Processor), an instruction set architecture [we](#authors) developed at UCSD for CSE 141L and designed with the purpose of executing three specific problems (the `problems` directory contains the ARK instruction files for each problem).

**Note:** Currently, the assembler only generates machine code based on the ISA definition. We plan to implement a *true* assembler for ARK in the near future -- probably sometime after the quarter ends, as that would fall outside the scope of the course. 

**Note:** Moreover, I believe that we may be able to draw out a more general Python package for creating assemblers and/or defining ISAs from this :metal:.

## Usage

To run the assembler, type:
```
$ python -m ark
```

**Note:** The `-m` flags tells Python to execute `ark/__main__.py`, which contains the assembler code.

**Note:** Because of Python’s import mechanism, running the assembler from within the `ark` directory will not work.

The assembler has three modes, determined by the number of positional arguments given.

### Start a Read-eval-print loop (REPL)

When the assembler is run without arguments, it will start a REPL. In this mode, you  can "compile" ARK instructions to machine code, one instruction at a time.
  
```bash
$ python -m ark
Starting the ARK interpreter... (Enter CTR + C to exit) 
>>> shifto $accumulator
101010_000
>>>
``` 
  
### Read instructions from a file and print to standard out.

When the assembler is given a single argument, it reads instructions from the file at the given path and outputs the generated machine code directly to the screen.

```bash
$ python -m ark problems/problem17.txt
Reading instructions from 'problem17.txt'...
Machine Code:
11000_1111 // high        0b1111
11001_1111 // low         0b1111
100011_011 // paste       $t1
11000_0011 // high        0b0011
11001_0101 // low         0b0101
1000000_00 // load        $s0
...
``` 

### Read instructions from a file and write to another file.

When the assembler is given two arguments, it reads instructions from the first file and writes the generated machine code
to the second.

```bash
$ python -m ark problems/problem17.txt problem17_out.txt
Reading instructions from 'problem17.txt' ... Done!
Writing machine code output to 'problem17_out.txt' ... Done!
``` 

## Implementation

The assembler is built using David Beazley’s [Python implementation of lex and yacc](https://github.com/dabeaz/ply).

## Authors

Brought to you by:

* **A**nil Jethani
* P. **R**aj Kumar 
* **K**evin Wong

### An Aside

With a better understanding of ISA design tradeoffs now than when we were designing ARK (being that was back in early October '16), we consider it far from perfect and hope to make a few optimizations before completing the accompanying processor design.


