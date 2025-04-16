import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import folium
import pandas as pd
import matplotlib.pyplot as plt
from folium.plugins import HeatMap
import webbrowser

def identify_stopped_locations(file_path):
    if not file_path:
        messagebox.showerror("Erro", "Nenhum arquivo selecionado.")
        return

    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    required_cols = {"speed_kmh", "latitude", "longitude", "time"}
    if not required_cols.issubset(df.columns):
        messagebox.showerror("Erro", "Colunas essenciais ausentes no CSV.")
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
                popup="Parado por pelo menos 5 minutos",
                icon=folium.Icon(color="red")
            ).add_to(folium_map)

        heat_data = [[stop["latitude"], stop["longitude"]] for stop in stopped_locations]
        HeatMap(heat_data).add_to(folium_map)

        os.makedirs("maps", exist_ok=True)
        folium_map.save("maps/mapa_paradas.html")

        # Abrir o mapa gerado no navegador
        webbrowser.open(f"file://{os.path.abspath('maps/mapa_paradas.html')}")

        # Criar gráfico
        plt.figure(figsize=(10, 5))
        plt.hist(stop_times, bins=len(set(stop_times)), edgecolor='black', alpha=0.7)
        plt.xlabel("Horário")
        plt.ylabel("Número de Paradas")
        plt.title("Horários das Paradas de 5 minutos")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        plt.savefig("maps/grafico_paradas.png")
        plt.show()

    else:
        messagebox.showinfo("Resultado", "Nenhuma parada longa identificada.")

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
    identify_stopped_locations(file_path)

# GUI Setup
root = tk.Tk()
root.title("Analisador de Paradas (Velocidade Zero)")
root.attributes("-fullscreen", True)
root.resizable(False, False)

# Adicionando texto explicativo
description_text = """
Identifique locais onde a velocidade estve parado por mais de 5 minutos.

Instruções:
- Selecione um arquivo CSV filtrado.
- Clique em "Analisar Paradas" para gerar um mapa com as paradas e um gráfico com os horários.
"""

label_description = tk.Label(root, text=description_text, font=("Arial", 18), justify="left", padx=10, pady=150)
label_description.pack(fill=tk.BOTH, padx=30, pady=0)

# Frame para a funcionalidade principal
frame = ttk.Frame(root, padding=0)
frame.place(relx=0.5, rely=0.5, anchor="center")

selected_file = tk.StringVar()

ttk.Label(frame, text="Arquivo CSV:").grid(row=0, column=0, sticky="w")
ttk.Entry(frame, textvariable=selected_file, width=50).grid(row=0, column=1)
ttk.Button(frame, text="Procurar", command=browse_file).grid(row=0, column=2, padx=5)

ttk.Button(frame, text="Analisar Paradas", command=start_analysis).grid(row=1, column=1, pady=20)

root.mainloop()
