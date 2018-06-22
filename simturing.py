from machine import Machine
import argparse
import copy

if __name__ == '__main__':
    parser = argparse.ArgumentParser()  # cria parser dos argumentos
    # adiciona o comando -head nos argumentos como uma string e tenho valor padrao "()"
    parser.add_argument("-head", type=str, help="Tipo de caractere do cabeçote", default="()")

    # cria um grupo de argumentos que so pode existir um destes argumentos, sendo necessario um deles
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-resume", "-r", action="store_true", help="Executa o programa até o fim em modo silencioso e "
                                                                  "depois imprime o conteúdo final da fita.")
    group.add_argument("-verbose", "-v", action="store_true", help="Mostra a execução passo a passo do programa até "
                                                                   "o fim.")
    group.add_argument("-step", "-s", type=int, help="Mostra n computações passo a passo na tela, depois abre prompt e "
                                                     "aguarda nova opção (-r,-v,-s). Caso não seja fornecida nova opção"
                                                     " (entrada em branco), o padrão é repetir a última opção.",
                       default=None)
    parser.add_argument("name", type=str, help="Nome do arquivo fonte")  # adiciona o argumento nome do arquivo

    # faz o parse dos argumentos e faz uma copia deles para usar ela no programa
    args = parser.parse_args()
    options = copy.deepcopy(args)

    # cria uma maquina de turing com o argumento do cabeçote
    machine = Machine(args.head)
    print("")
    print("Simulador de Máquina de Turing ver 1.0")
    print("Desenvolvido como trabalho prático para a disciplina de Teoria da Computação")
    print("Arthur Teodoro e Saulo Ricardo, IFMG, 2018")
    print("")

    try:
        machine.load_code(args.name)

        word_input = input("Forneça a palavra inicial: ")
        print("")
        machine.load_word(word_input)

        if not options.resume:
            print(machine.output)

        while machine.keep_run:
            interaction_counter = 0

            while True:  # while true para simulador um do while que nao existe em python
                machine.step()
                interaction_counter += 1
                if not options.resume:
                    print(machine.output)

                if machine.breakpoint:
                    break
                elif interaction_counter == 500:
                    break
                elif options.step is not None and interaction_counter == (options.step-1):
                    break
                elif not machine.keep_run:
                    break

            if machine.keep_run:  # se ainda tem que computar, pede pro usuario as opcoes
                print("")
                option = input("Forneça uma opção (-r, -v, -s): ")
                if option == "-r" or option == "-resume":
                    options.resume = True
                    options.verbose = False
                    options.step = None
                elif option == "-v" or option == "-verbose":
                    options.resume = False
                    options.verbose = True
                    options.step = None
                elif option.strip().split(" ")[0] == "-s" or option.strip().split(" ")[0] == "-step":
                    options.resume = False
                    options.verbose = False
                    options.step = int(option.strip().split(" ")[1])+1
        if options.resume:
            print(machine.output)

    except Exception as err:
        print(err)
