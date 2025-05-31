import os
from db import criar_conexao
from datetime import date
import bcrypt

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')

def cadastrar_lojista():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    try:
        cursor = conn.cursor()
        limpar_tela()
        print("\n--- Cadastrar Novo Lojista / Funcionário ---")

        name = input("Nome completo do funcionário: ").strip()
        if not name:
            print("O nome não pode ser vazio.")
            return

        email = input("E-mail (usado para login, deve ser único): ").strip()
        if not email:
            print("O e-mail não pode ser vazio.")
            return
        cursor.execute("SELECT employee_id FROM employee WHERE LOWER(email) = LOWER(%s);", (email,))
        if cursor.fetchone():
            print("Já existe um funcionário cadastrado com este e-mail.")
            return

        password = input("Senha: ").strip()
        if not password:
            print("A senha não pode ser vazia.")
            return
        hashed_password = criotpgrafar(password)

        cpf = input("CPF, sem a utilização de (.) e (-): ").strip()
        if cpf:
            cursor.execute("SELECT employee_id FROM employee WHERE cpf = %s;", (cpf,))
            if cursor.fetchone():
                print("Já existe um funcionário cadastrado com este CPF.")
                return
        else:
            cpf = None

        phone = input("Telefone (opcional): ").strip()
        if not phone:
            phone = None

        address = input("Endereço (opcional): ").strip()
        if not address:
            address = None

        while True:
            hire_date_str = input("Data de contratação (AAAA-MM-DD): ").strip()
            try:
                hire_date = date.fromisoformat(hire_date_str)
                break
            except ValueError:
                print("Formato de data inválido. Use AAAA-MM-DD.")
        
        role = input("Cargo (ex: Lojista, Vendedor, Administrador): ").strip()
        if not role:
            print("O cargo não pode ser vazio.")
            return
        
        is_active = True

        cursor.execute(
            """
            INSERT INTO employee (name, email, password_hash, cpf, phone, address, hire_date, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING employee_id;
            """,
            (name, email, hashed_password, cpf, phone, address, hire_date, role, is_active)
        )
        employee_id = cursor.fetchone()[0]

        conn.commit()
        print(f"Funcionário '{name}' (ID: {employee_id}) cadastrado com sucesso como {role}!")

    except Exception as e:
        print(f"Erro ao cadastrar funcionário: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
        input("Pressione Enter para continuar...")

def mostrar_funcionarios_adm():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    try:
        cursor = conn.cursor()
        limpar_tela()
        print("\n--- Funcionários Cadastrados ---")

        cursor.execute("""
            SELECT
                employee_id,
                name,
                email,
                cpf,
                phone,
                address,
                hire_date,
                role,
                is_active
            FROM
                employee
            ORDER BY
                name;
        """)
        funcionarios = cursor.fetchall()

        if not funcionarios:
            print("Nenhum funcionário cadastrado no momento.")
        else:
            print(f"{'ID':<5} {'Nome':<30} {'E-mail':<30} {'CPF':<15} {'Telefone':<15} {'Cargo':<20} {'Contratação':<15} {'Ativo':<8}")
            print("-" * 140)
            for func in funcionarios:
                employee_id, name, email, cpf, phone, address, hire_date, role, is_active = func
                cpf_str = cpf if cpf else "N/A"
                phone_str = phone if phone else "N/A"
                active_str = "Sim" if is_active else "Não"
                hire_date_str = hire_date.strftime('%Y-%m-%d') if hire_date else "N/A"
                print(f"{employee_id:<5} {name:<30} {email:<30} {cpf_str:<15} {phone_str:<15} {role:<20} {hire_date_str:<15} {active_str:<8}")

    except Exception as e:
        print(f"Erro ao buscar funcionários: {e}")
    finally:
        if conn:
            conn.close()
        input("\nPressione Enter para continuar...")

def remover_funcionario():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    try:
        cursor = conn.cursor()
        limpar_tela()
        print("\n--- Remover Funcionário ---")

        cursor.execute("SELECT employee_id, name, email, role, is_active FROM employee ORDER BY name;")
        funcionarios = cursor.fetchall()

        if not funcionarios:
            print("Nenhum funcionário cadastrado para remover.")
            input("Pressione Enter para continuar...")
            return

        print(f"{'ID':<5} {'Nome':<30} {'E-mail':<30} {'Cargo':<20} {'Ativo':<8}")
        print("-" * 100)
        for func in funcionarios:
            employee_id, name, email, role, is_active = func
            active_str = "Sim" if is_active else "Não"
            print(f"{employee_id:<5} {name:<30} {email:<30} {role:<20} {active_str:<8}")

        print("\n")
        id_remover_input = input("Digite o ID do funcionário a remover ou ENTER para cancelar: ").strip()

        if not id_remover_input:
            print("Operação cancelada.")
            input("Pressione Enter para continuar...")
            return

        try:
            id_remover = int(id_remover_input)
        except ValueError:
            print("ID inválido. Digite um número inteiro.")
            input("Pressione Enter para continuar...")
            return

        cursor.execute("SELECT name FROM employee WHERE employee_id = %s;", (id_remover,))
        funcionario_existente = cursor.fetchone()

        if not funcionario_existente:
            print(f"Funcionário com ID {id_remover} não encontrado.")
            input("Pressione Enter para continuar...")
            return

        nome_funcionario = funcionario_existente[0]
        confirm = input(f"Tem certeza que deseja remover o funcionário '{nome_funcionario}' (ID: {id_remover})? (s/n): ").strip().lower()

        if confirm != 's':
            print("Remoção cancelada.")
            input("Pressione Enter para continuar...")
            return

        cursor.execute("DELETE FROM employee WHERE employee_id = %s;", (id_remover,))
        conn.commit()
        print(f"Funcionário '{nome_funcionario}' (ID: {id_remover}) removido com sucesso.")

    except Exception as e:
        print(f"Erro ao remover funcionário: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
        input("Pressione Enter para continuar...")

def editar_funcionario():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    try:
        cursor = conn.cursor()
        limpar_tela()
        print("\n--- Editar Funcionário ---")

        cursor.execute("SELECT employee_id, name, email, role, is_active FROM employee ORDER BY name;")
        funcionarios = cursor.fetchall()

        if not funcionarios:
            print("Nenhum funcionário cadastrado para editar.")
            input("Pressione Enter para continuar...")
            return

        print(f"{'ID':<5} {'Nome':<30} {'E-mail':<30} {'Cargo':<20} {'Ativo':<8}")
        print("-" * 100)
        for func in funcionarios:
            employee_id, name, email, role, is_active = func
            active_str = "Sim" if is_active else "Não"
            print(f"{employee_id:<5} {name:<30} {email:<30} {role:<20} {active_str:<8}")

        print("\n")
        id_editar_input = input("Digite o ID do funcionário a editar ou ENTER para cancelar: ").strip()

        if not id_editar_input:
            print("Operação cancelada.")
            input("Pressione Enter para continuar...")
            return

        try:
            id_editar = int(id_editar_input)
        except ValueError:
            print("ID inválido. Digite um número inteiro.")
            input("Pressione Enter para continuar...")
            return

        cursor.execute("SELECT name, email, cpf, phone, address, hire_date, role, is_active FROM employee WHERE employee_id = %s;", (id_editar,))
        funcionario_existente = cursor.fetchone()

        if not funcionario_existente:
            print(f"Funcionário com ID {id_editar} não encontrado.")
            input("Pressione Enter para continuar...")
            return

        nome_atual, email_atual, cpf_atual, phone_atual, address_atual, hire_date_actual, role_actual, is_active_actual = funcionario_existente

        print(f"\nEditando funcionário: {nome_atual} (ID: {id_editar})")
        print("Deixe em branco para manter o valor atual.")

        novo_nome = input(f"Novo nome ({nome_atual}): ").strip()
        if not novo_nome:
            novo_nome = nome_atual

        novo_email = input(f"Novo e-mail ({email_atual}): ").strip()
        if not novo_email:
            novo_email = email_atual
        else:
            cursor.execute("SELECT employee_id FROM employee WHERE LOWER(email) = LOWER(%s) AND employee_id != %s;", (novo_email, id_editar))
            if cursor.fetchone():
                print("Este e-mail já está em uso por outro funcionário. Edição cancelada.")
                input("Pressione Enter para continuar...")
                return

        novo_cpf = input(f"Novo CPF ({cpf_atual if cpf_atual else 'N/A'}): ").strip()
        if not novo_cpf:
            novo_cpf = cpf_atual
        else:
            cursor.execute("SELECT employee_id FROM employee WHERE cpf = %s AND employee_id != %s;", (novo_cpf, id_editar))
            if cursor.fetchone():
                print("Este CPF já está em uso por outro funcionário. Edição cancelada.")
                input("Pressione Enter para continuar...")
                return

        novo_phone = input(f"Novo telefone ({phone_atual if phone_atual else 'N/A'}): ").strip()
        if not novo_phone:
            novo_phone = phone_atual

        novo_address = input(f"Novo endereço ({address_atual if address_atual else 'N/A'}): ").strip()
        if not novo_address:
            novo_address = address_atual

        nova_data_contratacao_str = input(f"Nova data de contratação (AAAA-MM-DD) ({hire_date_actual.strftime('%Y-%m-%d')}): ").strip()
        nova_data_contratacao = hire_date_actual
        if nova_data_contratacao_str:
            try:
                nova_data_contratacao = date.fromisoformat(nova_data_contratacao_str)
            except ValueError:
                print("Formato de data inválido. Mantendo a data atual.")

        novo_cargo = input(f"Novo cargo ({role_actual}): ").strip()
        if not novo_cargo:
            novo_cargo = role_actual

        novo_status_input = input(f"Funcionário ativo? (s/n) ({'s' if is_active_actual else 'n'}): ").strip().lower()
        novo_status = is_active_actual
        if novo_status_input == 's':
            novo_status = True
        elif novo_status_input == 'n':
            novo_status = False

        cursor.execute(
            """
            UPDATE employee SET
                name = %s,
                email = %s,
                cpf = %s,
                phone = %s,
                address = %s,
                hire_date = %s,
                role = %s,
                is_active = %s
            WHERE employee_id = %s;
            """,
            (novo_nome, novo_email, novo_cpf, novo_phone, novo_address,
             nova_data_contratacao, novo_cargo, novo_status, id_editar)
        )
        conn.commit()
        print(f"Funcionário '{novo_nome}' (ID: {id_editar}) atualizado com sucesso.")

    except Exception as e:
        print(f"Erro ao editar funcionário: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
        input("Pressione Enter para continuar...")

def menu_employee():
    while True:
        limpar_tela()
        print("\n--- Menu do Administrador ---")
        print("1. Cadastrar Lojista/Funcionário")
        print("2. Mostrar Funcionários Cadastrados")
        print("3. Editar Funcionário")
        print("4. Remover Funcionário")
        print("0. Voltar ao Menu Principal")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            cadastrar_lojista()
        elif opcao == '2':
            mostrar_funcionarios_adm()
        elif opcao == '3':
            editar_funcionario()
        elif opcao == '4':
            remover_funcionario()
        elif opcao == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")
            input("Pressione Enter para continuar...")

def criotpgrafar(password):
   password_bytes = password.encode('utf-8')
   salt = bcrypt.gensalt()
   hashed = bcrypt.hashpw(password_bytes, salt)
   return hashed

def checar_password(password, hashed):
   password_bytes = password.encode('utf-8')
   return bcrypt.checkpw(password_bytes, hashed)