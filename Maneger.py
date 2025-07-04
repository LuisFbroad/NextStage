from Tasks_ADM.Tasks_games_ADM import *
from Tasks_ADM.Task_employee_ADM import *
import os 
import maskpass

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')

def ADM():
    log_def = "ADM"
    senha_def = "Next"
    tentativas = 0

    log = input("Digite o Login.\n")
    while log != log_def:
        log = input("Login invalido tente novamente.\n")

    senha = maskpass.askpass(prompt="Digite sua senha.\n", mask="#")
    while senha != senha_def:
        tentativas += 1
        senha = maskpass.askpass(prompt="Digite sua senha.\n", mask="#")
        if tentativas >= 5:
            print("5 tentativas invalidas. Encerrando.")
            return False
    return True 

def menu_adm():
    while True:
        limpar_tela()
        print("\n--- Menu Administrador ---")
        print("1 --- Gerencia Joogs")
        print("2 --- Gerenciar Funcionarios")
        print("0 --- Fechar Sistema")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            menu_games()
        elif opcao == "2":
            menu_employee()
        elif opcao == "0":
            break
        else:
            print("Opção inválida. Tente novamente.")
            input("Pressione Enter para continuar...")