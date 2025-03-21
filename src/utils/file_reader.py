import pandas as pd

def read_coordinates(file_path, include_timestamps=False):
    """
    Lê as coordenadas de um arquivo CSV.

    :param file_path: Caminho para o arquivo CSV.
    :param include_timestamps: Se True, retorna também os timestamps.
    :return: Lista de coordenadas [(lat, lon)] e, opcionalmente, timestamps.
    """
    try:
        df = pd.read_csv(file_path)
        
        # Normalizar os nomes das colunas para minúsculas e remover espaços extras
        df.columns = df.columns.str.strip().str.lower()
        
        # Verificar se as colunas necessárias existem
        required_columns = {'latitude', 'longitude', 'date', 'time'}
        if not required_columns.issubset(df.columns):
            print("❌ Erro: O CSV não contém as colunas esperadas ('Latitude', 'Longitude', 'Date', 'Time').")
            return [] if not include_timestamps else ([], [])
        
        coordinates = list(zip(df['latitude'], df['longitude']))
        
        if include_timestamps:
            # Combinar 'date' e 'time' em um único timestamp no formato ISO 8601
            df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'], dayfirst=True).dt.strftime('%Y-%m-%dT%H:%M:%S')
            timestamps = df['timestamp'].tolist()
            print("Timestamps gerados:", timestamps)  # Debugging line
            return coordinates, timestamps
        return coordinates
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo CSV: {e}")
        return [] if not include_timestamps else ([], [])