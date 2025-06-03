from db import criar_conexao
import os

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')

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
                # --- CORREÇÃO 1 AQUI ---
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
                # --- CORREÇÃO 2 AQUI ---
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