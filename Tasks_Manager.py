import os
from db import criar_conexao

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
    print("Fazer dps")