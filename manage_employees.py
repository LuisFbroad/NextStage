from Task_employee_ADM import *

def menu_administrador():
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