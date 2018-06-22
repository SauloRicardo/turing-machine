from parser import Parser
from utils import Utils


class Machine(object):
    def __init__(self, header="()"):
        self.__tape = ["_" for _ in range(500)]
        self.__code = None
        self.__state = -1
        self.__tape_index = 250
        self.__stack = []
        self.__complete_compute = False

        self.__parser = Parser()
        self.__header = [header[0], header[1]]
        self.__stop_breakpoint = False

    @property
    def keep_run(self):
        return not self.__complete_compute

    @property
    def breakpoint(self):
        return self.__stop_breakpoint

    @property
    def state(self):
        return self.__state

    @property
    def block(self):
        return self.__stack[-1][0].name

    @property
    def tape(self):
        return self.__tape

    @property
    def tape_index(self):
        return self.__tape_index

    @property
    def output(self):
        block_name_len = len(self.__stack[-1][0].name)
        block = "." * (16 - block_name_len)
        block += self.__stack[-1][0].name

        state_len = len(str(self.__state))
        state = "0" * (4 - state_len)
        state += str(self.__state)

        left_tape = "".join(self.__tape[self.__tape_index-20:self.__tape_index])
        header = self.__header[0] + self.__tape[self.__tape_index] + self.__header[1]
        right_tape = "".join(self.__tape[self.__tape_index+1:self.__tape_index+21])

        return block + "." + state + ": " + left_tape + header + right_tape

    def load_code(self, file_name):
        self.__code = self.__parser.parse_file(file_name)
        self.__state = self.__code["main"].initial_state
        self.__stack.append((self.__code["main"], -1))

    def load_word(self, word):
        self.__tape[self.__tape_index:len(word)] = word

    def __add_tape(self):
        if self.__tape_index == 50 or self.__tape_index == len(self.__tape)-50:
            for i in range(250):
                self.__tape.insert(0, '_')
                self.__tape_index += 1

            for i in range(250):
                self.__tape.append('_')

    def step(self):
        self.__add_tape()  # funcao para adicionar elementos em branco no inicio e fim da fita caso esteja acabando
        char_head = self.__tape[self.__tape_index]
        this_state = self.__state
        block = self.__stack[-1][0]
        self.__stop_breakpoint = False

        # caso a maquina nao acabou de executar faz
        if not self.__complete_compute:
            if this_state in block.commands:
                possible_transitions = block.commands[this_state]

                # código para colocar a transição com asterisco sempre no final
                transition_ok = []
                transition_with_asterisk = None
                for i in possible_transitions:
                    if i[0] == "*":
                        transition_with_asterisk = i
                    else:
                        transition_ok.append(i)

                if transition_with_asterisk is not None:
                    transition_ok.append(transition_with_asterisk)

                compute = False  # variavel para controle de se fez uma operacao ou nao

                for transition in transition_ok:  # itera sobre as transicoes
                    if transition[-1]:
                        self.__stop_breakpoint = True
                    else:
                        self.__stop_breakpoint = False

                    if transition[0] == char_head:  # se for o caractere q esta no cabecote
                        if transition[1] == "*":  # faz a escrita na fita
                            self.__tape[self.__tape_index] = self.__tape[self.__tape_index]
                        else:
                            self.__tape[self.__tape_index] = transition[1]

                        # move o cabecote
                        if transition[2] == "e":
                            self.__tape_index -= 1
                        elif transition[2] == "d":
                            self.__tape_index += 1

                        # troca o novo estado
                        if transition[3] == "*":
                            self.__state = self.__state
                        elif transition[3] == "pare":
                            self.__complete_compute = True
                        elif transition[3] == "retorne":
                            self.__state = self.__stack[-1][1]
                            self.__stack.pop()
                        else:
                            if transition[3] in block.commands:
                                self.__state = transition[3]
                            else:
                                transition_str = "%d %c -- %c %c %d" % (this_state, transition[0], transition[1],
                                                                        transition[2], transition[3])
                                message = Utils.Colors.FAIL + "In the '%s' block there is no state '%d' used in the " \
                                                              "transition '%s'" % (block.name, this_state,
                                                                                   transition_str) + Utils.Colors.ENDC
                                raise Exception(message)  # dispara uma excecao se o bloco nao tiver aquele estado

                        compute = True
                        break
                    elif transition[0] in self.__code:  # se for uma chamada de um bloco
                        if transition[0] in self.__code:
                            next_block = self.__code[transition[0]]
                            if next_block.initial_state in next_block.commands:
                                if transition[1] in block.commands or transition[1] == "pare" or \
                                        transition[1] == "retorne":
                                    # insere aquele bloco no topo da pilha junto com o estado de retorno
                                    self.__stack.append((next_block, transition[1]))
                                    self.__state = next_block.initial_state
                                    compute = True
                                    break
                                else:
                                    msg = Utils.Colors.FAIL + "Return state '%d' used in block '%s' does not exist " \
                                                              "in block '%s'" % (transition[1], transition[0],
                                                                                 block.name) + Utils.Colors.FAIL
                                    raise Exception(msg)
                            else:
                                msg = Utils.Colors.FAIL + "The initial state '%d' does not exist in the '%s' block" % (
                                    next_block.initial_state, next_block.name) + Utils.Colors.ENDC
                                raise Exception(msg)
                        else:
                            msg = Utils.Colors.FAIL + "Block '%s' does not exist" % (transition[0], ) + \
                                  Utils.Colors.ENDC
                            raise Exception(msg)
                    elif transition[0] == "*":  # caso a transicao for com o estado atual usando coringa
                        if transition[1] == "*":
                            self.__tape[self.__tape_index] = self.__tape[self.__tape_index]
                        else:
                            self.__tape[self.__tape_index] = transition[1]

                        if transition[2] == "e":
                            self.__tape_index -= 1
                        elif transition[2] == "d":
                            self.__tape_index += 1

                        if transition[3] == "*":
                            self.__state = self.__state
                        elif transition[3] == "pare":
                            self.__complete_compute = True
                        elif transition[3] == "retorne":
                            if self.__stack[-1][1] == "pare":
                                self.__complete_compute = True
                            else:
                                self.__state = self.__stack[-1][1]
                            self.__stack.pop()
                        else:
                            if transition[3] in block.commands:
                                self.__state = transition[3]
                            else:
                                transition_str = "%d %c -- %c %c %d" % (this_state, transition[0], transition[1],
                                                                        transition[2], transition[3])
                                message = Utils.Colors.FAIL + "In the '%s' block there is no state '%d' used in the " \
                                                              "transition '%s'" % (block.name, this_state,
                                                                                   transition_str) + Utils.Colors.ENDC
                                raise Exception(message)

                        compute = True
                        break
                if not compute:
                    message = Utils.Colors.FAIL + "There is no transition from state '%d' with the head in '%c'." % \
                              (this_state, char_head) + Utils.Colors.ENDC
                    raise Exception(message)
            else:
                raise Exception(Utils.Colors.FAIL + "State %s not exists" % (this_state, ) + Utils.Colors.ENDC)
