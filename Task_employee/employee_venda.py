import os
from db import criar_conexao
from datetime import date
from decimal import Decimal
import traceback

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')

def calcular_total_carrinho(carrinho):
    total = Decimal('0.0')
    for item in carrinho.values():
        total += item['quantidade'] * item['preco_unitario']
    return total

def employee_venda(employee_id_logado):
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    carrinho = {}

    try:
        cursor = conn.cursor()

        while True:
            limpar_tela()
            print("\n--- Terminal de Vendas ---")

            print("\n--- Catálogo de Jogos Disponíveis ---")
            cursor.execute("""
                SELECT g.game_id, g.game_name, g.genre, g.price, COALESCE(s.quantity_available, 0)
                FROM games g
                LEFT JOIN stock s ON g.game_id = s.game_id
                WHERE COALESCE(s.quantity_available, 0) > 0
                ORDER BY g.game_name;
            """)
            jogos_disponiveis = cursor.fetchall()
            if not jogos_disponiveis:
                print("Nenhum jogo disponível em estoque no momento.")
            else:
                print(f"{'ID':<5} {'Nome do Jogo':<30} {'Gênero':<15} {'Preço':<10} {'Estoque':<8}")
                print("-" * 75)
                for id_jogo, nome_jogo, genero, preco, estoque in jogos_disponiveis:
                    preco_str = f"R$ {preco:.2f}"
                    print(f"{id_jogo:<5} {nome_jogo:<30} {genero:<15} {preco_str:<10} {estoque:<8}")

            print("\n--- Carrinho de Compras ---")
            total_venda_atual = calcular_total_carrinho(carrinho)
            if not carrinho:
                print("O carrinho está vazio.")
            else:
                print(f"{'Nome do Jogo':<30} {'Qtde':<5} {'Preço Unit.':<15} {'Subtotal':<15}")
                print("-" * 65)
                for item in carrinho.values():
                    subtotal_item = item['quantidade'] * item['preco_unitario']
                    print(f"{item['nome']:<30} {item['quantidade']:<5} R$ {item['preco_unitario']:.2f}         R$ {subtotal_item:.2f}")
                print("-" * 65)
                print(f"{'TOTAL DA VENDA':<52} R$ {total_venda_atual:.2f}")

            print("\nOpções:\n1. Adicionar item\n2. Remover item\n3. Finalizar Venda\n0. Cancelar Venda")
            opcao = input("Digite sua opção: ").strip()

            if opcao == '1':
                try:
                    id_jogo_add = int(input("Digite o ID do jogo para adicionar: ").strip())
                    quantidade_add = int(input("Digite a quantidade: ").strip())
                    if quantidade_add <= 0:
                        print("A quantidade deve ser maior que zero.")
                        input("Pressione Enter para continuar...")
                        continue
                except ValueError:
                    print("Entrada inválida. Digite um número.")
                    input("Pressione Enter para continuar...")
                    continue
                
                cursor.execute("""
                    SELECT g.game_name, g.price, COALESCE(s.quantity_available, 0)
                    FROM games g LEFT JOIN stock s ON g.game_id = s.game_id
                    WHERE g.game_id = %s;
                """, (id_jogo_add,))
                resultado_jogo = cursor.fetchone()

                if resultado_jogo:
                    nome_jogo, preco_unitario, estoque_disponivel = resultado_jogo
                    quantidade_no_carrinho = carrinho.get(id_jogo_add, {}).get('quantidade', 0)

                    if (quantidade_no_carrinho + quantidade_add) > estoque_disponivel:
                        print(f"Estoque insuficiente! Disponível: {estoque_disponivel - quantidade_no_carrinho}.")
                    else:
                        if id_jogo_add in carrinho:
                            carrinho[id_jogo_add]['quantidade'] += quantidade_add
                        else:
                            carrinho[id_jogo_add] = {
                                'nome': nome_jogo,
                                'quantidade': quantidade_add,
                                'preco_unitario': preco_unitario
                            }
                        print(f"{quantidade_add}x '{nome_jogo}' adicionado(s) ao carrinho.")
                else:
                    print("ID do jogo não encontrado.")
                input("Pressione Enter para continuar...")

            elif opcao == '2':
                if not carrinho:
                    print("O carrinho está vazio.")
                    input("Pressione Enter para continuar...")
                    continue

                print("\nItens no Carrinho:")
                itens_listados = list(carrinho.keys())
                for i, game_id in enumerate(itens_listados, start=1):
                    item = carrinho[game_id]
                    print(f"{i}. {item['nome']} (Qtde: {item['quantidade']})")
                
                try:
                    escolha_remover_idx = int(input("Digite o número do item para remover: ").strip()) - 1
                    if 0 <= escolha_remover_idx < len(itens_listados):
                        game_id_remover = itens_listados[escolha_remover_idx]
                        item_a_remover = carrinho[game_id_remover]
                        qtde_max = item_a_remover['quantidade']
                        qtde_remover = int(input(f"Quantas unidades de '{item_a_remover['nome']}' remover (1-{qtde_max})? ").strip())

                        if 1 <= qtde_remover <= qtde_max:
                            if qtde_remover == qtde_max:
                                del carrinho[game_id_remover]
                                print("Item removido completamente.")
                            else:
                                carrinho[game_id_remover]['quantidade'] -= qtde_remover
                                print(f"{qtde_remover} unidade(s) removida(s).")
                        else:
                            print("Quantidade inválida.")
                    else:
                        print("Escolha inválida.")
                except ValueError:
                    print("Entrada inválida.")
                input("Pressione Enter para continuar...")

            elif opcao == '3':
                if not carrinho:
                    print("Carrinho vazio.")
                    input("Pressione Enter para continuar...")
                    continue

                cliente_id = None
                if input("Associar cliente existente? (s/n): ").strip().lower() == 's':
                    cpf_cliente = input("CPF do cliente (somente números): ").strip()
                    cursor.execute("SELECT customer_id FROM customer WHERE cpf = %s;", (cpf_cliente,))
                    cliente = cursor.fetchone()
                    if cliente:
                        cliente_id = cliente[0]
                        print("Cliente associado.")
                    else:
                        if input("Cadastrar novo cliente? (s/n): ").strip().lower() == 's':
                            nome = input("Nome: ").strip()
                            email = input("Email (opcional): ").strip() or None
                            telefone = input("Telefone (opcional): ").strip() or None
                            endereco = input("Endereço (opcional): ").strip() or None
                            cursor.execute("""
                                INSERT INTO customer (name, email, cpf, phone, address)
                                VALUES (%s, %s, %s, %s, %s)
                                RETURNING customer_id;
                            """, (nome, email, cpf_cliente, telefone, endereco))
                            cliente_id = cursor.fetchone()[0]
                            print("Cliente cadastrado e associado.")
                
                # Inputs removidos. Valores agora são fixos.
                metodo = "Pix"
                status = "Pago"

                total_final = calcular_total_carrinho(carrinho)

                cursor.execute("""
                    INSERT INTO sales (customer_id, employee_id, sale_date, total_value, payment_method, payment_status)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING sale_id;
                """, (cliente_id, employee_id_logado, date.today(), total_final, metodo, status))
                sale_id = cursor.fetchone()[0]

                for game_id, item in carrinho.items():
                    subtotal = item['quantidade'] * item['preco_unitario']
                    cursor.execute("""
                        INSERT INTO sales_items (sale_id, game_id, quantity, unit_price, subtotal)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (sale_id, game_id, item['quantidade'], item['preco_unitario'], subtotal))
                    
                    cursor.execute("""
                        UPDATE stock SET quantity_available = quantity_available - %s WHERE game_id = %s;
                    """, (item['quantidade'], game_id))
                
                conn.commit()
                print(f"\nVenda {sale_id} finalizada com sucesso!")
                print(f"Total: R$ {total_final:.2f}")
                print(f"Método: {metodo} | Status: {status}")
                input("Pressione Enter para continuar...")
                return

            elif opcao == '0':
                if input("Tem certeza que deseja cancelar a venda? (s/n): ").strip().lower() == 's':
                    print("Venda cancelada.")
                    input("Pressione Enter para continuar...")
                    return
            
            else:
                print("Opção inválida.")
                input("Pressione Enter para continuar...")

    except Exception:
        print("\nOcorreu um erro crítico. A operação será revertida.")
        traceback.print_exc()
        if conn:
            conn.rollback()
        input("Pressione Enter para continuar...")

    finally:
        if conn:
            conn.close()
            # print("Conexão com o banco de dados fechada.") # Removido para não poluir a tela