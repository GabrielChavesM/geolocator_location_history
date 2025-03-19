# Location Mapper

This project is designed to read latitude and longitude data from a CSV file and plot the coordinates on a map. The coordinates are displayed in blue for easy visualization. Additionally, the project now supports filtering data by date and time ranges.

## Project Structure

```
location-mapper
├── src
│   ├── main.py          # Entry point of the application
│   ├── utils
│   │   ├── file_reader.py    # Utility functions for reading CSV files
│   │   └── data_filter.py    # Utility functions for filtering and cleaning data by date and time
├── data
│   └── coordinates.csv   # CSV file containing latitude and longitude data
├── requirements.txt      # List of dependencies
└── README.md             # Project documentation
```

## Requirements

To run this project, you need to install the following dependencies:

- pandas
- matplotlib
- folium
- datetime

You can install the required packages using pip:

```
pip install -r requirements.txt
```

## Usage

1. Place your `coordinates.csv` file in the `data` directory. Ensure it has the following headers: `Latitude`, `Longitude`, `Date`, `Time`.
2. Run the application by executing the `main.py` file:

```
python src/main.py
```

3. The application will read the coordinates from the CSV file, apply any specified filters, and plot the filtered data on a map.

### Filtering Data

You can now filter the data by specifying a date and time range in the `main.py` file. Update the `start_date`, `end_date`, `start_time`, and `end_time` variables to apply the desired filters.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the project.