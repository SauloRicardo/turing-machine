import pyparsing as pp
from src.block import Block
from src.utils import Utils


class Parser(object):

    def __init__(self):
        self.__blocks = dict()
        self.__this_block = None

        comment = pp.Literal(";") - pp.restOfLine
        comment.setDefaultWhitespaceChars(" \t")
        comment.callDuringTry = True

        NL = pp.Suppress(pp.LineEnd())
        NL.setDefaultWhitespaceChars(" \t")
        NL.callDuringTry = True

        identifier = pp.Word(pp.alphas+"_", pp.alphanums+"_")
        identifier.setDefaultWhitespaceChars(" \t")
        identifier.callDuringTry = True

        this_state = pp.Word(pp.nums, max=4)
        this_state.setDefaultWhitespaceChars(" \t")
        this_state.callDuringTry = True

        new_state = (pp.Word(pp.nums, max=4) ^ pp.Literal("retorne") ^ pp.Literal("pare") ^ pp.Literal("*"))
        new_state.setDefaultWhitespaceChars(" \t")
        new_state.callDuringTry = True

        this_symbol = (pp.Word(pp.printables) ^ pp.Literal("_") ^ pp.Literal("*"))
        this_symbol.setDefaultWhitespaceChars(" \t")
        this_symbol.callDuringTry = True

        new_symbol = (pp.Word(pp.printables) ^ pp.Literal("_") ^ pp.Literal("*"))
        new_symbol.setDefaultWhitespaceChars(" \t")
        new_symbol.callDuringTry = True

        move = pp.Word("edi")
        move.setDefaultWhitespaceChars(" \t")
        move.callDuringTry = True

        NLO = pp.ZeroOrMore(NL, stopOn=this_state ^ "fim" ^ "bloco")
        NLO.setDefaultWhitespaceChars(" \t")
        NLO.callDuringTry = True

        transition = pp.Group(NLO - this_state - this_symbol - "--" - new_symbol - move - new_state - pp.Optional("!")
                              - NL)
        transition.setParseAction(self.__insert_transition)
        transition.setDefaultWhitespaceChars(" \t")
        transition.callDuringTry = True

        call_block = pp.Group(NLO - this_state - identifier - new_state - pp.Optional("!") - NL)
        call_block.setParseAction(self.__insert_call_block)
        call_block.setDefaultWhitespaceChars(" \t")
        call_block.callDuringTry = True

        create_block = pp.Group(NLO - "bloco" - identifier - this_state - NL)
        create_block.setDefaultWhitespaceChars(" \t")
        create_block.callDuringTry = True
        create_block.setParseAction(self.__create_new_block)

        block_end = pp.Group(NLO - pp.Literal("fim") - NLO)
        block_end.setDefaultWhitespaceChars(" \t")
        block_end.callDuringTry = True

        codes = pp.OneOrMore(pp.Or(transition ^ call_block), stopOn=block_end)
        codes.setDefaultWhitespaceChars(" \t")
        codes.callDuringTry = True

        block = create_block - codes - block_end
        block.setDefaultWhitespaceChars(" \t")
        block.callDuringTry = True

        self.__prog = pp.OneOrMore(block, stopOn=pp.StringEnd())
        self.__prog.setDefaultWhitespaceChars(" \t")
        self.__prog.ignore(comment)
        self.__prog.callDuringTry = True

    def __create_new_block(self, toks):
        new_block = Block(toks[0][1], int(toks[0][2]))
        self.__blocks[toks[0][1]] = new_block
        self.__this_block = new_block

    def __insert_transition(self, toks):
        value = (int(toks[0][0]))

        if toks[0][5].isdigit():
            if len(toks[0]) == 7:
                compute = (toks[0][1], toks[0][3], toks[0][4], int(toks[0][5]), True)
            else:
                compute = (toks[0][1], toks[0][3], toks[0][4], int(toks[0][5]), False)
        else:
            if len(toks[0]) == 7:
                compute = (toks[0][1], toks[0][3], toks[0][4], toks[0][5], True)
            else:
                compute = (toks[0][1], toks[0][3], toks[0][4], toks[0][5], False)

        if value not in self.__this_block.commands:
            self.__this_block.commands[value] = [compute]
        else:
            if compute not in self.__this_block.commands[value]:
                self.__this_block.commands[value].append(compute)

    def __insert_call_block(self, toks):
        value = (int(toks[0][0]))

        if toks[0][2].isdigit():
            if len(toks[0]) == 4:
                compute = (toks[0][1], int(toks[0][2]), True)
            else:
                compute = (toks[0][1], int(toks[0][2]), False)
        else:
            if len(toks[0]) == 4:
                compute = (toks[0][1], toks[0][2], True)
            else:
                compute = (toks[0][1], toks[0][2], False)

        if value not in self.__this_block.commands:
            self.__this_block.commands[value] = [compute]
        else:
            if compute not in self.__this_block.commands[value]:
                self.__this_block.commands[value].append(compute)

    def parse_file(self, file):
        try:
            self.__prog.parseFile(file)

            if "main" not in self.__blocks:
                raise Exception(Utils.Colors.FAIL + "Not exists main block" + Utils.Colors.ENDC)
            else:
                return self.__blocks
        except pp.ParseSyntaxException as err:
            print(Utils.Colors.FAIL + err.line.strip() + Utils.Colors.ENDC)
            error = str(err)
            pos = error.find("(line:")
            raise Exception(Utils.Colors.FAIL + "Error in "+error[pos:]+" -- File syntax error" + Utils.Colors.ENDC)
