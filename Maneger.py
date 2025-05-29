from Tasks_Manager import *
import os 

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

    senha = input("Digite sua Senha.\n")
    while senha != senha_def:
        tentativas += 1
        senha = input("Senha invalida tente novamente.\n")
        if tentativas >= 5:
            print("5 tentativas invalidas. Encerrando.")
            return False
    return True 

def menu_adm():
    while True:
        limpar_tela()
        print("\n--- Menu Administrador ---")
        print("1 --- Gerenciar Catálogo")
        print("2 --- Alterar estoque")
        print("3 --- Cadastrar Lojista")
        print("4 --- Fechar sistema")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            adicionar_jogo()
        elif opcao == "2":
            atualizar_estoque()
        elif opcao == "3":
            cadastrar_lojista()
        elif opcao == "4":
            print("Sistema encerrado.")
            break
        else:
            print("Opção inválida. Tente novamente.")
            input("Pressione Enter para continuar...")