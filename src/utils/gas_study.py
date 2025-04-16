import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

def list_csv_files(directory="data"):
    return [f for f in os.listdir(directory) if f.endswith(".csv")]

def process_csv(csv_path, fuel_consumption, fuel_price):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    if "distance_in_m" not in df.columns or "time" not in df.columns:
        messagebox.showerror("Erro", "Colunas 'distance_in_m' ou 'time' não encontradas.")
        return

    df["distance_in_m"] = pd.to_numeric(df["distance_in_m"], errors="coerce")
    df.dropna(subset=["distance_in_m"], inplace=True)

    total_distance = df["distance_in_m"].sum() / 1000
    fuel_consumed = total_distance / fuel_consumption
    custo_total = fuel_consumed * fuel_price

    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df.dropna(subset=["time"], inplace=True)
    df.sort_values(by="time", inplace=True)

    df["cumulative_distance_km"] = df["distance_in_m"].cumsum() / 1000
    df["cumulative_fuel"] = df["cumulative_distance_km"] / fuel_consumption
    df["cumulative_cost"] = df["cumulative_fuel"] * fuel_price

    # Plotando
    plt.figure(figsize=(10, 5))
    plt.plot(df["time"], df["cumulative_cost"], marker="o", linestyle="-", color="b")
    plt.xlabel("Hora")
    plt.ylabel("Custo Acumulado (€)")
    plt.title("Custo do Combustível ao Longo do Tempo")
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout()
    plt.show()

    messagebox.showinfo("Resumo",
        f"Distância total percorrida: {total_distance:.2f} km\n"
        f"Combustível consumido: {fuel_consumed:.2f} litros\n"
        f"Custo total: {custo_total:.2f} €"
    )

def browse_file():
    filename = filedialog.askopenfilename(
        title="Escolha um arquivo CSV",
        filetypes=[("CSV files", "*.csv")],
        initialdir="data"
    )
    if filename:
        selected_file.set(filename)

def run_analysis():
    try:
        fuel_cons = float(entry_consumo.get())
        fuel_price = float(entry_preco.get())
        filepath = selected_file.get()
        if not filepath:
            messagebox.showwarning("Atenção", "Selecione um arquivo CSV.")
            return
        process_csv(filepath, fuel_cons, fuel_price)
    except ValueError:
        messagebox.showerror("Erro", "Consumo e preço devem ser números válidos.")

# GUI
root = tk.Tk()
root.title("Analisador de Consumo de Combustível")
root.geometry("575x350")
root.attributes("-fullscreen", True)
root.resizable(False, False)

# Adicionando o tutorial/descrição
description = """
Aqui pode analisar dados de consumo de combustível registrados em um arquivo CSV. 
Através dos dados de distância percorrida e tempo, ele calcula o consumo total de combustível e o custo 
acumulado ao longo do tempo, considerando o consumo de combustível e o preço fornecido pelo utilizador. 
Além disso, exibe um gráfico com o custo acumulado ao longo do tempo.

Instruções:
1. Selecione um arquivo CSV contendo as colunas 'distance_in_m' (distância em metros) e 'time' (tempo).
2. Informe o consumo do veículo (km/l) e o preço do combustível (€/l).
3. Clique em "Analisar" para visualizar os resultados e o gráfico de custo acumulado.

Entre com os dados no formulário abaixo e clique em "Analisar" para começar a análise.

[Recomenda-se filtrar os dados antes de usar esta funcionalidade]
"""

label_description = tk.Label(root, text=description, font=("Arial", 18), justify="left", padx=0, pady=5)
label_description.pack(fill=tk.BOTH, expand=False, padx=0, pady=50)

# Centralizando o frame
frame = ttk.Frame(root, padding=50)
frame.pack(expand=False)

selected_file = tk.StringVar()

ttk.Label(frame, text="Arquivo CSV:").grid(row=0, column=0, sticky="w")
ttk.Entry(frame, textvariable=selected_file, width=50).grid(row=0, column=1)
ttk.Button(frame, text="Procurar", command=browse_file).grid(row=0, column=2, padx=5)

ttk.Label(frame, text="Consumo (km/l):").grid(row=1, column=0, sticky="w", pady=(10, 0))
entry_consumo = ttk.Entry(frame)
entry_consumo.grid(row=1, column=1, pady=(10, 0))

ttk.Label(frame, text="Preço do Combustível (€/l):").grid(row=2, column=0, sticky="w", pady=(10, 0))
entry_preco = ttk.Entry(frame)
entry_preco.grid(row=2, column=1, pady=(10, 0))

ttk.Button(frame, text="Analisar", command=run_analysis).grid(row=3, column=1, pady=20)

root.mainloop()
