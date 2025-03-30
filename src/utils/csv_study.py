import os
import folium
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
    csv_files = list_csv_files() # chama a list_csv_files para listar os CSV disponíveis
    if not csv_files:
        print("Nenhum arquivo CSV encontrado na pasta 'data'.")
        return None
    
    print("\nArquivos disponíveis:")
    for i, file in enumerate(csv_files, start=1): # se houver disponível, enumera os arquivos
        print(f"{i}. {file}")
    
    while True:
        try:
            choice = int(input("\nEscolha o número do arquivo desejado: ")) # a escolha é um inteiro que enumera os arquivos CSV do "data"
            if 1 <= choice <= len(csv_files): # oercorre desde o primeiro até ao último CSV
                return os.path.join("data", csv_files[choice - 1]) # retorna o CSV escolhido, tendo em conta que o int começa em 0 e a lista em 1
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Digite um número correspondente a um arquivo.")


def speed_graph():
  """
   Análise de Mobilidade e Padrões de Movimento
   - Identifica áreas onde a velocidade é mais alta/baixa.
   - Detectar paradas longas e frequentes.
   - Analisar padrões de deslocamento ao longo do tempo.

  Gera um gráfico com os dados da velocidade e média das mesmas.
  Gera um html com um mapa com as velocidades altas e baixas e onde são mais incidentes
  """
  csv_path = choose_csv_file() # chama a função para escolher o CSV
  if csv_path is None:
    return # Evita erro caso p arquivo não seja selecionado

  df = pd.read_csv(csv_path) # Lê o CSV escolhido
  # Remove espaços extras nos nomes das colunas
  df.columns = df.columns.str.strip()

  if "speed_kmh" not in df.columns:
    print("A coluna 'speed_kmh' não foi encontrada no arquivo CSV.")
    return

  # Converte a coluna para numérico e remove valores inválidos
  # Valores inválidos são convertidos para NaN e depois removidos
  df["speed_kmh"] = pd.to_numeric(df["speed_kmh"], errors="coerce")
  df.dropna(subset=["speed_kmh"])
  df = df[df["speed_kmh"] != 0]

  df["time"] = pd.to_datetime(df["time"], errors="coerce")
  df.dropna(subset=["time"])

  # Verifica se após a remoção de valores inválidos ainda existem dados
  if df.empty:
    print("Não há dados válidos na coluna 'speed_kmh'.")
    return

  # Cria o gráfico
  plt.figure(figsize=(18,8))
  plt.plot(df["time"], df["speed_kmh"], label="Velocidade (km/h)", color="blue")
  plt.title("Gráfico de Velocidade")
  plt.xlabel("Horas")
  plt.xticks(rotation=70)
  plt.ylabel("Velocidade (km/h)")

  plt.xticks(rotation=70) # Rotaciona os rótulos do eixo x para melhor legibilidade 
  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
  plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=10)) # Define o intervalo de 1 hora entre os rótulos do eixo x 

  # Adiciona uma linha horizontal com a média da velocidade
  plt.axhline(y=df["speed_kmh"].mean(), color="red", linestyle="--", label="Média")
  plt.legend()
  plt.grid()
  plt.show() # Mostra o gráico

  """
  Mapa de altas velocidades 
  """
  # Posição inicial no mapa
  map_center = [df["latitude"].iloc[0], df["longitude"].iloc[0]]
  folium_map = folium.Map(location=map_center, zoom_start=14)

  # Marcadores de maior velocidade
  max_speed = df["speed_kmh"].max()

  for index, row in df.iterrows(): # itera sobre as linhas do DataFrame
     # Filtra as velocidades acima de 95% da máxima
     if row["speed_kmh"] >= max_speed * 0.50: # Modificado para 0.75 (ou seja, 75% do máximo)
        folium.CircleMarker(
           location=[row["latitude"], row["longitude"]],
           radius=5,
           color="red",
           fill=True,
           fill_color="red",
           fill_opacity=0.5,
           popup=f"Velocidade: {row['speed_kmh']} km/h"
        ).add_to(folium_map)

  # Adiciona HeatMap para mostrar as áreas com altas velocidades
  heat_data = [[row["latitude"], row["longitude"], row["speed_kmh"]]
              for index, row in df.iterrows()]
  HeatMap(heat_data).add_to(folium_map)

  folium_map.save("mapa_alta_velocidade.html")
  print("Mapa salvo como 'mapa_alta_velocidade.html'.")

  """
  Mapa de baixas velocidades 
  """
  # Posição inicial no mapa
  map_center = [df["latitude"].iloc[0], df["longitude"].iloc[0]]
  folium_map = folium.Map(location=map_center, zoom_start=14)

  # Marcadores de menor velocidade
  min_speed = df["speed_kmh"].min()

  for index, row in df.iterrows(): # itera sobre as linhas do DataFrame
    # Filtra as velocidades abaixo de 25% da mínima
    if row["speed_kmh"] <= min_speed * 1.50:  # Modificado para 1.25 (ou seja, 125% da mínima)
        folium.CircleMarker(
          location=[row["latitude"], row["longitude"]],
          radius=5,
          color="blue",  # Mudando a cor para azul para diferenciar
          fill=True,
          fill_color="blue",
          fill_opacity=0.5,
          popup=f"Velocidade: {row['speed_kmh']} km/h"
        ).add_to(folium_map)


  # Adiciona HeatMap para mostrar as áreas com baixas velocidades
  heat_data = [[row["latitude"], row["longitude"], row["speed_kmh"]]
              for index, row in df.iterrows()]
  HeatMap(heat_data).add_to(folium_map)

  folium_map.save("mapa_baixa_velocidade.html")
  print("Mapa salvo como 'mapa_baixa_velocidade.html'.")


      

# Chama a função para gerar o gráfico
speed_graph()