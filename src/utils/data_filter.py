import os
import pandas as pd
import re
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

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

def detect_date_format(value):
    """
    Detecta o formato de uma data e retorna True se for válido.
    """
    date_formats = ["%d-%m-%Y", "%Y-%m-%d", "%m-%d-%Y"]
    for date_format in date_formats:
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            continue
    return False

def detect_time_format(value):
    """
    Detecta se o valor é um horário válido no formato HH:MM:SS.
    """
    try:
        datetime.strptime(value, "%H:%M:%S")
        return True
    except ValueError:
        return False

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distância entre dois pontos geográficos usando a fórmula de Haversine.
    Retorna a distância em metros.
    """
    R = 6371000  # Raio da Terra em metros
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def format_time(seconds):
    """
    Formata o tempo em segundos para uma string legível, dependendo da magnitude:
    - Segundos até 1 minuto
    - Minutos até 1 hora
    - Horas até 1 dia
    - Dias, horas, minutos e segundos para tempos maiores que 1 dia
    """
    if seconds < 60:
        return f"{seconds} segundos"
    elif seconds < 3600:
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes} minutos, {seconds} segundos"
    elif seconds < 86400:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours} horas, {minutes} minutos, {seconds} segundos"
    else:
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days} dias, {hours} horas, {minutes} minutos, {seconds} segundos"

def process_csv(file_path):
    """
    Processa o CSV para identificar corretamente as colunas necessárias e calcular distância, tempo e velocidade.
    """
    df = pd.read_csv(file_path)
    
    # Normalizar nomes de colunas para minúsculas e remover espaços
    df.columns = [col.strip().lower() for col in df.columns]

    # Mapear nomes de colunas possíveis
    col_map = {
        "latitude": ["latitude", "lat"],
        "longitude": ["longitude", "lon"],
        "date": ["date"],
        "time": ["time"],
        "datetime": ["datetime", "timestamp", "date_time", "dateTime"]
    }

    mapped_columns = {}

    for key, possible_names in col_map.items():
        for col in df.columns:
            if col in possible_names:
                mapped_columns[key] = col
                break

    # Verificar se temos data e hora separadas ou juntas
    if "datetime" in mapped_columns:
        df["datetime"] = pd.to_datetime(df[mapped_columns["datetime"]], errors="coerce")
        df["date"] = df["datetime"].dt.strftime("%Y-%m-%d")
        df["time"] = df["datetime"].dt.strftime("%H:%M:%S")
    else:
        if "date" in mapped_columns and "time" in mapped_columns:
            df["datetime"] = pd.to_datetime(df[mapped_columns["date"]] + " " + df[mapped_columns["time"]], errors="coerce")
        else:
            print("Erro: Não foi possível identificar corretamente data e hora.")
            return

    # Garantir que as colunas latitude e longitude estejam presentes
    if "latitude" not in mapped_columns or "longitude" not in mapped_columns:
        print("Erro: Não foi possível identificar colunas de latitude e longitude.")
        return

    df = df.rename(columns={
        mapped_columns["latitude"]: "latitude",
        mapped_columns["longitude"]: "longitude"
    })

    df = df[["latitude", "longitude", "date", "time", "datetime"]].dropna()

    # Ordenar pela data/hora
    df = df.sort_values(by="datetime").reset_index(drop=True)

    # Remover duplicados, mantendo apenas a primeira ocorrência
    df = df.drop_duplicates(subset=["latitude", "longitude"], keep="first").reset_index(drop=True)

    # Filtrar linhas com intervalos de tempo menores que 10 segundos
    filtered_rows = []
    last_time = None

    for _, row in df.iterrows():
        if last_time is None or (row["datetime"] - last_time).total_seconds() >= 10:
            filtered_rows.append(row)
            last_time = row["datetime"]

    df = pd.DataFrame(filtered_rows)

    # Calcular a diferença de tempo e distância entre as linhas consecutivas
    time_distances = [0]  # A primeira linha não tem diferença de tempo anterior
    distances = [0]  # A primeira linha não tem distância anterior
    for i in range(1, len(df)):
        # Calcular a diferença de tempo em segundos
        time_diff = (df.iloc[i]["datetime"] - df.iloc[i - 1]["datetime"]).total_seconds()
        time_distances.append(time_diff)

        # Calcular a distância entre os pontos geográficos
        lat1, lon1 = df.iloc[i - 1][["latitude", "longitude"]]
        lat2, lon2 = df.iloc[i][["latitude", "longitude"]]
        distance = haversine(lat1, lon1, lat2, lon2)
        distances.append(distance)

    # Adicionar as colunas "time_distance" e "distance_in_m" ao DataFrame
    df["time_distance"] = time_distances
    df["distance_in_m"] = distances

    # Calcular velocidade
    df["speed_m/s"] = [round(dist / time, 2) if time > 0 else 0 for dist, time in zip(distances, time_distances)]
    df["speed_kmh"] = df["speed_m/s"].apply(lambda x: round(x * 3.6, 2))

    # Adicionar coluna formatada de tempo acumulado
    df["formatted_time"] = df["time_distance"].apply(lambda x: format_time(int(x)))

    # Calcular o tempo total acumulado
    total_time_seconds = 0
    total_time_formatted = []
    for time in df["time_distance"]:
        total_time_seconds += time
        total_time_formatted.append(format_time(int(total_time_seconds)))

    df["total_time"] = total_time_formatted

    # Calcular a distância total acumulada
    df["total_distance"] = df["distance_in_m"].cumsum()

    # Remover as colunas "datetime" e "time_distance" antes de salvar
    df = df.drop(columns=["datetime", "time_distance"])

    # Salvar CSV limpo
    output_file = os.path.join("data", "cleaned_" + os.path.basename(file_path))
    df.to_csv(output_file, index=False)
    print(f"\n✅ CSV processado e salvo como: {output_file}")

def main():
    file_path = choose_csv_file()
    if file_path:
        process_csv(file_path)

if __name__ == "__main__":
    main()

# TODO 
# 4. Infiram o meio de transporte utilizado em cada um deles.
# Tarefa 4, 5