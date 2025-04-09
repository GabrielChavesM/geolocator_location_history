import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
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

import os

def process_csv(file_path, log_widget, preview_widget):
    try:
        # Garantir que a pasta "data" exista
        output_dir = "data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        df_original = pd.read_csv(file_path)
        rows_before = df_original.shape[0]
        columns_before = df_original.shape[1]

        df = df_original.copy()

        # Perguntar ao usuário em qual coluna estão os dados de latitude, longitude, data e hora
        col_lat = simpledialog.askinteger("Coluna Latitude", "Em qual coluna está a latitude (1 a n)?", minvalue=1, maxvalue=columns_before)
        col_lon = simpledialog.askinteger("Coluna Longitude", "Em qual coluna está a longitude (1 a n)?", minvalue=1, maxvalue=columns_before)
        col_date = simpledialog.askinteger("Coluna Date", "Em qual coluna está a data (1 a n)?", minvalue=1, maxvalue=columns_before)
        col_time = simpledialog.askinteger("Coluna Time", "Em qual coluna está o tempo (1 a n)?", minvalue=1, maxvalue=columns_before)

        # Ajustar as colunas para índices baseados em 0
        col_lat -= 1
        col_lon -= 1
        col_date -= 1
        col_time -= 1

        # Definir cabeçalhos de colunas
        new_lat_header = simpledialog.askstring("Novo Cabeçalho", "Qual é o novo nome para a coluna de Latitude?")
        new_lon_header = simpledialog.askstring("Novo Cabeçalho", "Qual é o novo nome para a coluna de Longitude?")
        new_date_header = simpledialog.askstring("Novo Cabeçalho", "Qual é o novo nome para a coluna de Data?")
        new_time_header = simpledialog.askstring("Novo Cabeçalho", "Qual é o novo nome para a coluna de Hora?")

        # Renomear as colunas conforme os cabeçalhos fornecidos pelo usuário
        df.columns = ['latitude', 'longitude', 'date', 'time'] + list(df.columns[4:])
        
        # Atribuir os dados das colunas para latitude, longitude, date e time
        df['latitude'] = df.iloc[:, col_lat]
        df['longitude'] = df.iloc[:, col_lon]
        df['date'] = df.iloc[:, col_date]
        df['time'] = df.iloc[:, col_time]

        # Substituir os cabeçalhos das colunas de acordo com o nome fornecido pelo usuário
        df = df.rename(columns={
            "latitude": new_lat_header,
            "longitude": new_lon_header,
            "date": new_date_header,
            "time": new_time_header
        })

        # Mapear as colunas
        col_map = {
            "latitude": [new_lat_header, "lat"],
            "longitude": [new_lon_header, "lon"],
            "date": [new_date_header],
            "time": [new_time_header],
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
            return

        if "latitude" not in mapped_columns or "longitude" not in mapped_columns:
            messagebox.showerror("Erro", "Colunas de latitude ou longitude ausentes.")
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
        output_file = os.path.join(output_dir, "cleaned_" + os.path.basename(file_path))
        
        # Verificar se o caminho de saída está correto
        print(f"Salvando arquivo em: {output_file}")
        
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

    except pd.errors.ParserError as e:
        # Caso o CSV tenha erro, pedir ao usuário para remover linhas inválidas
        messagebox.showerror("Erro", f"Ocorreu um erro ao processar o arquivo: {str(e)}")
        
        remove_invalid_rows = simpledialog.askinteger("Linhas Inválidas", "Quantas linhas inválidas deseja eliminar?", minvalue=0)
        
        if remove_invalid_rows is not None and remove_invalid_rows > 0:
            try:
                # Remover as primeiras linhas e tentar novamente
                df_original = pd.read_csv(file_path, skiprows=remove_invalid_rows)
                output_file = os.path.join("data", "cleaned_removed_" + os.path.basename(file_path))
                df_original.to_csv(output_file, index=False)
                
                # Atualizar o log
                rows_after = df_original.shape[0]
                columns_after = df_original.shape[1]
                log_widget.configure(state='normal')
                log_widget.insert(tk.END, f"\n✅ Arquivo salvo como: {output_file}\n")
                log_widget.insert(tk.END, f"🧹 Linhas removidas: {remove_invalid_rows}\n")
                log_widget.insert(tk.END, f"📊 Linhas finais: {rows_after}, Colunas finais: {columns_after}\n")
                log_widget.insert(tk.END, "-" * 50 + "\n")
                log_widget.configure(state='disabled')

                # Exibir conteúdo do CSV na interface gráfica
                preview_widget.configure(state='normal')
                preview_widget.delete(1.0, tk.END)  # Limpar o conteúdo anterior
                preview_widget.insert(tk.END, df_original.to_string(index=False))  # Mostrar o conteúdo do DataFrame
                preview_widget.configure(state='disabled')

            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao tentar remover as linhas: {str(e)}")

def main_gui():
    root = tk.Tk()
    root.title("Processador de CSV - Limpeza e Estatísticas")
    root.geometry("800x600")

    label = tk.Label(root, text="Selecione o arquivo CSV:", font=("Arial", 12))
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

    button = tk.Button(root, text="Processar CSV", command=on_process, font=("Arial", 11))
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
