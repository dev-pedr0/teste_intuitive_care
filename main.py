from programas import prog1, prog2, prog3

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
                print("""
                    Esse exercício é uma aplicação web. 
                    No diretório raiz digite o comando 'npm un dev'.
                    O sistema irá rodar o frontend e o backend em cojunto.
                    É necessário haver um banco de dados disponível, rodar a primeira opção de código na atividade 3 para gerar as tabelas,
                    e atualizar a função auxiliar conectar_banco() em support_code.py e em db.py
                      """)

            case "0":
                print("Saindo...")
                break
            case _:
                print("Valor inválido")

#Executor padrão
if __name__ == "__main__":
    menu()