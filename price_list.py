import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# URL of the page to scrape
base_url = 'https://www.opel.hu/tools/arlistak-es-katalogusok.html'


# Function to download a file from a given URL
def download_file(url, output_folder):
    local_filename = os.path.join(output_folder, url.split('/')[-1])
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': base_url
    }
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


# Function to fetch and parse the main page
def fetch_main_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')


# Get current month and year for folder naming
now = datetime.now()
month_year_folder = now.strftime("%Y-%m")  # Format: YYYY-MM

# Create the folder with the month-year name if it doesn't exist
output_folder = f'opel_{month_year_folder}'
os.makedirs(output_folder, exist_ok=True)

# Fetch the main page
soup = fetch_main_page(base_url)

# Find all <a> elements with href containing the specific pattern
pdf_links = soup.find_all('a', href=lambda
    href: href and '/content/dam/opel/hungary/brochures/Pricelists/' in href and href.endswith('.pdf'))

# Loop through all found <a> elements and download the PDFs
for link in pdf_links:
    href = link.get('href')
    if href:
        # Construct the full URL if the href is relative
        pdf_url = urljoin(base_url, href)
        try:
            print(f'Downloading {pdf_url}')
            download_file(pdf_url, output_folder)
            print(f'Successfully downloaded {pdf_url}')
        except Exception as e:
            print(f'Failed to download {pdf_url}: {e}')

print('Download complete')



# Base URL of the main page
main_url = 'https://auto.suzuki.hu/modellek'


def clean_text(text):
    """Remove non-breaking spaces and other unwanted characters from the text."""
    return text.replace('\xa0', ' ').strip()


# Function to extract model details and prices
def extract_model_data(model_url):
    try:
        # Fetch the model-specific page
        response = requests.get(model_url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract price list table
        price_list_div = soup.find('div', class_='price-list-table-container')
        table = price_list_div.find('table')

        headers = []
        data = []

        if table:
            # Extract headers
            headers = [clean_text(th.text) for th in table.find_all('tr')[0].find_all('td')]
            # Extract rows
            rows = table.find_all('tr')[1:]  # Skip header row

            for row in rows:
                cols = [clean_text(col.text) for col in row.find_all('td')]
                if len(cols) > 1:  # Ensure row has data
                    data.append(cols)

        return headers, data

    except Exception as e:
        print(f"Failed to extract data from {model_url}: {e}")
        return [], []


# Get current month and year for folder naming
now = datetime.now()
month_year_folder = now.strftime("%Y-%m")  # Format: YYYY-MM

# Create the suzuki folder with the month-year name if it doesn't exist
folder_name = f'suzuki_{month_year_folder}'
os.makedirs(folder_name, exist_ok=True)

# Prepare to write results to a text file
txt_filename = os.path.join(folder_name, 'suzuki_price_list.txt')

# Fetch the main page
response = requests.get(main_url)
response.raise_for_status()  # Check if the request was successful
soup = BeautifulSoup(response.text, 'html.parser')

# Find all model links
model_links = soup.find_all('a', href=True)
model_urls = [urljoin(main_url, link['href']) for link in model_links if 'arlista' in link['href']]

# Set to keep track of processed URLs
processed_urls = set()

# Write to text file
with open(txt_filename, mode='w', encoding='utf-8') as file:
    # Iterate through each model URL and extract data
    for model_url in model_urls:
        if model_url in processed_urls:
            print(f"Skipping already processed URL: {model_url}")
            continue

        try:
            print(f"Processing {model_url}")
            headers, rows = extract_model_data(model_url)
            if headers and rows:  # Only write to file if data extraction was successful
                # Write headers
                file.write(f"{' | '.join(headers)}\n")
                file.write('-' * 80 + '\n')  # Separator line

                # Write data rows
                for row in rows:
                    file.write(f"{' | '.join(row)}\n")

                file.write('\n' + '=' * 80 + '\n')  # End of current model section
                processed_urls.add(model_url)  # Mark this URL as processed
                print(f"Data from {model_url} written to text file")
        except Exception as e:
            print(f"Failed to process {model_url}: {e}")

print(f'Data extraction complete. Results saved to {txt_filename}')



# Base URL of the page to scrape
base_url = 'https://www.nissan.hu/katalogus-arlista.html'

# Get current month and year for folder naming
now = datetime.now()
month_year_folder = now.strftime("%Y-%m")  # Format: YYYY-MM

# Create the folder with the month-year name if it doesn't exist
output_folder = f'nissan_{month_year_folder}'
os.makedirs(output_folder, exist_ok=True)


def download_file(url, output_folder):
    """Download a file from a given URL and save it to the specified folder."""
    local_filename = os.path.join(output_folder, url.split('/')[-1])
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


# Make a request to the website
response = requests.get(base_url)
response.raise_for_status()  # Check if the request was successful

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all <a> elements
links = soup.find_all('a')

# Loop through all <a> elements and check if they link to a PDF in the specified directory
for link in links:
    href = link.get('href')
    if href and href.endswith(
            '.pdf') and 'www-europe.nissan-cdn.net/content/dam/Nissan/hu/brochures/Pricelists/' in href:
        # Complete the URL if href is relative
        if href.startswith('//'):
            href = 'https:' + href
        pdf_url = urljoin(base_url, href)
        try:
            print(f'Downloading {pdf_url}')
            download_file(pdf_url, output_folder)
            print(f'Successfully downloaded {pdf_url}')
        except Exception as e:
            print(f'Failed to download {pdf_url}: {e}')

print('Download complete')


# Base URL of the page to scrape
base_url = 'https://www.kia.com/hu/vasarlas/arlistak-katalogusok-adatok/'

# Get current month and year for folder naming
now = datetime.now()
month_year_folder = now.strftime("%Y-%m")  # Format: YYYY-MM

# Create the folder with the month-year name if it doesn't exist
output_folder = f'kia_{month_year_folder}'
os.makedirs(output_folder, exist_ok=True)


def download_file(url, output_folder):
    """Download a file from a given URL and save it to the specified folder."""
    local_filename = os.path.join(output_folder, url.split('/')[-1])
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


# Make a request to the website
response = requests.get(base_url)
response.raise_for_status()  # Check if the request was successful

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all <a> elements
links = soup.find_all('a')

# Loop through all <a> elements and check if they link to a PDF in the specified directory
for link in links:
    href = link.get('href')
    if href and href.endswith(
            '.pdf') and 'content/dam/kwcms/kme/hu/hu/assets/contents/utility/Brochure/price-list/' in href:
        # Construct the full URL if the href is relative
        pdf_url = urljoin(base_url, href)
        try:
            print(f'Downloading {pdf_url}')
            download_file(pdf_url, output_folder)
            print(f'Successfully downloaded {pdf_url}')
        except Exception as e:
            print(f'Failed to download {pdf_url}: {e}')

print('Download complete')



# URL of the page to scrape
url = 'https://www.dacia.hu/arlista-letoltes.html'

# Get current month and year for folder naming
now = datetime.now()
month_year_folder = now.strftime("%Y-%m")  # Format: YYYY-MM

# Create the folder with the month-year name if it doesn't exist
output_folder = f'dacia_{month_year_folder}'
os.makedirs(output_folder, exist_ok=True)


def download_file(url, folder):
    """Download a file from a given URL and save it to the specified folder."""
    local_filename = os.path.join(folder, url.split('/')[-1])
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


# Make a request to the website
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the specified <div> elements
divs = soup.find_all('div', class_='col-xs-12 col-sm-6 col-sm-6--clear-third col-md-4')

pdf_links = []

# Loop through each <div> and find the <a> element with href ending in 'price.pdf'
for div in divs:
    a_tag = div.find('a', href=True)
    if a_tag and 'price.pdf' in a_tag['href']:
        pdf_url = urljoin(url, a_tag['href'])
        pdf_links.append(pdf_url)

# Download the PDFs found
if pdf_links:
    for pdf_link in pdf_links:
        try:
            print(f"Downloading {pdf_link}")
            download_file(pdf_link, output_folder)
            print(f"Successfully downloaded {pdf_link}")
        except Exception as e:
            print(f"Failed to download {pdf_link}: {e}")
else:
    print("No PDF links found ending with 'price.pdf'.")

print('Download complete.')


# URL of the page to scrape
url = 'https://byd-wallismotor.hu/arlista/'

# Get current month and year for folder naming
now = datetime.now()
month_year_folder = now.strftime("%Y-%m")  # Format: YYYY-MM

# Create the folder with the month-year name if it doesn't exist
output_folder = f'byd_{month_year_folder}'
os.makedirs(output_folder, exist_ok=True)


def download_pdf(pdf_url, folder):
    """Download a PDF file from the URL and save it to the specified folder."""
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()  # Check if the request was successful

        # Extract filename from the URL
        filename = os.path.basename(pdf_url)
        filepath = os.path.join(folder, filename)

        # Write the PDF content to a file
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {filepath}")
    except Exception as e:
        print(f"Failed to download {pdf_url}: {e}")


# Make a request to the website
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find the section with class "pricelist"
pricelist_section = soup.find('section', class_='pricelist')

if pricelist_section:
    # Find all <a> elements in the pricelist section
    links = pricelist_section.find_all('a', href=True)

    for link in links:
        href = link['href']
        # Check if the href contains '/uploads' and ends with '.pdf'
        if '/uploads' in href and href.endswith('.pdf'):
            # Construct the full URL of the PDF
            pdf_url = urljoin(url, href)
            print(f"PDF found: {pdf_url}")
            # Download the PDF
            download_pdf(pdf_url, output_folder)
else:
    print('No pricelist section found.')

print('Scraping complete.')


# Base URL of the main page
main_url = 'https://hyundai.hu/modellek/'

# Get current month and year for folder naming
now = datetime.now()
month_year_folder = now.strftime("%Y-%m")  # Format: YYYY-MM

# Create the folder with the month-year name if it doesn't exist
output_folder = f'hyundai_{month_year_folder}'
os.makedirs(output_folder, exist_ok=True)


def clean_text(text):
    """Remove non-breaking spaces and other unwanted characters from the text."""
    return text.replace('\xa0', ' ').strip()


def extract_filename_from_url(url):
    """Extract filename from URL based on the specified pattern."""
    match = re.search(r'/docs/([^/]+)', url)
    if match:
        filename = match.group(1)
        if '?dokumentum' in filename:
            filename = filename.split('?')[0]
        return f"{filename}.pdf"
    return 'unknown.pdf'


def download_pdf(pdf_url, folder):
    """Download a file from a given URL and save it to the specified folder."""
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()  # Check if the request was successful

        # Generate filename based on the URL
        filename = extract_filename_from_url(pdf_url)
        filepath = os.path.join(folder, filename)

        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {filepath}")
    except Exception as e:
        print(f"Failed to download {pdf_url}: {e}")


def fetch_and_process_model_page(model_url):
    response = requests.get(model_url)
    response.raise_for_status()  # Check if the request was successful
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find links that contain '?menu=arlista-katalogus' or '?menu=letoltesek'
    links = soup.find_all('a', href=True)
    relevant_links = [urljoin(model_url, a['href']) for a in links if
                      any(menu in a['href'] for menu in
                          ['?menu=arlista-katalogus', '?menu=letoltesek', '?menu=arlistakatalogus'])]

    # Process each relevant link in parallel
    with ThreadPoolExecutor() as executor:
        futures = []
        for link in relevant_links:
            future = executor.submit(process_link_for_pdfs, link)
            futures.append(future)
        for future in as_completed(futures):
            future.result()


def process_link_for_pdfs(link):
    response = requests.get(link)
    response.raise_for_status()  # Check if the request was successful
    linked_soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <a> tags with href containing 'dokumentum=arlista'
    pdf_links = linked_soup.find_all('a', href=lambda x: x and 'dokumentum=arlista' in x)
    with ThreadPoolExecutor() as executor:
        futures = []
        for pdf_link in pdf_links:
            pdf_href = pdf_link['href']
            pdf_url = urljoin(main_url, pdf_href)
            future = executor.submit(download_pdf, pdf_url, output_folder)
            futures.append(future)
        for future in as_completed(futures):
            future.result()


def fetch_main_page_and_process_models():
    response = requests.get(main_url)
    response.raise_for_status()  # Check if the request was successful
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the specific div with class 'rows large-container-padding'
    rows_div = soup.find('div', class_='rows large-container-padding')

    # Find all the divs with class 'row' within the 'rows' div
    row_divs = rows_div.find_all('div', class_='row')

    # Process each row div to find the initial model links
    with ThreadPoolExecutor() as executor:
        futures = []
        for row_div in row_divs:
            a_tags = row_div.find_all('a', href=True)
            for a_tag in a_tags:
                href = a_tag['href']
                if 'modellek' in href:
                    full_url = urljoin(main_url, href)
                    future = executor.submit(fetch_and_process_model_page, full_url)
                    futures.append(future)
        for future in as_completed(futures):
            future.result()


fetch_main_page_and_process_models()
print('PDF download complete')
