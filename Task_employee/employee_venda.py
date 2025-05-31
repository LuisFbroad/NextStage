import os
from db import criar_conexao
from datetime import date

def employee_venda(employee_id_logado):
    conn = criar_conexao()
    if conn is None:
        print("Erro ao conectar ao banco de dados.")
        input("Pressione Enter para continuar...")
        return

    carrinho = {}
    total_venda = 0.0

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
            if not carrinho:
                print("O carrinho está vazio.")
            else:
                print(f"{'Nome do Jogo':<30} {'Qtde':<5} {'Preço Unit.':<15} {'Subtotal':<15}")
                print("-" * 65)
                for game_id, item in carrinho.items():
                    subtotal_item = item['quantidade'] * item['preco_unitario']
                    print(f"{item['nome']:<30} {item['quantidade']:<5} R$ {item['preco_unitario']:.2f:<15} R$ {subtotal_item:.2f:<15}")
                print("-" * 65)
                print(f"{'TOTAL DA VENDA':<52} R$ {total_venda:.2f}")

            print("\nOpções:")
            print("1. Adicionar item ao carrinho")
            print("2. Remover item do carrinho")
            print("3. Finalizar Venda")
            print("0. Cancelar Venda e Voltar")

            opcao = input("Digite sua opção: ").strip()

            if opcao == '1':
                try:
                    id_jogo_add = int(input("Digite o ID do jogo para adicionar: ").strip())
                    quantidade_add = int(input("Digite a quantidade: ").strip())

                    if quantidade_add <= 0:
                        print("A quantidade deve ser maior que zero.")
                        input("Pressione Enter para continuar...")
                        continue

                    cursor.execute("""
                        SELECT g.game_name, g.price, COALESCE(s.quantity_available, 0)
                        FROM games g
                        LEFT JOIN stock s ON g.game_id = s.game_id
                        WHERE g.game_id = %s;
                    """, (id_jogo_add,))
                    resultado_jogo = cursor.fetchone()

                    if resultado_jogo:
                        nome_jogo, preco_unitario, estoque_disponivel = resultado_jogo

                        quantidade_no_carrinho = carrinho.get(id_jogo_add, {}).get('quantidade', 0)
                        
                        if (quantidade_no_carrinho + quantidade_add) > estoque_disponivel:
                            print(f"Estoque insuficiente! Disponível: {estoque_disponivel - quantidade_no_carrinho}. Você está tentando adicionar {quantidade_add}.")
                        else:
                            if id_jogo_add in carrinho:
                                carrinho[id_jogo_add]['quantidade'] += quantidade_add
                            else:
                                carrinho[id_jogo_add] = {
                                    'nome': nome_jogo,
                                    'quantidade': quantidade_add,
                                    'preco_unitario': preco_unitario
                                }
                            total_venda += (quantidade_add * preco_unitario)
                            print(f"{quantidade_add}x '{nome_jogo}' adicionado(s) ao carrinho.")
                    else:
                        print("ID do jogo não encontrado.")
                except ValueError:
                    print("Entrada inválida para ID ou quantidade.")
                input("Pressione Enter para continuar...")

            elif opcao == '2':
                if not carrinho:
                    print("O carrinho está vazio. Não há itens para remover.")
                    input("Pressione Enter para continuar...")
                    continue
                
                print("\nItens no Carrinho:")
                itens_listados = []
                for i, (game_id, item) in enumerate(carrinho.items(), start=1):
                    itens_listados.append(game_id)
                    print(f"{i}. {item['nome']} (Qtde: {item['quantidade']})")
                
                try:
                    escolha_remover_idx = int(input("Digite o número do item para remover do carrinho: ").strip()) - 1
                    if 0 <= escolha_remover_idx < len(itens_listados):
                        game_id_remover = itens_listados[escolha_remover_idx]
                        item_a_remover = carrinho[game_id_remover]

                        qtde_remover = int(input(f"Quantas unidades de '{item_a_remover['nome']}' deseja remover (atual: {item_a_remover['quantidade']})? ").strip())
                        
                        if qtde_remover <= 0:
                            print("A quantidade a remover deve ser maior que zero.")
                        elif qtde_remover >= item_a_remover['quantidade']:
                            total_venda -= (item_a_remover['quantidade'] * item_a_remover['preco_unitario'])
                            del carrinho[game_id_remover]
                            print(f"Todas as unidades de '{item_a_remover['nome']}' removidas do carrinho.")
                        else:
                            carrinho[game_id_remover]['quantidade'] -= qtde_remover
                            total_venda -= (qtde_remover * item_a_remover['preco_unitario'])
                            print(f"{qtde_remover}x '{item_a_remover['nome']}' removido(s) do carrinho.")
                    else:
                        print("Escolha inválida.")
                except ValueError:
                    print("Entrada inválida.")
                input("Pressione Enter para continuar...")

            elif opcao == '3':
                if not carrinho:
                    print("O carrinho está vazio. Não é possível finalizar a venda.")
                    input("Pressione Enter para continuar...")
                    continue

                print("\n--- Finalizar Venda ---")
                
                cliente_id = None
                opcao_cliente = input("Associar a um cliente existente? (s/n): ").strip().lower()
                if opcao_cliente == 's':
                    cpf_cliente = input("Digite o CPF do cliente (somente números): ").strip()
                    if cpf_cliente:
                        cursor.execute("SELECT customer_id FROM customer WHERE cpf = %s;", (cpf_cliente,))
                        cliente_existente = cursor.fetchone()
                        if cliente_existente:
                            cliente_id = cliente_existente[0]
                            print(f"Cliente encontrado e associado (ID: {cliente_id}).")
                        else:
                            print("Cliente não encontrado com este CPF.")
                            criar_novo = input("Deseja cadastrar um novo cliente? (s/n): ").strip().lower()
                            if criar_novo == 's':
                                print("\n--- Cadastrar Novo Cliente ---")
                                nome_cliente = input("Nome do cliente: ").strip()
                                email_cliente = input("E-mail do cliente (opcional): ").strip() or None
                                telefone_cliente = input("Telefone do cliente (opcional): ").strip() or None
                                endereco_cliente = input("Endereço do cliente (opcional): ").strip() or None

                                cursor.execute(
                                    """
                                    INSERT INTO customer (name, email, cpf, phone, address)
                                    VALUES (%s, %s, %s, %s, %s) RETURNING customer_id;
                                    """,
                                    (nome_cliente, email_cliente, cpf_cliente, telefone_cliente, endereco_cliente)
                                )
                                cliente_id = cursor.fetchone()[0]
                                conn.commit()
                                print(f"Novo cliente '{nome_cliente}' (ID: {cliente_id}) cadastrado e associado à venda.")
                            else:
                                print("Venda será registrada sem cliente associado.")
                else:
                    print("Venda será registrada sem cliente associado.")

                metodo_pagamento = input("Método de pagamento (Ex: Crédito, Débito, Dinheiro, Pix): ").strip()
                if not metodo_pagamento:
                    metodo_pagamento = "Não Informado"
                
                status_pagamento = input("Status do pagamento (Ex: Pago, Pendente): ").strip()
                if not status_pagamento:
                    status_pagamento = "Pago"
                
                cursor.execute(
                    """
                    INSERT INTO sales (customer_id, employee_id, sale_date, total_value, payment_method, payment_status)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING sale_id;
                    """,
                    (cliente_id, employee_id_logado, date.today(), total_venda, metodo_pagamento, status_pagamento)
                )
                sale_id = cursor.fetchone()[0]

                for game_id, item in carrinho.items():
                    subtotal_item = item['quantidade'] * item['preco_unitario']
                    cursor.execute(
                        """
                        INSERT INTO sales_items (sale_id, game_id, quantity, unit_price, subtotal)
                        VALUES (%s, %s, %s, %s, %s);
                        """,
                        (sale_id, game_id, item['quantidade'], item['preco_unitario'], subtotal_item)
                    )
                    
                    cursor.execute(
                        "UPDATE stock SET quantity_available = quantity_available - %s WHERE game_id = %s;",
                        (item['quantidade'], game_id)
                    )
                
                conn.commit()
                print(f"\nVenda {sale_id} finalizada com sucesso! Total: R$ {total_venda:.2f}")
                input("Pressione Enter para continuar...")
                return

            elif opcao == '0':
                confirm_cancel = input("Tem certeza que deseja cancelar a venda? (s/n): ").strip().lower()
                if confirm_cancel == 's':
                    print("Venda cancelada.")
                    input("Pressione Enter para continuar...")
                    return
                else:
                    print("Retornando à venda para continuar.")
                    input("Pressione Enter para continuar...")

            else:
                print("Opção inválida. Tente novamente.")
                input("Pressione Enter para continuar...")

    except Exception as e:
        print(f"Erro na operação de venda: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()