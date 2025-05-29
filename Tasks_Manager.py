import os
from db import criar_conexao
from datetime import date
import bcrypt

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')

def adicionar_jogo():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    try:
        cursor = conn.cursor()
        limpar_tela()
        print("\n--- Catálogo Atual de Jogos ---")
        cursor.execute("""
            SELECT g.game_name, g.genre, g.price, COALESCE(s.quantity_available, 0)
            FROM games g
            LEFT JOIN stock s ON g.game_id = s.game_id
            ORDER BY g.game_name;
        """)
        jogos = cursor.fetchall()
        
        if jogos:
            for idx, (nome, genero, preco, estoque) in enumerate(jogos, start=1):
                preco_str = f"R$ {preco:.2f}" if preco is not None else "N/A"
                print(f"{idx}. {nome} | Gênero: {genero} | Preço: {preco_str} | Estoque: {estoque}")
        else:
            print("Nenhum jogo cadastrado no momento.")

        print("\n--- Adicionar Novo Jogo ao Catálogo ---")

        nome = input("Nome do jogo: ").strip()
        if not nome:
            print("O nome do jogo não pode ser vazio.")
            input("Pressione Enter para continuar...")
            return

        cursor.execute("SELECT game_id FROM games WHERE LOWER(game_name) = LOWER(%s);", (nome,))
        if cursor.fetchone():
            print("Já existe um jogo com esse nome no catálogo.")
            input("Pressione Enter para continuar...")
            return

        descricao = input("Descrição do jogo (pressione ENTER para deixar em branco): ").strip()
        if not descricao:
            descricao = None

        genre = input("Gênero do jogo: ").strip()
        if not genre:
            print("O gênero do jogo não pode ser vazio.")
            input("Pressione Enter para continuar...")
            return

        classificacao = input("Classificação indicativa: ").strip()
        if not classificacao:
            print("A classificação indicativa não pode ser vazia.")
            input("Pressione Enter para continuar...")
            return

        while True:
            preco_input = input("Preço do jogo: ").strip()
            try:
                preco = float(preco_input)
                if preco < 0:
                    print("O preço não pode ser negativo.")
                    continue
                break
            except ValueError:
                print("Preço inválido. Digite um número válido.")

        try:
            estoque_inicial = int(input("Quantidade inicial em estoque: "))
            if estoque_inicial < 0:
                print("A quantidade não pode ser negativa.")
                input("Pressione Enter para continuar...")
                return
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")
            input("Pressione Enter para continuar...")
            return

        cursor.execute(
            """
            INSERT INTO games (game_name, description, genre, indicative_classification, price)
            VALUES (%s, %s, %s, %s, %s) RETURNING game_id;
            """,
            (nome, descricao, genre, classificacao, preco)
        )
        game_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO stock (game_id, quantity_available) VALUES (%s, %s);",
            (game_id, estoque_inicial)
        )

        conn.commit()
        print(f"Jogo '{nome}' adicionado com sucesso com {estoque_inicial} unidades em estoque e preço R$ {preco:.2f}.")

    except Exception as e:
        print(f"Erro ao adicionar jogo: {e}")
    finally:
        if conn:
            conn.close()
        input("Pressione Enter para continuar...")

def apagar_jogo():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    try:
        cursor = conn.cursor()
        limpar_tela()
        print("\n--- Catálogo Atual de Jogos ---")
        cursor.execute("""
            SELECT g.game_id, g.game_name, COALESCE(s.quantity_available, 0)
            FROM games g
            LEFT JOIN stock s ON g.game_id = s.game_id
            ORDER BY g.game_name;
        """)
        jogos = cursor.fetchall()

        if not jogos:
            print("Nenhum jogo cadastrado no momento.")
            input("Pressione Enter para continuar...")
            return

        for idx, (game_id, nome, estoque) in enumerate(jogos, start=1):
            print(f"{idx}. {nome} | Estoque: {estoque}")

        escolha_input = input("\nDigite o número do jogo que deseja apagar ou ENTER para cancelar: ").strip()
        if not escolha_input:
            print("Operação cancelada.")
            input("Pressione Enter para continuar...")
            return

        try:
            escolha_idx = int(escolha_input) - 1
            if 0 <= escolha_idx < len(jogos):
                game_id_selecionado = jogos[escolha_idx][0]
                nome_selecionado = jogos[escolha_idx][1]

                confirm = input(f"Tem certeza que deseja apagar o jogo '{nome_selecionado}'? (s/n): ").strip().lower()
                if confirm != 's':
                    print("Operação cancelada.")
                    input("Pressione Enter para continuar...")
                    return

                cursor.execute("DELETE FROM stock WHERE game_id = %s;", (game_id_selecionado,))
                cursor.execute("DELETE FROM games WHERE game_id = %s;", (game_id_selecionado,))

                conn.commit()
                print(f"Jogo '{nome_selecionado}' apagado com sucesso.")
            else:
                print("Escolha inválida.")
        except ValueError:
            print("Entrada inválida. Digite um número válido.")

        input("Pressione Enter para continuar...")

    except Exception as e:
        print(f"Erro ao apagar jogo: {e}")
        input("Pressione Enter para continuar...")
    finally:
        if conn:
            conn.close()

def atualizar_estoque():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    try:
        cursor = conn.cursor()
        limpar_tela()
        print("\n--- Atualizar Estoque ---")
        cursor.execute("""
            SELECT g.game_id, g.game_name, s.quantity_available
            FROM games g
            JOIN stock s ON g.game_id = s.game_id
            ORDER BY g.game_name;
        """)
        jogos_estoque = cursor.fetchall()

        if not jogos_estoque:
            print("Nenhum jogo com estoque para atualizar.")
            input("Pressione Enter para continuar...")
            return

        for idx, (game_id, nome, quantidade) in enumerate(jogos_estoque, start=1):
            print(f"{idx}. Jogo: {nome} | Estoque Atual: {quantidade}")

        escolha_input = input("\nDigite o número do jogo para atualizar o estoque ou aperte ENTER para sair: ").strip()

        if not escolha_input:
            print("Saindo da atualização de estoque.")
            input("Pressione Enter para continuar...")
            return

        try:
            escolha_idx = int(escolha_input) - 1
            if 0 <= escolha_idx < len(jogos_estoque):
                game_id_selecionado = jogos_estoque[escolha_idx][0]
                nome_selecionado = jogos_estoque[escolha_idx][1]
                quantidade_atual = jogos_estoque[escolha_idx][2]

                quantidade_adicional = int(input(f"Digite a quantidade a adicionar ao estoque de '{nome_selecionado}': "))
                nova_quantidade = quantidade_atual + quantidade_adicional

                cursor.execute("UPDATE stock SET quantity_available = %s WHERE game_id = %s;", (nova_quantidade, game_id_selecionado))
                conn.commit()
                print(f"Estoque de '{nome_selecionado}' atualizado para {nova_quantidade} unidades (adicionado {quantidade_adicional}).")
            else:
                print("Escolha inválida. O número do jogo não existe.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número válido.")

        input("Pressione Enter para continuar...")

    except Exception as e:
        print(f"Erro ao atualizar estoque: {e}")
        input("Pressione Enter para continuar...")
    finally:
        if conn:
            conn.close()

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
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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