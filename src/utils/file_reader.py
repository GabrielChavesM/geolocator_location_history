
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

        # Verificar se as colunas necessárias existem
        if 'Latitude' not in df or 'Longitude' not in df or 'Data' not in df or 'Hora' not in df:
            print("Erro: O arquivo CSV não contém as colunas necessárias ('Latitude', 'Longitude', 'Data', 'Hora').")
            return [] if not include_timestamps else ([], [])

        coordinates = list(zip(df['Latitude'], df['Longitude']))

        if include_timestamps:
            # Combinar 'Data' e 'Hora' em um único timestamp no formato ISO 8601
            df['Timestamp'] = pd.to_datetime(df['Data'] + ' ' + df['Hora']).dt.strftime('%Y-%m-%dT%H:%M:%S')
            timestamps = df['Timestamp'].tolist()
            print("Timestamps gerados:", timestamps)  # Debugging line
            return coordinates, timestamps
        return coordinates
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return [] if not include_timestamps else ([], [])