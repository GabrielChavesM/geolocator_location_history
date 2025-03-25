# Location Mapper

This project reads latitude and longitude data from a CSV file and plots the coordinates on an interactive map. The coordinates are displayed in blue for easy visualization. The project also supports filtering data by date and time ranges.

## Project Structure

```
location-mapper
├── src
│   ├── main.py          # Entry point of the application
│   ├── utils
│   │   ├── file_reader.py    # Functions for reading CSV files
│   │   └── data_filter.py    # Functions for filtering and cleaning data by date and time
├── data
│   └── coordinates.csv   # CSV file containing latitude, longitude, date, and time data
├── requirements.txt      # List of dependencies
└── README.md             # Project documentation
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

## Usage

1. Place your `coordinates.csv` file in the `data` directory. Ensure it contains the following headers: `Latitude`, `Longitude`, `Date`, `Time`.
2. Run the application by executing the `main.py` file:

```
python src/main.py
```

3. The application will:
  - Read the coordinates from the CSV file.
  - Apply any specified filters.
  - Plot the filtered data on an interactive map.

### Filtering Data

To filter data, update the following variables in `main.py`:

- `start_date` and `end_date` for date range.
- `start_time` and `end_time` for time range.

The application will only plot data within the specified ranges.

## Contributing

Contributions are welcome! Submit issues or pull requests to suggest improvements or report bugs.