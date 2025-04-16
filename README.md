# Location Mapper & Analyzer

This project reads latitude and longitude data from a CSV file and plots the coordinates on an interactive map. The coordinates are displayed in blue for easy visualization. The project also supports filtering data by date and time ranges.

- Filter CSV data
- Visualize Maps
- Analyze fuel consumption
- Remove and restructure invalid CSV
- Generate suitable graphics
- Supports all CSV with latitude, longitude, date and time


## Project Structure

```
location-mapper
├── src
│   ├── main.py          # Main interface of the program
│   ├── utils
│   │   ├── data_filter.py    # Filtering and cleaning data
│   │   ├── file_reader.py    # Non-graphical functions for reading CSV files
│   │   ├── gas_study.py      # Analyze fuel consuption and generates a graph
│   │   ├── line_remover.py   # Removes unwanted lines and restructure the CSV to filter it later
│   │   ├── locations_maps.py # Generate a static map and a timelapse map with all locations in the CSV
│   │   ├── stopping_study.py # Analyze stop points and generates a map illustrating them
│   │   └──velocity_study.py # Analyze speed patterns and create an graph and a map with speed records
├── data
│   └── test1.csv          # CSV file containing latitude, longitude, date, and time data
├── maps
│   └── timelapse_map.html # HTML file with map generated from 'locations_map.py'
├── requirements.txt       # List of dependencies
└── README.md              # Project documentation
```

## Requirements

Ensure you have Python installed. Install the required dependencies using pip:

```
pip install -r requirements.txt
```

Dependencies include:

- pandas
- matplotlib
- folium
- datetime
- geopy
- numpy
- tkintermapview
- scikit-learn
- pyproj
- shapely
- geopandas
- seaborn
- openpyxl
- xlsxwriter
- tqdm

## Usage

1. Place your `coordinates.csv` file in the `data` directory. Ensure it contains the following headers: `Latitude`, `Longitude`, `Date`, `Time`.
2. Run the application by executing the `main.py` file:

```
python src/main.py
```

3. The application will:
  - Read the coordinates from the CSV file.
  - Apply any specified filters.
  - Plot the filtered data on an interactive map & create graphs.

## Contributing

Contributions are welcome! Submit issues or pull requests to suggest improvements or report bugs.