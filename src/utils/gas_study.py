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

def calculate_distance_and_fuel():
    """
    Calcula a soma das distâncias percorridas e o consumo de combustível baseado na eficiência informada pelo usuário.
    """
    fuel_consumption = float(input("\nInsira o consumo médio do veículo (km/l): "))
    fuel_price = float(input("\nInsira o preço do combustível (€/l): "))
    
    csv_path = choose_csv_file()
    if csv_path is None:
        return
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    
    if "distance_in_m" not in df.columns or "time" not in df.columns:
        print("Colunas essenciais não encontradas no arquivo CSV.")
        return
    
    df["distance_in_m"] = pd.to_numeric(df["distance_in_m"], errors="coerce")
    df.dropna(subset=["distance_in_m"], inplace=True)
    
    total_distance = df["distance_in_m"].sum() / 1000  # Convertendo para km
    fuel_consumed = total_distance / fuel_consumption  # Consumo baseado na entrada do usuário
    
    print(f"Distância total percorrida: {total_distance:.2f} km")
    print(f"Combustível consumido: {fuel_consumed:.2f} litros")
    
    # Cálculo do custo acumulado ao longo do tempo
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df.dropna(subset=["time"], inplace=True)
    df.sort_values(by="time", inplace=True)
    df["cumulative_distance_km"] = df["distance_in_m"].cumsum() / 1000
    df["cumulative_fuel"] = df["cumulative_distance_km"] / fuel_consumption
    df["cumulative_cost"] = df["cumulative_fuel"] * fuel_price
    
    # Criar gráfico
    plt.figure(figsize=(10, 5))
    plt.plot(df["time"], df["cumulative_cost"], marker="o", linestyle="-", color="b")
    plt.xlabel("Hora")
    plt.ylabel("Custo Acumulado (€)")
    plt.title("Custo do Combustível ao Longo do Tempo")
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

calculate_distance_and_fuel()
