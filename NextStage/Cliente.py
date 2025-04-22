import os
import time
from Catalogo import catalogo

def cliente_main():
    cli_option = cliente_menu()
    if cli_option == 1:
        cli_catalogo()
    elif cli_option == 2:
        cli_compra()

def cliente_menu():
    while True:
        print("1 --- Olhar jogos no catálogo")
        print("2 --- Adicionar o jogo no carrinho")
        print("3 --- Ver carrinho")
        print("4 --- Sair")
        try:
            cli_option = int(input("Escolha uma opção..: "))
            if cli_option in [1, 2, 3, 4]:
                return cli_option
            else:
                print("Opção inválida. Por favor, escolha um número entre 1 e 4.")
        except ValueError:
            limpar_tela()
            print("Entrada inválida. Por favor, digite um número.")


def cli_catalogo():
    limpar_tela()
    print("Catálogo de Jogos:\n")
    for codigo, jogo in catalogo.items():
        print(f"Código: {codigo} | Nome: {jogo['nome']} | Preço: R$ {jogo['preco']:.2f}")
    
    sair = input("\nDigite 'sair' para fechar o catálogo: ")
    if sair.lower() == "sair":
        limpar_tela()
        return cliente_main()
    else:
        print("Comando inválido.")
        return cli_catalogo()

def cli_compra():
    total = 0.00
    print("Bem-vindo à compra de jogos! Veja o catálogo abaixo:\n")

    for codigo, jogo in catalogo.items():
        print(f"Código: {codigo} | Nome: {jogo['nome']} | Preço: R$ {jogo['preco']:.2f}")

    while True:
        compra = input("\nDigite o código do jogo que você deseja comprar\nou 'sair' para finalizar a conta ou 'cancelar' para cancelar a compra: ")

        if compra.lower() == "sair":
            print(f"\nSua compra foi finalizada. Total: R$ {total:.2f}")
            return
        elif compra.lower() == "cancelar":
            print("\nCompra cancelada.")
            return

        try:
            if compra not in catalogo:
                raise ValueError("Código inválido. Por favor, tente novamente.")

            jogo = catalogo[compra]
            total += jogo["preco"]
            print(f"{jogo['nome']} adicionado à compra. Preço: R$ {jogo['preco']:.2f}")
        except ValueError as ve:
            print(f"Erro: {ve}")
        except Exception as e:
            print(f"Erro inesperado: {e}")


def limpar_tela():
    if os.name == 'nt':
        os.system('cls')