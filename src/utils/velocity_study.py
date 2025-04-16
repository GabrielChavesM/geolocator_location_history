import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import folium
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from folium.plugins import HeatMap
import webbrowser  # Importando para abrir o arquivo no navegador

def analyze_speed(csv_path):
    if not csv_path:
        messagebox.showerror("Erro", "Nenhum arquivo selecionado.")
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    if "speed_kmh" not in df.columns or "latitude" not in df.columns or "longitude" not in df.columns or "time" not in df.columns:
        messagebox.showerror("Erro", "O arquivo CSV não possui todas as colunas necessárias.")
        return

    df["speed_kmh"] = pd.to_numeric(df["speed_kmh"], errors="coerce")
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df.dropna(subset=["speed_kmh", "time", "latitude", "longitude"], inplace=True)
    df = df[df["speed_kmh"] != 0]

    if df.empty:
        messagebox.showwarning("Aviso", "Nenhum dado válido encontrado após filtragem.")
        return

    # Gráfico de velocidade
    plt.figure(figsize=(18, 8))
    plt.plot(df["time"], df["speed_kmh"], label="Velocidade (km/h)", color="blue")
    plt.title("Gráfico de Velocidade")
    plt.xlabel("Tempo")
    plt.ylabel("Velocidade (km/h)")
    plt.xticks(rotation=70)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
    plt.axhline(y=df["speed_kmh"].mean(), color="red", linestyle="--", label="Média")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    os.makedirs("maps", exist_ok=True)
    plt.savefig("maps/grafico_velocidade.png")
    plt.show()
    
    # Mapa de altas velocidades
    map_center = [df["latitude"].iloc[0], df["longitude"].iloc[0]]
    high_speed_map = folium.Map(location=map_center, zoom_start=14)
    max_speed = df["speed_kmh"].max()

    for _, row in df.iterrows():
        if row["speed_kmh"] >= max_speed * 0.5:
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=5,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.5,
                popup=f"Velocidade: {row['speed_kmh']} km/h"
            ).add_to(high_speed_map)

    HeatMap([[row["latitude"], row["longitude"], row["speed_kmh"]] for _, row in df.iterrows()]).add_to(high_speed_map)
    high_speed_map.save("maps/mapa_alta_velocidade.html")

    # Mapa de baixas velocidades
    low_speed_map = folium.Map(location=map_center, zoom_start=14)
    min_speed = df["speed_kmh"].min()

    for _, row in df.iterrows():
        if row["speed_kmh"] <= min_speed * 1.5:
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=5,
                color="blue",
                fill=True,
                fill_color="blue",
                fill_opacity=0.5,
                popup=f"Velocidade: {row['speed_kmh']} km/h"
            ).add_to(low_speed_map)

    HeatMap([[row["latitude"], row["longitude"], row["speed_kmh"]] for _, row in df.iterrows()]).add_to(low_speed_map)
    low_speed_map.save("maps/mapa_baixa_velocidade.html")

    # Abrir os mapas gerados automaticamente no navegador
    webbrowser.open(f"file://{os.path.abspath('maps/mapa_alta_velocidade.html')}")
    webbrowser.open(f"file://{os.path.abspath('maps/mapa_baixa_velocidade.html')}")

    messagebox.showinfo("Sucesso", "Análise completa!\nGráfico salvo como 'maps/grafico_velocidade.png'\nMapas salvos como:\n- 'maps/mapa_alta_velocidade.html'\n- 'maps/mapa_baixa_velocidade.html'")

def browse_file():
    filename = filedialog.askopenfilename(
        title="Escolha um arquivo CSV",
        filetypes=[("CSV files", "*.csv")],
        initialdir="data"
    )
    if filename:
        selected_file.set(filename)

def start_analysis():
    file_path = selected_file.get()
    analyze_speed(file_path)

# GUI Setup
root = tk.Tk()
root.title("Análise de Velocidade")
root.attributes("-fullscreen", True)  # Tornando a janela em tela cheia
root.resizable(False, False)  # Impede o redimensionamento da janela

# Adicionando texto explicativo
description_text = """
Realize uma análise de velocidade contendo coordenadas geográficas e velocidades.

Instruções:
- Selecione um arquivo CSV filtrado.
- Clique em "Analisar Velocidade" para gerar gráficos e mapas de alta e baixa velocidade.
"""

label_description = tk.Label(root, text=description_text, font=("Arial", 18), justify="left", padx=10, pady=150)
label_description.pack(fill=tk.BOTH, padx=30, pady=0)

# Frame para a funcionalidade principal
frame = ttk.Frame(root, padding=0)
frame.place(relx=0.5, rely=0.5, anchor="center")  # Centraliza o frame na janela

selected_file = tk.StringVar()

ttk.Label(frame, text="Arquivo CSV:").grid(row=0, column=0, sticky="w")
ttk.Entry(frame, textvariable=selected_file, width=50).grid(row=0, column=1)
ttk.Button(frame, text="Procurar", command=browse_file).grid(row=0, column=2, padx=5)

ttk.Button(frame, text="Analisar Velocidade", command=start_analysis).grid(row=1, column=1, pady=20)

root.mainloop()
