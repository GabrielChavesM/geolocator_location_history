import os
import pandas as pd
import folium
from utils.file_reader import read_coordinates
import time
from folium.plugins import TimestampedGeoJson

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

def create_timelapse(coordinates, timestamps, output_file='maps/timelapse_map.html'):
    """
    Cria um timelapse mostrando os caminhos do utilizador ponto a ponto pelo horário.
    """
    if not coordinates or not timestamps:
        print("Nenhum dado disponível para criar o timelapse.")
        return

    # Criar a pasta "maps" se não existir
    os.makedirs("maps", exist_ok=True)

    map_ = folium.Map(location=coordinates[0], zoom_start=12)

    features = [{
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[lon, lat] for lat, lon in coordinates]
        },
        "properties": {
            "times": timestamps,
            "popup": "Caminho do utilizador"
        }
    }]

    timestamped_geojson = TimestampedGeoJson({
        "type": "FeatureCollection",
        "features": features
    }, period="PT1S", add_last_point=True)

    timestamped_geojson.add_to(map_)
    map_.save(output_file)
    print(f"Timelapse completo e salvo como '{output_file}'.")

def main():
    csv_file = choose_csv_file()
    if not csv_file:
        return
    
    coordinates, timestamps = read_coordinates(csv_file, include_timestamps=True)
    
    if coordinates:
        avg_lat = sum(lat for lat, _ in coordinates) / len(coordinates)
        avg_lon = sum(lon for _, lon in coordinates) / len(coordinates)

        # Criar a pasta "maps" se não existir
        os.makedirs("maps", exist_ok=True)

        # Criar o mapa estático
        map_ = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
        for lat, lon in coordinates:
            folium.CircleMarker(location=[lat, lon], radius=5, color='blue').add_to(map_)

        static_map_path = os.path.join("maps", "location_map.html")
        map_.save(static_map_path)
        print(f"Mapa estático criado e salvo como '{static_map_path}'.")

        # Criar o timelapse
        create_timelapse(coordinates, timestamps)
    else:
        print("Nenhuma coordenada encontrada.")

if __name__ == "__main__":
    main()