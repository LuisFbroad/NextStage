import os
from db import criar_conexao

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')

def atualizar_catalogo():
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    try:
        cursor = conn.cursor()

        limpar_tela()
        print("\n--- Catálogo Atual ---")
        cursor.execute("SELECT game_name, price FROM games ORDER BY game_name;")
        jogos = cursor.fetchall()
        if not jogos:
            print("Nenhum jogo encontrado no catálogo.")
        else:
            for idx, (nome, preco) in enumerate(jogos, start=1):
                print(f"{idx}. Nome: {nome} | Preço: R$ {preco:.2f}")

        escolha = input("\nDigite 'add' para adicionar ou 'del' para deletar um jogo do catálogo: ").strip().lower()

        if escolha == "add":
            print("\n--- Adicionar Novo Jogo ---")
            nome = input("Digite o nome do novo jogo: ")
            preco = float(input("Digite o preço do jogo: "))
            genero = input("Digite o gênero do jogo: ")
            indicative_classification = int(input("Digite a classificação indicativa (somente números): "))
            release_date = input("Digite a data de lançamento (AAAA-MM-DD): ")
            description = input("Digite uma breve descrição do jogo: ")

            author_enterprise_id = 1
            enterprise_id = 1

            cursor.execute("""
                INSERT INTO public.games (
                    author_enterprise_id, game_name, enterprise_id, genre,
                    indicative_classification, release_date, price, description
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (author_enterprise_id, nome, enterprise_id, genero,
                  indicative_classification, release_date, preco, description))
            conn.commit()
            print(f"Jogo '{nome}' adicionado com sucesso!")
            cursor.execute("INSERT INTO stock (game_id, quantity_available) VALUES ((SELECT game_id FROM games WHERE game_name = %s), 0);", (nome,))
            conn.commit()
            print(f"Jogo '{nome}' adicionado ao estoque com 0 unidades.")


        elif escolha == "del":
            print("\n--- Deletar Jogo ---")
            nome = input("Digite o nome do jogo que deseja remover: ").strip()

            cursor.execute("DELETE FROM stock WHERE game_id = (SELECT game_id FROM games WHERE LOWER(game_name) = %s);", (nome.lower(),))
            conn.commit()

            cursor.execute("DELETE FROM games WHERE LOWER(game_name) = %s;", (nome.lower(),))
            conn.commit()
            print(f"Jogo '{nome}' removido com sucesso!")

        else:
            print("Opção inválida.")

        input("Pressione Enter para continuar...")

    except Exception as e:
        print(f"Erro ao atualizar catálogo: {e}")
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
        cursor.execute("SELECT g.game_id, g.game_name, s.quantity_available FROM games g JOIN stock s ON g.game_id = s.game_id ORDER BY g.game_name;")
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
                nova_quantidade = int(input(f"Digite a nova quantidade para '{nome_selecionado}': "))

                cursor.execute("UPDATE stock SET quantity_available = %s WHERE game_id = %s;", (nova_quantidade, game_id_selecionado))
                conn.commit()
                print(f"Estoque de '{nome_selecionado}' atualizado para {nova_quantidade} unidades.")
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