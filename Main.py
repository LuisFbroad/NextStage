import os
import time
from datetime import datetime
from Maneger import ADM
from Maneger import menu_adm
from Employee import login_funcionario
from Employee import employee_menu

def entrar_menu():
    while True:
        try:
            print("Vendedor digite 1.\nADM digite 2.\nPara fechar o terminal 3.")
            escolha = int(input("Qual sua opção\n"))
            return escolha
        except ValueError:
            print("Por favor, digite um número válido.")
            time.sleep(2)
            limpar_tela()

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')

while True:
    limpar_tela()
    escolha = entrar_menu()

    if escolha == 1:
        try:
            employee_id, role = login_funcionario()

            if employee_id is not None:
                employee_menu(employee_id)
        except Exception as e:
            erro_msg = f"Ocorreu um erro ao executar o cliente: {e}"
            time.sleep(2)

    elif escolha == 2:
        try:
            limpar_tela()
            print("Entrando em ADM")
            ADM()
            limpar_tela()
            menu_adm()
        except Exception as e:
            erro_msg = f"Ocorreu um erro ao executar o ADM: {e}"
            time.sleep(2)

    elif escolha == 3:
        print("Encerrando o programa...")
        time.sleep(1)
        break

    else:
        limpar_tela()
        print("Opção inválida.\n\n")
        time.sleep(2)