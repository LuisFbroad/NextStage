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
        print("1 --- Adicionar Catálogo")
        print("2 --- Apagar jogo do Catálogo")
        print("3 --- Alterar estoque")
        print("4 --- Cadastrar Lojista")
        print("5 --- Fechar sistema")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            adicionar_jogo()
        elif opcao == "2":
            apagar_jogo()
        elif opcao == "3":
            atualizar_estoque()
        elif opcao == "4":
            cadastrar_lojista()
        elif opcao == "5":
            print("Sistema encerrado.")
            break
        else:
            print("Opção inválida. Tente novamente.")
            input("Pressione Enter para continuar...")