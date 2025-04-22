from Catalogo import catalogo
import os 

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')

def ADM():
    log_def = "ADM"
    senha_def = "Next"
    tentativas = 0

    log = input("Digite o Login.\n")
    while log != log_def:
        log = input("Login ivalido tente novamente.\n")

    senha = input("Digite sua Senha.\n")
    while senha != senha_def:
        tentativas += 1
        senha = input("Senha ivalido tente novamente.\n")
        if tentativas == 5:
            print("5 tentativas ivalidas.")
            break

def add_catalogo():
    while True:
        limpar_tela()
        print("\n--- Catálogo Atual ---")
        for cod, jogo in catalogo.items():
            print(f"Código: {cod} | Nome: {jogo['nome']} | Preço: R$ {jogo['preco']:.2f}")
        
        codigo = input("\nDigite o código do novo jogo: ")
        if codigo in catalogo:
            print("Esse código já existe no catálogo. Tente novamente.")
            continue

        nome = input("Digite o nome do jogo..: ")
        nome_ja_existe = any(jogo["nome"].lower() == nome.lower() for jogo in catalogo.values())
        
        if nome_ja_existe:
            limpar_tela()
            print("Já existe um jogo com esse nome no catálogo. Tente outro nome.")
            continue

        try:
            preco = float(input("Digite o preço do jogo..: "))
            catalogo[codigo] = {"nome": nome, "preco": preco}
            catalogo[codigo] = 0
            print(f"\nJogo '{nome}' adicionado ao catálogo com sucesso.")
            break
        except ValueError:
            print("Preço inválido. Tente novamente.")



def add_estoque():
    limpar_tela()
    print("\n--- Catálogo Atual ---")
    for cod, jogo in catalogo.items():
        print(f"Código: {cod} | Nome: {jogo['nome']} | Quantidade: {jogo['estoque']}")
    
    codigo = input("Digite o código do jogo para adicionar ao estoque: ")
    
    if codigo not in catalogo:
        print("Esse código não existe no catálogo.")
        return

    try:
        quantidade = int(input("Digite a quantidade a adicionar ao estoque: "))
        catalogo[codigo]["estoque"] += quantidade
        print(f"{quantidade} unidades adicionadas ao estoque do jogo '{catalogo[codigo]['nome']}'.")
    except ValueError:
        print("Quantidade inválida. Tente novamente.")

def ver_estoque():
    limpar_tela()
    print("\n--- Estoque Atual ---")
    for cod, jogo in catalogo.items():
        print(f"Código: {cod} | Nome: {jogo['nome']} | Quantidade: {jogo['estoque']}")

def menu_adm():
    while True:
        print("\n--- Menu Administrador ---")
        print("1 --- Adicionar jogo no catálogo")
        print("2 --- Adicionar jogo ao estoque")
        print("3 --- Ver estoque")
        print("4 --- Fechar sistema")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            add_catalogo()
        elif opcao == "2":
            add_estoque()
        elif opcao == "3":
            ver_estoque()
        elif opcao == "4":
            print("Sistema encerrado.")
            break
        else:
            print("Opção inválida. Tente novamente.")



