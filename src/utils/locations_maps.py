import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import folium
from folium.plugins import TimestampedGeoJson
from file_reader import read_coordinates
import webbrowser  # Importando para abrir o arquivo no navegador

def create_timelapse(coordinates, timestamps, output_file='maps/timelapse_map.html'):
    if not coordinates or not timestamps:
        messagebox.showwarning("Aviso", "Nenhum dado disponível para criar o timelapse.")
        return

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

    # Abrir o arquivo gerado no navegador
    webbrowser.open(f"file://{os.path.abspath(output_file)}")  # Abre no navegador

def create_static_map(coordinates, output_file='maps/location_map.html'):
    if not coordinates:
        messagebox.showwarning("Aviso", "Nenhuma coordenada disponível para o mapa.")
        return

    avg_lat = sum(lat for lat, _ in coordinates) / len(coordinates)
    avg_lon = sum(lon for _, lon in coordinates) / len(coordinates)

    os.makedirs("maps", exist_ok=True)

    map_ = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
    for lat, lon in coordinates:
        folium.CircleMarker(location=[lat, lon], radius=5, color='blue').add_to(map_)

    map_.save(output_file)

    # Abrir o arquivo gerado no navegador
    webbrowser.open(f"file://{os.path.abspath(output_file)}")  # Abre no navegador

def run_mapping():
    file_path = selected_file.get()
    if not file_path:
        messagebox.showerror("Erro", "Nenhum arquivo selecionado.")
        return

    try:
        coordinates, timestamps = read_coordinates(file_path, include_timestamps=True)
        if not coordinates:
            messagebox.showwarning("Aviso", "Nenhuma coordenada foi lida.")
            return

        create_static_map(coordinates)  # Criar o mapa estático
        create_timelapse(coordinates, timestamps)  # Criar o timelapse
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar o arquivo:\n{str(e)}")

def browse_file():
    filename = filedialog.askopenfilename(
        title="Escolha um arquivo CSV",
        filetypes=[("CSV files", "*.csv")],
        initialdir="data"
    )
    if filename:
        selected_file.set(filename)

# GUI Setup
root = tk.Tk()
root.title("Gerador de Mapas com Folium")
root.geometry("500x200")

frame = ttk.Frame(root, padding=20)
frame.pack(fill=tk.BOTH, expand=True)

selected_file = tk.StringVar()

ttk.Label(frame, text="Arquivo CSV:").grid(row=0, column=0, sticky="w")
ttk.Entry(frame, textvariable=selected_file, width=50).grid(row=0, column=1)
ttk.Button(frame, text="Procurar", command=browse_file).grid(row=0, column=2, padx=5)

ttk.Button(frame, text="Gerar Mapas", command=run_mapping).grid(row=1, column=1, pady=20)

root.mainloop()
