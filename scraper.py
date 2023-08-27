import requests
from bs4 import BeautifulSoup
import pandas as pd

# Wikipedia URL for the list of brightest stars and other record stars
BRIGHT_STARS_URL = "https://en.wikipedia.org/wiki/List_of_brightest_stars_and_other_record_stars"
BROWN_DWARFS_URL = "https://en.wikipedia.org/wiki/List_of_brown_dwarfs"

# Send an HTTP GET request to fetch the HTML content of the page
response = requests.get(BRIGHT_STARS_URL)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find the table with class="wikitable sortable"
table = soup.find("table", class_="wikitable sortable")

# Initialize the list to store scraped data
scraped_data = []

# Define scrape() method to scrape all column data
def scrape():
    for row in table.find_all("tr")[1:]:
        columns = row.find_all("td")

        # Extracting data from columns
        v_mag = columns[0].text.strip()
        proper_name = columns[1].text.strip()
        bayer_designation = columns[2].text.strip()
        distance_ly = columns[3].text.strip()
        spectral_class = columns[4].text.strip()

        # Append the data to the list scraped_data
        scraped_data.append([v_mag, proper_name, bayer_designation, distance_ly, spectral_class])

# Call the scrape() method to fetch the data
scrape()

# Create a DataFrame from the scraped data
headers = ["V Mag. (mV)", "Proper name", "Bayer designation", "Distance (ly)", "Spectral class"]
stars_df = pd.DataFrame(scraped_data, columns=headers)

# Export DataFrame to CSV
stars_df.to_csv("brightest_stars_data.csv", index=False)

# Now let's proceed with scraping and processing brown dwarfs data

# Send an HTTP GET request to fetch the HTML content of the page
response = requests.get(BROWN_DWARFS_URL)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find the 3rd table on the page (index 2) using class name "wikitable"
table = soup.find_all("table", class_="wikitable")[2]

# Find all rows in the table
rows = table.find_all("tr")

# Initialize an empty list to store the data
data = []

# Extract data from each row
for row in rows[1:]:  # Skip the header row
    columns = row.find_all("td")
    row_data = [column.get_text(strip=True) for column in columns]
    data.append(row_data)

# Define header names for brown dwarfs data
headers = ["Brown dwarf", "Constellation", "Right ascension", "Declination", "App. mag.", "Distance (ly)", "Spectral Type", "Mass (MJ)", "Radius (RJ)", "Discovery Year"]

# Create a DataFrame from the extracted data
brown_dwarfs_df = pd.DataFrame(data, columns=headers)

# Export DataFrame to a new CSV file (original, unmodified data)
brown_dwarfs_df.to_csv("original_brown_dwarfs_data.csv", index=False)

# Clean the data by dropping rows with "n/a" values
brown_dwarfs_df = brown_dwarfs_df.replace("n/a", pd.NA).dropna()

# Convert Mass and Radius columns to floating point values
brown_dwarfs_df["Mass (MJ)"] = pd.to_numeric(brown_dwarfs_df["Mass (MJ)"], errors='coerce') * 0.000954588
brown_dwarfs_df["Radius (RJ)"] = pd.to_numeric(brown_dwarfs_df["Radius (RJ)"], errors='coerce') * 0.102763

# Drop rows with NaN values
brown_dwarfs_df = brown_dwarfs_df.dropna()

# Export DataFrame to a new CSV file (cleaned data)
brown_dwarfs_df.to_csv("cleaned_brown_dwarfs_data.csv", index=False)

# Load the "brightest_stars_data.csv" file
brightest_stars_df = pd.read_csv("brightest_stars_data.csv")

# Merge the two DataFrames based on common columns
merged_df = pd.merge(brightest_stars_df, brown_dwarfs_df, how="outer")

# Sort the merged DataFrame by values
sorted_df = merged_df.sort_values(by="Mass (MJ)", ascending=False)

# Export the merged and sorted DataFrame to a new CSV file
sorted_df.to_csv("merged_stars_data.csv", index=False)
