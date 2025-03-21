import os
import pandas as pd
from geopy.distance import geodesic
import re  # Importando o módulo de expressões regulares

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
    
    print("\nArquivos disponíveis:")
    for i, file in enumerate(csv_files, start=1):
        print(f"{i}. {file}")
    
    while True:
        try:
            choice = int(input("\nEscolha o número do arquivo desejado: "))
            if 1 <= choice <= len(csv_files):
                return os.path.join("data", csv_files[choice - 1])
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Digite um número correspondente a um arquivo.")

def calculate_speed(coord1, coord2, time_diff_seconds):
    """
    Calcula a velocidade entre dois pontos geográficos em km/h e m/s.
    """
    if time_diff_seconds == 0:
        return 0, 0  # Retorna zero para ambos caso o tempo seja zero
    
    # Distância em quilômetros
    distance_km = geodesic(coord1, coord2).kilometers
    
    # Distância em metros
    distance_m = distance_km * 1000
    
    # Velocidade em km/h
    speed_kmh = (distance_km / time_diff_seconds) * 3600
    
    # Velocidade em m/s
    speed_ms = distance_m / time_diff_seconds
    
    return round(speed_kmh, 2), round(speed_ms, 2)  # Retorna ambas as velocidades com duas casas decimais

def clean_and_filter_data(input_file: str, output_file: str, min_interval_seconds: int = 10):
    """
    Limpa os dados removendo duplicatas e filtrando por intervalo de tempo mínimo entre pontos.
    Calcula a velocidade entre pontos consecutivos e inclui essa informação.
    """
    try:
        # Ler o arquivo CSV
        df = pd.read_csv(input_file)

        # Identificar os nomes das colunas relacionadas à latitude, longitude, data e hora
        lat_col = next((col for col in df.columns if 'lat' in col.lower()), None)
        lon_col = next((col for col in df.columns if 'lon' in col.lower()), None)
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        time_col = next((col for col in df.columns if 'hora' in col.lower() or 'time' in col.lower()), None)

        if not all([lat_col, lon_col, date_col, time_col]):
            print("Erro: Colunas essenciais não encontradas.")
            return

        # Verificar se a coluna 'dateTime' existe e separar 'Date' e 'Time' caso necessário
        if 'dateTime' in df.columns:
            df[['Date', 'Time']] = df['dateTime'].str.split(' at ', expand=True)
            date_col, time_col = 'Date', 'Time'

        # Usar regex para normalizar os separadores entre a data e hora
        def normalize_date_format(date_str):
            # Substituir qualquer coisa entre a data e hora (palavras como 'at', 'a', 'nas horas', ou espaços)
            # Substitui qualquer texto ou separador por um espaço
            return re.sub(r'[^0-9]+', ' ', date_str)

        # Aplicar a função de normalização na coluna de data e hora
        df['Normalized_DateTime'] = df[date_col] + ' ' + df[time_col]
        df['Normalized_DateTime'] = df['Normalized_DateTime'].apply(normalize_date_format)

        # Converter para o formato de timestamp
        df['Timestamp'] = pd.to_datetime(df['Normalized_DateTime'], format='%d %m %Y %H %M %S')

        # Ordenar os dados primeiro por Date e Time
        df = df.sort_values(by=['Timestamp'])

        # Remover duplicatas baseadas em Date e Time
        df = df.drop_duplicates(subset=[date_col, time_col], keep='first')

        # Filtrar os dados para garantir o intervalo mínimo de tempo
        filtered_rows = [df.iloc[0]]  # Sempre incluir o primeiro ponto
        velocities_kmh = [0]  # A velocidade do primeiro ponto é zero
        velocities_ms = [0]   # A velocidade em m/s do primeiro ponto é zero
        last_timestamp = df.iloc[0]['Timestamp']
        last_coord = (df.iloc[0][lat_col], df.iloc[0][lon_col])

        for _, row in df.iterrows():
            current_timestamp = row['Timestamp']
            current_coord = (row[lat_col], row[lon_col])
            time_diff = (current_timestamp - last_timestamp).total_seconds()

            if time_diff >= min_interval_seconds:
                # Calcular a velocidade
                speed_kmh, speed_ms = calculate_speed(last_coord, current_coord, time_diff)
                velocities_kmh.append(speed_kmh)
                velocities_ms.append(speed_ms)
                filtered_rows.append(row)
                last_timestamp = current_timestamp
                last_coord = current_coord

        # Criar um novo DataFrame com os dados filtrados
        filtered_df = pd.DataFrame(filtered_rows)

        # Adicionar as colunas de velocidade
        filtered_df['velocity_km/h'] = velocities_kmh
        filtered_df['velocity_m/s'] = velocities_ms

        # Manter apenas as colunas necessárias na ordem correta
        filtered_df = filtered_df[[lat_col, lon_col, date_col, time_col, 'velocity_km/h', 'velocity_m/s']]

        # Salvar os dados limpos em um novo arquivo CSV
        filtered_df.to_csv(output_file, index=False)

        print(f"\n✅ Dados limpos e salvos em: {output_file}")
    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")

def main():
    # Permitir ao usuário escolher o arquivo CSV
    input_file = choose_csv_file()
    if not input_file:
        return

    # Gerar o nome do arquivo de saída
    output_file = os.path.join("data", f"cleaned_filtered_{os.path.basename(input_file)}")

    # Limpar e filtrar os dados
    clean_and_filter_data(
        input_file=input_file,
        output_file=output_file,
        min_interval_seconds=10
    )

if __name__ == "__main__":
    main()
