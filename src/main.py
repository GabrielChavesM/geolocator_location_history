import os

def list_available_scripts(directory="./src/utils"):
    """
    Lista os scripts Python disponíveis no diretório especificado.
    """
    os.system("clear")
    scripts = {}
    try:
        # Lista todos os arquivos no diretório e filtra os .py
        files = [f for f in os.listdir(directory) if f.endswith(".py")]
        for i, file in enumerate(files, start=1):
            scripts[i] = os.path.join(directory, file)  # Mapeia o número ao caminho do arquivo
        # Se o ficheiro for o "file_reader.py", remove-o da lista
        if "file_reader.py" in scripts.values():
            scripts.pop(list(scripts.keys())[list(scripts.values()).index("file_reader.py")])

    except FileNotFoundError:
        print(f"O diretório {directory} não foi encontrado.")
    
    return scripts

def execute_script(script_path):
    """
    Executa o script escolhido pelo usuário, dado o caminho correto do script.
    """
    # Executa o script no caminho fornecido
    os.system(f"python3 {script_path}")

def main():
    while True:
        print("\nSelecione um dos scripts para executar:")
        scripts = list_available_scripts()
        
        # Verificar se scripts foram encontrados
        if not scripts:
            print("Nenhum script encontrado no diretório 'utils'.")
            break
        
        # Listar os scripts disponíveis
        for i, script_path in scripts.items():
            script_name = os.path.basename(script_path)
            print(f"{i}. {script_name}")
        
        print("0. Sair")
        
        choice = input("\nDigite o número da opção desejada: ")
        
        if choice == "0":
            print("Saindo...")
            break
        
        try:
            choice = int(choice)
            if choice in scripts:
                script_path = scripts[choice]
                print(f"\nExecutando '{os.path.basename(script_path)}'...\n")
                execute_script(script_path)
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Digite um número correspondente a uma opção.")

if __name__ == "__main__":
    main()
