import os
import pandas as pd
import re
from datetime import datetime

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

def process_csv(file_path):
    """
    Processa o CSV para garantir que possui as colunas corretas.
    """
    df = pd.read_csv(file_path)
    
    # Normalizar nomes de colunas (tornando tudo minúsculo)
    df.columns = [col.strip().lower() for col in df.columns]
    
    expected_columns = {"latitude", "longitude", "date", "time"}
    current_columns = set(df.columns)
    
    # Se o CSV já contém as colunas corretas, apenas salva e retorna
    if expected_columns.issubset(current_columns):
        print("\nO CSV já possui as colunas corretas. Nenhuma alteração necessária.")
        return
    
    # Identificar possíveis colunas de latitude e longitude
    lat_col = next((col for col in df.columns if "lat" in col), None)
    lon_col = next((col for col in df.columns if "lon" in col), None)
    
    # Analisar a primeira linha para identificar data e hora
    sample_row = df.iloc[0]
    date_col, time_col = None, None
    
    for col in df.columns:
        if detect_date_format(str(sample_row[col])):
            date_col = col
        elif detect_time_format(str(sample_row[col])):
            time_col = col
    
    # Se data e hora estiverem na mesma coluna, separá-las
    if date_col is None or time_col is None:
        for col in df.columns:
            match = re.match(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})[^\d]+(\d{2}:\d{2}:\d{2})", str(sample_row[col]))
            if match:
                df["date"] = df[col].apply(lambda x: re.match(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", str(x)).group(1) if re.match(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", str(x)) else "")
                df["time"] = df[col].apply(lambda x: re.match(r".*?(\d{2}:\d{2}:\d{2})", str(x)).group(1) if re.match(r".*?(\d{2}:\d{2}:\d{2})", str(x)) else "")
                date_col, time_col = "date", "time"
                break
    
    if not all([lat_col, lon_col, date_col, time_col]):
        print("Erro: Não foi possível identificar todas as colunas corretamente.")
        return
    
    # Renomear as colunas identificadas para os nomes esperados
    df = df.rename(columns={lat_col: "Latitude", lon_col: "Longitude", date_col: "Date", time_col: "Time"})
    
    # Manter apenas as colunas relevantes
    df = df[["Latitude", "Longitude", "Date", "Time"]]
    
    # Criar um novo arquivo CSV com os dados corrigidos
    output_file = os.path.join("data", "cleaned_" + os.path.basename(file_path))
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ CSV processado e salvo como: {output_file}")

def main():
    file_path = choose_csv_file()
    if file_path:
        process_csv(file_path)

if __name__ == "__main__":
    main()
