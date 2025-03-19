import os
import pandas as pd

def list_csv_files(directory="data"):
    """
    Lista todos os arquivos CSV dentro do diretório especificado.
    """
    return [f for f in os.listdir(directory) if f.endswith(".csv")]

def choose_csv_file():
    """
    Permite ao usuário escolher um arquivo CSV disponível na pasta "data".
    """
    csv_files = list_csv_files()
    if not csv_files:
        print("Nenhum arquivo CSV encontrado na pasta 'data'.")
        return None
    
    print("Arquivos disponíveis:")
    for i, file in enumerate(csv_files, start=1):
        print(f"{i}. {file}")
    
    while True:
        try:
            choice = int(input("Escolha o número do arquivo desejado: "))
            if 1 <= choice <= len(csv_files):
                return os.path.join("data", csv_files[choice - 1])
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Digite um número correspondente a um arquivo.")

def clean_data(input_file: str, output_file: str, key_columns: list, min_interval_seconds: int = 10):
    """
    Limpa os dados removendo duplicatas e filtrando por intervalo de tempo mínimo entre pontos.

    Args:
        input_file (str): Caminho para o arquivo CSV de entrada.
        output_file (str): Caminho para salvar o arquivo CSV limpo.
        key_columns (list): Lista de nomes de colunas para verificar duplicatas.
        min_interval_seconds (int): Intervalo mínimo de tempo entre os pontos em segundos.
    """
    try:
        # Ler o arquivo CSV
        df = pd.read_csv(input_file)

        # Remover duplicatas com base nas colunas especificadas
        df_cleaned = df.drop_duplicates(subset=key_columns, keep='first')

        # Verificar se as colunas necessárias existem para filtrar o intervalo de tempo
        if 'Data' not in df_cleaned or 'Hora' not in df_cleaned:
            print("Erro: O arquivo CSV não contém as colunas necessárias ('Data', 'Hora').")
            return

        # Combinar 'Data' e 'Hora' em um único timestamp
        df_cleaned['Timestamp'] = pd.to_datetime(df_cleaned['Data'] + ' ' + df_cleaned['Hora'])

        # Ordenar os dados por timestamp (caso não estejam ordenados)
        df_cleaned = df_cleaned.sort_values(by='Timestamp')

        # Filtrar os dados para garantir o intervalo mínimo de tempo
        filtered_rows = [df_cleaned.iloc[0]]  # Sempre incluir o primeiro ponto
        last_timestamp = df_cleaned.iloc[0]['Timestamp']

        for _, row in df_cleaned.iterrows():
            current_timestamp = row['Timestamp']
            if (current_timestamp - last_timestamp).total_seconds() >= min_interval_seconds:
                filtered_rows.append(row)
                last_timestamp = current_timestamp

        # Criar um novo DataFrame com os dados filtrados
        filtered_df = pd.DataFrame(filtered_rows)

        # Remover a coluna 'Timestamp' antes de salvar
        filtered_df = filtered_df.drop(columns=['Timestamp'])

        # Salvar os dados limpos em um novo arquivo CSV
        filtered_df.to_csv(output_file, index=False)

        print(f"Dados limpos e salvos em {output_file}.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

def main():
    # Permitir ao usuário escolher o arquivo CSV
    input_file = choose_csv_file()
    if not input_file:
        return

    # Gerar o nome do arquivo de saída
    output_file = os.path.join("data", f"cleaned_filtered_{os.path.basename(input_file)}")

    # Limpar e filtrar os dados
    clean_data(
        input_file=input_file,
        output_file=output_file,
        key_columns=['Hora'],
        min_interval_seconds=10
    )

if __name__ == "__main__":
    main()