import os
import time
from db import criar_conexao
import bcrypt
import maskpass
from Task_employee.employee_venda import *
from Task_employee.employee_games import *

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')

def login_funcionario():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return None, None

    try:
        cursor = conn.cursor()
        limpar_tela()
        print("\n--- Login de Funcionário ---")

        email = input("E-mail: ").strip()
        password = maskpass.askpass(prompt="Digite sua senha: ", mask="#")

        if not email or not password:
            print("E-mail e senha não podem ser vazios.")
            input("Pressione Enter para continuar...")
            return None, None

        cursor.execute(
            "SELECT employee_id, password_hash, role, is_active FROM employee WHERE LOWER(email) = LOWER(%s);",
            (email,)
        )
        resultado = cursor.fetchone()

        if resultado:
            employee_id, hashed_password_db, role, is_active = resultado

            if not is_active:
                print("Sua conta está inativa. Contate o administrador.")
                input("Pressione Enter para continuar...")
                return None, None

            if bcrypt.checkpw(password.encode('utf-8'), bytes(hashed_password_db)):
                print(f"Login bem-sucedido! Bem-vindo(a), {email}.")
                input("Pressione Enter para continuar...")
                return employee_id, role
            else:
                print("Senha incorreta.")
        else:
            print("Funcionário não encontrado.")

    except Exception as e:
        print(f"Erro durante o login: {e}")


    return None, None

def employee_menu(employee_id):
    while True:
        limpar_tela()
        print("\n--- Menu Funcionário ---")
        print("1 --- Vender Jogo")
        print("2 --- Buscar Jogo")
        print("3 --- Olhar Estoque")
        print("0 --- Sair do Sistema")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            employee_venda(employee_id)
        elif opcao == "2":
            buscar_jogo()
        elif opcao == "3":
            visualizar_estoque()
        elif opcao == "0":
            print("\nSaindo do sistema...")
            break
        else:
            print("\nOpção inválida. Tente novamente.")
            input("Pressione Enter para continuar...")