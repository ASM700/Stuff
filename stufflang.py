import warnings
import time

code = """
!!S03Hey

!RS01A

!JS01A

/R=J<*!>


"""

acceptable = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"

class FutureWarning(Warning):
    pass

class DepricatedWarning(Warning):
    pass

class InvalidOpcodeError(Exception):
    pass

class InvalidArgsError(Exception):
    pass


class Variables:
    def __init__(self):
        self.svars = [[var, "u", None] for var in acceptable]
    def get_var(self, varname):
        for vargroup in self.svars:
            if vargroup[0] == varname:
                return vargroup
    def set_var(self, varname, vtype, value):
        ctr = 0
        for vargroup in self.svars:
            if vargroup[0] == varname:
                self.svars[ctr] = [varname, vtype, value]
            ctr += 1



class Input:
    def __init__(self):
        pass
    def feed(self, code):
        self.code = code
        self.off = 0
    def get(self, length):
        value = self.code[self.off:self.off+length]
        self.off += length
        return value
    def uninit(self):
        self.code = ""
        self.off = None
    def done(self):
        return len(self.code) <= self.off



class Parser:
    def __init__(self):
        pass
    def parse(self, code, rvars=Variables()):
        self.vars = rvars
        self.input = Input()
        self.input.feed(code)

        while not self.input.done():
            opcode = self.input.get(1)
            if opcode == "!":
                self.parseinit()
            elif opcode == "\"":
                self.parsecopy()
            elif opcode == "#":
                self.parseadd()
            elif opcode == "$":
                self.parsesub()
            elif opcode == "%":
                self.parsemul()
            elif opcode == "&":
                self.parsediv()
            elif opcode == "'":
                self.parseexp()
            elif opcode == "(":
                self.parsesti()
            elif opcode == ")":
                self.parseits()
            elif opcode == "*":
                self.parseprnt()
            elif opcode == "~":
                self.parsecom()
            elif opcode == "+":
                self.parsepntn()
            elif opcode == ",":
                self.parseuinp()
            elif opcode == "-":
                self.parsedel()
            elif opcode == ".":
                self.parseloop()
            elif opcode == "/":
                self.parseifst()
            elif opcode == " " or opcode == "\n" or opcode == "\n" or opcode == "\t":
                continue
            elif opcode in acceptable:
                warnings.warn("opcode '%s' not defined" % opcode, FutureWarning)
                print()
            else:
                raise InvalidOpcodeError("invalid opcode '%s' (must be inside of the 0x21 - 0x7E range)" % opcode)

    def parseinit(self):
        dest = self.input.get(1)
        dtype = self.input.get(1)
        if dtype == "S":
            length = int(self.input.get(2))
            data = self.input.get(length)
        elif dtype == "s":
            data = self.input.get(1)
        elif dtype == "N" or dtype == "n":
            length = int(self.input.get(1))
            data = int(self.input.get(length))
        elif dtype == "u":
            data = None
        elif dtype == "B":
            data = (self.input.get(1) == "t")
        else:
            raise InvalidArgsError("Invalid data type: '%s'" % dtype)

        self.vars.set_var(dest, dtype, data)
    def parsecopy(self):
        src = self.input.get(1)
        dest = self.input.get(1)
        src_type = self.vars.get_var(src)[1]
        src_data = self.vars.get_var(src)[2]
        self.vars.set_var(dest, src_type, src_data)
    def parseadd(self):
        src1 = self.input.get(1)
        src2 = self.input.get(1)
        src1_data = self.vars.get_var(src1)[2]
        src2_data = self.vars.get_var(src2)[2]
        self.vars.set_var(src1, "N", src1_data+src2_data)
    def parsesub(self):
        src1 = self.input.get(1)
        src2 = self.input.get(1)
        src1_data = self.vars.get_var(src1)[2]
        src2_data = self.vars.get_var(src2)[2]
        self.vars.set_var(src1, "N", src1_data-src2_data)
    def parsemul(self):
        src1 = self.input.get(1)
        src2 = self.input.get(1)
        src1_data = self.vars.get_var(src1)[2]
        src2_data = self.vars.get_var(src2)[2]
        self.vars.set_var(src1, "N", src1_data*src2_data)
    def parsediv(self):
        src1 = self.input.get(1)
        src2 = self.input.get(1)
        src1_data = self.vars.get_var(src1)[2]
        src2_data = self.vars.get_var(src2)[2]
        self.vars.set_var(src1, "N", src1_data/src2_data)
    def parseexp(self):
        src1 = self.input.get(1)
        src2 = self.input.get(1)
        src1_data = self.vars.get_var(src1)[2]
        src2_data = self.vars.get_var(src2)[2]
        self.vars.set_var(src1, "N", src1_data**src2_data)
    def parsesti(self):
        sd = self.vars.get_var(self.input.get(1))[2]
        integer = int(sd)
        self.vars.set_var(sd, "N", integer)
    def parseits(self):
        sd = self.vars.get_var(self.input.get(1))[2]
        string = str(sd)
        self.vars.set_var(sd, "S", string)
    def parseprnt(self):
        src = self.input.get(1)
        print(self.vars.get_var(src)[2])
    def parsecom(self):
        length = int(self.input.get(2))
        ignore = self.input.get(length)
    def parsepntn(self):
        src = self.input.get(1)
        print(self.vars.get_var(src)[2], end="")
    def parseuinp(self):
        dest = self.input.get(1)
        self.vars.set_var(dest, "S", input().strip())
    def parsedel(self):
        lenms = int(self.input.get(8))
        time.sleep(lenms/1000)
    def parseloop(self):
        depth = 0
        times = int(self.input.get(3))
        isdone = False
        start = self.input.off+1
        while not isdone:
            char = self.input.get(1)
            if char == ">":
                depth -= 1
            elif char == "<":
                depth += 1
                
            isdone = (depth == 0)
        end = self.input.off-1

        new = Parser() # Recursion!

        for x in range(times):
            new.parse(self.input.code[start:end], rvars=self.vars)
    def parseifst(self):
        c1 = self.vars.get_var(self.input.get(1))[2]
        sign = self.input.get(1)
        c2 = self.vars.get_var(self.input.get(1))[2]

        depth = 0
        isdone = False
        start = self.input.off+1
        while not isdone:
            char = self.input.get(1)
            if char == ">":
                depth -= 1
            elif char == "<":
                depth += 1

            isdone = (depth == 0)
        end = self.input.off-1

        new = Parser() # New parser to parse the code in <...>

        
        if (sign == "=" and c1 == c2) or (sign == ">" and c1 > c2) or \
           (sign == "<" and c1 < c2) or (sign == "g" and c1 >= c2) or \
           (sign == "l" and c1 <= c2) or (sign == "!" and c1 != c2):
            new.parse(self.input.code[start:end], rvars=self.vars)
                

parser = Parser()

parser.parse(code)
