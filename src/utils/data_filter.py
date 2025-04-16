import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

def list_csv_files(directory="data"):
    return [f for f in os.listdir(directory) if f.endswith(".csv")]

def format_time(seconds):
    if seconds < 60:
        return f"{seconds} segundos"
    elif seconds < 3600:
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes} minutos, {seconds} segundos"
    elif seconds < 86400:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours} horas, {minutes} minutos, {seconds} segundos"
    else:
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days} dias, {hours} horas, {minutes} minutos, {seconds} segundos"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def process_csv(file_path, log_widget, preview_widget):
    try:
        df_original = pd.read_csv(file_path)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao abrir o arquivo CSV: {e}")
        messagebox.showinfo("Erro", "Open your CSV with 'Error Solver'")
        return

    rows_before = df_original.shape[0]
    columns_before = df_original.shape[1]

    df = df_original.copy()
    df.columns = [col.strip().lower() for col in df.columns]

    col_map = {
        "latitude": ["latitude", "lat"],
        "longitude": ["longitude", "lon"],
        "date": ["date"],
        "time": ["time"],
        "datetime": ["datetime", "timestamp", "date_time", "dateTime"]
    }

    mapped_columns = {}

    for key, possible_names in col_map.items():
        for col in df.columns:
            if col in possible_names:
                mapped_columns[key] = col
                break

    if "datetime" in mapped_columns:
        df["datetime"] = pd.to_datetime(df[mapped_columns["datetime"]], errors="coerce")
        df["date"] = df["datetime"].dt.strftime("%Y-%m-%d")
        df["time"] = df["datetime"].dt.strftime("%H:%M:%S")
    elif "date" in mapped_columns and "time" in mapped_columns:
        df["datetime"] = pd.to_datetime(df[mapped_columns["date"]] + " " + df[mapped_columns["time"]], errors="coerce")
    else:
        messagebox.showerror("Erro", "Não foi possível identificar corretamente as colunas de data e hora.")
        messagebox.showinfo("Erro", "Open your CSV with 'Error Solver'")
        return

    if "latitude" not in mapped_columns or "longitude" not in mapped_columns:
        messagebox.showerror("Erro", "Colunas de latitude ou longitude ausentes.")
        messagebox.showinfo("Erro", "Open your CSV with 'Error Solver'")
        return

    df = df.rename(columns={
        mapped_columns["latitude"]: "latitude",
        mapped_columns["longitude"]: "longitude"
    })

    df = df[["latitude", "longitude", "date", "time", "datetime"]].dropna()
    df = df.sort_values(by="datetime").reset_index(drop=True)

    # Remover duplicados
    df = df.drop_duplicates(subset=["latitude", "longitude"], keep="first").reset_index(drop=True)

    # Filtrar por tempo >= 10 segundos
    filtered_rows = []
    last_time = None
    for _, row in df.iterrows():
        if last_time is None or (row["datetime"] - last_time).total_seconds() >= 10:
            filtered_rows.append(row)
            last_time = row["datetime"]

    df = pd.DataFrame(filtered_rows)

    # Calcular tempos/distâncias
    time_distances = [0]
    distances = [0]
    for i in range(1, len(df)):
        time_diff = (df.iloc[i]["datetime"] - df.iloc[i - 1]["datetime"]).total_seconds()
        time_distances.append(time_diff)

        lat1, lon1 = df.iloc[i - 1][["latitude", "longitude"]]
        lat2, lon2 = df.iloc[i][["latitude", "longitude"]]
        distances.append(haversine(lat1, lon1, lat2, lon2))

    df["time_distance"] = time_distances
    df["distance_in_m"] = distances
    df["speed_m/s"] = [round(dist / time, 2) if time > 0 else 0 for dist, time in zip(distances, time_distances)]
    df["speed_kmh"] = df["speed_m/s"].apply(lambda x: round(x * 3.6, 2))
    df["formatted_time"] = df["time_distance"].apply(lambda x: format_time(int(x)))

    total_time = 0
    cumulative_times = []
    for t in df["time_distance"]:
        total_time += t
        cumulative_times.append(format_time(int(total_time)))

    df["total_time"] = cumulative_times
    df["total_distance"] = df["distance_in_m"].cumsum()
    df = df.drop(columns=["datetime", "time_distance"])

    # Salvar arquivo com nome correto
    output_file = os.path.join("data", "cleaned_" + os.path.basename(file_path))
    df.to_csv(output_file, index=False)

    rows_after = df.shape[0]
    columns_after = df.shape[1]

    # Atualizar o log
    log_widget.configure(state='normal')
    log_widget.insert(tk.END, f"\n✅ Arquivo salvo como: {output_file}\n")
    log_widget.insert(tk.END, f"🧹 Linhas eliminadas: {rows_before - rows_after}\n")
    log_widget.insert(tk.END, f"🧹 Colunas eliminadas: {columns_before - columns_after}\n")
    log_widget.insert(tk.END, f"📊 Linhas finais: {rows_after}, Colunas finais: {columns_after}\n")
    log_widget.insert(tk.END, "-" * 50 + "\n")
    log_widget.configure(state='disabled')

    # Exibir conteúdo do CSV na interface gráfica
    preview_widget.configure(state='normal')
    preview_widget.delete(1.0, tk.END)  # Limpar o conteúdo anterior
    preview_widget.insert(tk.END, df.to_string(index=False))  # Mostrar o conteúdo do DataFrame
    preview_widget.configure(state='disabled')

def main_gui():
    root = tk.Tk()
    root.title("Processador de CSV - Limpeza e Estatísticas")
    root.geometry("800x600")
    root.attributes("-fullscreen", True)
    root.resizable(False, False)

    label = tk.Label(root, text="Selecione um arquivo CSV para filtragem:", font=("Arial", 12))
    label.pack(pady=10)

    csv_files = list_csv_files()
    if not csv_files:
        messagebox.showinfo("Nenhum CSV", "Nenhum arquivo CSV foi encontrado na pasta 'data'.")
        root.destroy()
        return

    combo = ttk.Combobox(root, values=csv_files, state="readonly", width=50)
    combo.pack(pady=5)

    log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12, state='disabled')
    log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    preview_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, state='disabled')
    preview_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def on_process():
        selected = combo.get()
        if selected:
            path = os.path.join("data", selected)
            process_csv(path, log_text, preview_text)
        else:
            messagebox.showwarning("Aviso", "Por favor, selecione um arquivo.")

    # Centralizando o botão na tela
    button = tk.Button(root, text="Processar CSV", command=on_process, font=("Arial", 11))
    button.place(relx=0.5, rely=0.5, anchor="center")

    root.mainloop()

if __name__ == "__main__":
    main_gui()
