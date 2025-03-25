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

def process_csv(file_path):
    """
    Processa o CSV para garantir que possui as colunas corretas.
    """
    df = pd.read_csv(file_path)
    
    # Normalizar nomes de colunas
    df.columns = [col.strip().lower() for col in df.columns]
    
    expected_columns = {"latitude", "longitude", "date", "time"}
    current_columns = set(df.columns)
    
    if expected_columns.issubset(current_columns):
        df = df[["latitude", "longitude", "date", "time"]]
    else:
        lat_col = next((col for col in df.columns if "lat" in col), None)
        lon_col = next((col for col in df.columns if "lon" in col), None)
        
        sample_row = df.iloc[0]
        date_col, time_col = None, None
        
        for col in df.columns:
            if detect_date_format(str(sample_row[col])):
                date_col = col
            elif detect_time_format(str(sample_row[col])):
                time_col = col
        
        if date_col is None or time_col is None:
            for col in df.columns:
                match = re.match(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})[^\d]+(\d{2}:\d{2}:\d{2})", str(sample_row[col]))
                if match:
                    df["date"] = df[col].apply(lambda x: re.match(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", str(x)).group(1))
                    df["time"] = df[col].apply(lambda x: re.match(r".*?(\d{2}:\d{2}:\d{2})", str(x)).group(1))
                    date_col, time_col = "date", "time"
                    break
        
        if not all([lat_col, lon_col, date_col, time_col]):
            print("Erro: Não foi possível identificar todas as colunas corretamente.")
            return
        
        df = df.rename(columns={lat_col: "latitude", lon_col: "longitude", date_col: "date", time_col: "time"})
        df = df[["latitude", "longitude", "date", "time"]]
    
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"], errors='coerce')
    df = df.dropna(subset=["datetime"])
    df = df.sort_values(by="datetime")
    
    filtered_rows = []
    last_time = None
    
    for _, row in df.iterrows():
        if last_time is None or (row["datetime"] - last_time) >= timedelta(seconds=10):
            filtered_rows.append(row)
            last_time = row["datetime"]
    
    df = pd.DataFrame(filtered_rows)[["latitude", "longitude", "date", "time"]]
    
    # Calcular a distância entre os pontos consecutivos
    distances = [0]  # A primeira linha não tem distância anterior
    times = [0]  # A primeira linha não tem tempo anterior
    for i in range(1, len(df)):
        lat1, lon1 = df.iloc[i - 1][["latitude", "longitude"]]
        lat2, lon2 = df.iloc[i][["latitude", "longitude"]]
        distance = haversine(lat1, lon1, lat2, lon2)
        distances.append(distance)
        
        # Calcular a diferença de tempo em segundos
        time_diff = (pd.to_datetime(df.iloc[i]["time"]) - pd.to_datetime(df.iloc[i - 1]["time"])).total_seconds()
        times.append(time_diff if time_diff > 0 else 0)  # Evitar divisões por zero

    df["distance_in_m"] = distances  # Adicionar a coluna "distance"
    
    # Calcular a velocidade em m/s e km/h
    df["speed_m/s"] = [dist / time if time > 0 else 0 for dist, time in zip(distances, times)]
    df["speed_kmh"] = df["speed_m/s"] * 3.6  # Converter m/s para km/h
    
    # Arredondar os valores das colunas para 2 casas decimais
    df["distance_in_m"] = df["distance_in_m"].round(2)
    df["speed_m/s"] = df["speed_m/s"].round(2)
    df["speed_kmh"] = df["speed_kmh"].round(2)
    # Calcular a distância total acumulada e arredonda para 2 casas decimais
    df["total_distance"] = df["distance_in_m"].cumsum()
    df["total_distance"] = df["total_distance"].round(2)

    # Criar a coluna "datetime" combinando "date" e "time"
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"], errors="coerce", dayfirst=True)

    # Remover linhas com valores inválidos na coluna "datetime"
    if df["datetime"].isnull().any():
        print("⚠️ Algumas linhas possuem valores inválidos em 'datetime' e serão removidas.")
        df = df.dropna(subset=["datetime"])

    # Ordenar o DataFrame pela coluna "datetime"
    df = df.sort_values(by="datetime").reset_index(drop=True)

    # Calcular o tempo acumulado desde o início até a linha atual manualmente
    start_time = df["datetime"].iloc[0]
    time_needed = []
    for current_time in df["datetime"]:
        elapsed_seconds = int((current_time - start_time).total_seconds())
        formatted_time = str(timedelta(seconds=elapsed_seconds))
        time_needed.append(formatted_time)

    # Adicionar a coluna "time_needed" ao DataFrame
    df["time_needed"] = time_needed
    
    output_file = os.path.join("data", "cleaned_" + os.path.basename(file_path))
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ CSV processado e salvo como: {output_file}")

# TODO Calcular a distância total percorrida (somando a distância de linha a linha)
# e o tempo total gasto (última hora - primeira hora)

def main():
    file_path = choose_csv_file()
    if file_path:
        process_csv(file_path)

if __name__ == "__main__":
    main()
