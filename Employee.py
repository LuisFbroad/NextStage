import os
import time
from db import criar_conexao
import bcrypt

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
        password = input("Senha: ").strip()

        if not email or not password:
            print("E-mail e senha não podem ser vazios.")
            input("Pressione Enter para continuar...")
            return None, None

        cursor.execute("SELECT employee_id, password_hash, role, is_active FROM employee WHERE LOWER(email) = LOWER(%s);", (email,))
        resultado = cursor.fetchone()

        if resultado:
            employee_id, hashed_password_db, role, is_active = resultado

            if not is_active:
                print("Sua conta de funcionário está inativa. Entre em contato com o administrador.")
                input("Pressione Enter para continuar...")
                return None, None

            if bcrypt.checkpw(password.encode('utf-8'), bytes(hashed_password_db)):
                print(f"Login bem-sucedido! Bem-vindo(a), {email}.")
                input("Pressione Enter para continuar...")
                return employee_id, role
            else:
                print("E-mail ou senha inválidos.")
        else:
            print("E-mail ou senha inválidos.")

    except Exception as e:
        print(f"Erro durante o login: {e}")
    finally:
        if conn:
            conn.close()
        input("Pressione Enter para continuar...")
    
    return None, None