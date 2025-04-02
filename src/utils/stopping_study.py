import os
import folium
import pandas as pd
import matplotlib.pyplot as plt
from folium.plugins import HeatMap

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

def identify_stopped_locations():
    """
    Identifica locais onde a velocidade é 0 por pelo menos 5 minutos.
    """
    csv_path = choose_csv_file()
    if csv_path is None:
        return
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    
    if "speed_kmh" not in df.columns or "latitude" not in df.columns or "longitude" not in df.columns or "time" not in df.columns:
        print("Colunas essenciais não encontradas no arquivo CSV.")
        return
    
    df["speed_kmh"] = pd.to_numeric(df["speed_kmh"], errors="coerce")
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df.dropna(subset=["speed_kmh", "time", "latitude", "longitude"], inplace=True)
    
    stopped_locations = []
    current_stop = []
    stop_times = []
    
    for i in range(len(df)):
        if df.iloc[i]["speed_kmh"] <= 4:
            current_stop.append(df.iloc[i])
        else:
            if len(current_stop) > 1:
                start_time = current_stop[0]["time"]
                end_time = current_stop[-1]["time"]
                duration = (end_time - start_time).total_seconds() / 60
                if duration >= 5:
                    stopped_locations.append(current_stop[0])
                    stop_times.append(start_time.strftime("%H:%M"))
            current_stop = []
    
    if stopped_locations:
        map_center = [stopped_locations[0]["latitude"], stopped_locations[0]["longitude"]]
        folium_map = folium.Map(location=map_center, zoom_start=14)
        
        for stop in stopped_locations:
            folium.Marker(
                location=[stop["latitude"], stop["longitude"]],
                popup=f"Parado por pelo menos 5 minutos",
                icon=folium.Icon(color="red")
            ).add_to(folium_map)
        
        heat_data = [[stop["latitude"], stop["longitude"]] for stop in stopped_locations]
        HeatMap(heat_data).add_to(folium_map)
        
        folium_map.save("mapa_paradas.html")
        print("Mapa salvo como 'mapa_paradas.html'.")
        
        # Criar gráfico de horários das paradas
        plt.figure(figsize=(10, 5))
        plt.hist(stop_times, bins=len(set(stop_times)), edgecolor='black', alpha=0.7)
        plt.xlabel("Horário")
        plt.ylabel("Número de Paradas")
        plt.title("Horários das Paradas de 5 minutos")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig("grafico_paradas.png")
        print("Gráfico salvo como 'grafico_paradas.png'.")
        plt.show()
    else:
        print("Nenhuma parada longa identificada.")

identify_stopped_locations()
