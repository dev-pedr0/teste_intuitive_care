from programas import prog1, prog2, prog3, prog4

# Função de menu
def menu():
    while True:
        print("\n=== Menu Principal ===")
        print("1 - Programa 1")
        print("2 - Programa 2")
        print("3 - Programa 3")
        print("4 - Programa 4")
        print("0 - Sair")
        opcao = input("Escolha: ")

        match opcao:
            case "1":
                prog1.executar()
            case "2":
                prog2.executar()
            case "3":
                prog3.executar()
            case "4":
                prog4.executar()
            case "0":
                print("Saindo...")
                break
            case _:
                print("Valor inválido")

#Executor padrão
if __name__ == "__main__":
    menu()