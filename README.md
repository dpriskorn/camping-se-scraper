# Camping.se Scraper
Note: this is an attempt to create open data for Swedish camping sites

This project is an asynchronous scraper for gathering camping site data from [camping.se](https://camping.se). It fetches information about different camping sites, such as their name, coordinates, and favorite node ID, and exports the data to a GeoJSON file. The purpose is to do quality control in Wikidata and OpenStreetMap.

## Features

- Asynchronous fetching of camping site pages using `aiohttp`
- Extraction of site information such as name, coordinates, and Drupal ID
- Exporting site data to a GeoJSON file
- Usage of `tqdm` to display progress

## Requirements

- Python 3.8+
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/camping-site-scraper.git
   cd camping-site-scraper
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Usage

Run the scraper with the following command:

```bash
poetry run python main.py
```

The scraper will start fetching data and export the results to `camping_sites.geojson`.

## Exported Data

The exported data contains the following fields:
- `drupal_id`: Drupal ID of the camping site
- `name`: Name of the camping site
- `website`: Generated URL of the site
- Coordinates (`lat` and `long`) are stored in the GeoJSON geometry.

## Development

If you want to contribute to this project or modify it, install the dev dependencies:

```bash
poetry install --with dev
```