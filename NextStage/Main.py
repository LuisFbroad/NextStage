## NextStageGames ##
import os
import time
from Gerente import ADM
from Gerente import menu_adm
from Cliente import cliente_main

def entrar_menu():
    print ("Cliente digite 1.\nADM digite 2.\nPara fechar o terminal 3.")
    escolha = int(input("Qual sua opção\n"))
    return escolha

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')

while True:
    limpar_tela()
    escolha = entrar_menu()
    ## Cliente
    if escolha == 1:
        limpar_tela()
        cliente_main()
    ## Gerente
    elif escolha == 2:
        limpar_tela()
        print("Entrendo em ADM")
        ADM()
        limpar_tela()
        menu_adm()
    elif escolha ==3:
        break
    else:
        limpar_tela()
        print("Opção invalida.\n\n")

## Implementar funcionario no futuro