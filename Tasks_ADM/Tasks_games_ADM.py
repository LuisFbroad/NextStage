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

        print("\n--- Adicionar Novo Jogo ---")

        nome = input("Nome do jogo..: ").strip()
        if not nome:
            print("O nome do jogo não pode ser vazio.")
            input("Pressione Enter para continuar...")
            return

        cursor.execute("SELECT game_id FROM games WHERE LOWER(game_name) = LOWER(%s);", (nome,))
        if cursor.fetchone():
            print("Já existe um jogo com esse nome no catálogo.")
            input("Pressione Enter para continuar...")
            return

        descricao = input("Descrição do jogo (pressione ENTER para deixar em branco)..: ").strip()
        if not descricao:
            descricao = None

        genre = input("Gênero do jogo..: ").strip()
        if not genre:
            print("O gênero do jogo não pode ser vazio.")
            input("Pressione Enter para continuar...")
            return

        classificacao = input("Classificação indicativa..: ").strip()
        if not classificacao:
            print("A classificação indicativa não pode ser vazia.")
            input("Pressione Enter para continuar...")
            return

        while True:
            preco_input = input("Preço do jogo..: ").strip()
            try:
                preco = float(preco_input)
                if preco < 0:
                    print("O preço não pode ser negativo.")
                    continue
                break
            except ValueError:
                print("Preço inválido. Digite um número válido.")

        try:
            estoque_inicial = int(input("Quantidade inicial em estoque..: "))
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

def buscar_jogo():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    try:
        cursor = conn.cursor()
        limpar_tela()
        print("\n--- Catálogo Atual de Jogos ---")

        sql_todos_jogos = """
            SELECT g.game_name, g.genre, g.price, COALESCE(s.quantity_available, 0) as quantity
            FROM games g
            LEFT JOIN stock s ON g.game_id = s.game_id
            ORDER BY g.game_name;
        """
        cursor.execute(sql_todos_jogos)
        catalogo_jogos = cursor.fetchall()

        if catalogo_jogos:
            print(f"{'Nome do Jogo':<40} {'Gênero':<20} {'Preço':<10} {'Estoque':<8}")
            print("-" * 80)
            for nome, genero, preco, estoque in catalogo_jogos:
                preco_str = f"R$ {preco:.2f}" if preco is not None else "N/A"
                genero_str = genero if genero is not None else "Não Definido"
                print(f"{nome:<40} {genero_str:<20} {preco_str:<10} {estoque:<8}")
        else:
            print("Nenhum jogo cadastrado no catálogo atualmente.")

        print("\n--- Buscar Jogo por Nome ---")
        nome_busca = input("Digite o nome do jogo para buscar (ou ENTER para voltar): ").strip()

        if not nome_busca:
            return

        sql_busca_por_nome = """
            SELECT g.game_name, g.genre, g.price, COALESCE(s.quantity_available, 0) as quantity
            FROM games g
            LEFT JOIN stock s ON g.game_id = s.game_id
            WHERE LOWER(g.game_name) LIKE LOWER(%s)
            ORDER BY g.game_name;
        """
        cursor.execute(sql_busca_por_nome, ('%' + nome_busca + '%',))
        resultados = cursor.fetchall()

        limpar_tela()
        print(f"\n--- Resultados da Busca por '{nome_busca}' ---")
        if resultados:
            print(f"{'Nome do Jogo':<40} {'Gênero':<20} {'Preço':<10} {'Estoque':<8}")
            print("-" * 80)
            for nome, genero, preco, estoque in resultados:
                preco_str = f"R$ {preco:.2f}" if preco is not None else "N/A"
                genero_str = genero if genero is not None else "Não Definido"
                print(f"{nome:<40} {genero_str:<20} {preco_str:<10} {estoque:<8}")
        else:
            print(f"Nenhum jogo encontrado com o nome '{nome_busca}'.")

    except Exception as e:
        print(f"Erro ao buscar jogo: {e}")
    finally:
        if conn:
            conn.close()
        input("\nPressione Enter para continuar...")

def visualizar_estoque():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    try:
        cursor = conn.cursor()
        limpar_tela()
        print("\n--- Estoque de Jogos ---")

        sql_estoque = """
            SELECT g.game_name, COALESCE(s.quantity_available, 0) as quantity
            FROM games g
            LEFT JOIN stock s ON g.game_id = s.game_id
            ORDER BY g.game_name;
        """
        cursor.execute(sql_estoque)
        estoque_jogos = cursor.fetchall()

        if estoque_jogos:
            print(f"{'Nome do Jogo':<40} {'Estoque':<10}")
            print("-" * 50)
            for nome, quantidade in estoque_jogos:
                print(f"{nome:<40} {quantidade:<10}")
        else:
            print("Nenhum jogo cadastrado ou sem informações de estoque.")
    except Exception as e:
        print(f"Erro ao consultar o estoque: {e}")
    finally:
        if conn:
            conn.close()
        input("\nPressione Enter para continuar...")

def menu_games():
    while True:
        limpar_tela()
        print("\n--- Menu de Gerenciamento de Jogos ---")
        print("1 --- Adicionar Novo Jogo")
        print("2 --- Apagar Jogo Existente")
        print("3 --- Atualizar Estoque de Jogo")
        print("4 --- Buscar Jogo")
        print("5 --- Visualizar Estoque")
        print("0 --- Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            adicionar_jogo()
        elif opcao == '2':
            apagar_jogo()
        elif opcao == '3':
            atualizar_estoque()
        elif opcao == '4':
            buscar_jogo()
        elif opcao == '5':
            visualizar_estoque()
        elif opcao == '0':
            print("Saindo do programa. Até mais!")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")
            input("Pressione Enter para continuar...")