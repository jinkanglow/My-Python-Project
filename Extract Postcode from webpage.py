import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time 
import csv
import pandas as pd 
import keyboard

main_url = "https://postcode.my"

# Function to check for CAPTCHA
def check_for_captcha(soup):
    captcha_elements = soup.find_all(text="Validate that you are indeed a human being by solving the following CAPTCHA")
    if captcha_elements:
        return True
    return False

# Function to handle CAPTCHA
def handle_captcha():
    print("CAPTCHA detected. Please handle manually.Press 'Enter' to continue...")
    while True:
        if keyboard.read_event().name == 'enter':
            break
        time.sleep(10)


# Function to get the URLs for each area
def extract_area_urls(main_url):
    while True:
        try:
            response = requests.get(main_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            if check_for_captcha(soup):
                handle_captcha()
                continue  # Retry the request after CAPTCHA is solved
        
            # Extract area URLs from <h4 class="media-heading"> elements
            areas = soup.find_all('h4', class_='media-heading')

            area_urls = []
            for area in areas:
                area_url = urljoin(main_url, area.find('a')['href'])
                area_urls.append(area_url)
            
            return area_urls
        
        except requests.exceptions.RequestException as e:
                print(f"Error fetching main URL: {e}")
                time.sleep(0.5)


# Function to get the URLs for each post office in an area
def extract_post_office_urls(area_url):
    while True:
        try:
            response = requests.get(area_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            if check_for_captcha(soup):
                handle_captcha()
                continue  # Retry the request after CAPTCHA is solved
            
            post_offices = soup.find_all('a', class_='pull-left')

            post_office_urls = []
            for post_office in post_offices:
                # Check if 'a' tag exists within post_office
                if post_office.has_attr('href'):
                    post_office_url = urljoin(main_url, post_office['href'])
                    post_office_urls.append(post_office_url)
                    time.sleep(0.5)
            
            return post_office_urls
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching area URL {area_url}: {e}")
            time.sleep(0.5)


# Function to get data from a single page
def extract_data_from_page(post_office_url):
    all_data = []
    page_number = 1
    
    while True:
        # Construct the URL for the current page
        if page_number > 1:
            page_url = f"{post_office_url}?page={page_number}"
        else:
            page_url = post_office_url
            
        print(f"Fetching data from: {page_url}")  # Debugging: Print current page_url

        try:
            response = requests.get(page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            if check_for_captcha(soup):
                handle_captcha()
                continue  # Retry the request after CAPTCHA is solved
            
            table = soup.find('table', id='t2')

            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if cols:
                        location = cols[0].text.strip()
                        post_office = cols[1].text.strip()
                        state = cols[2].text.strip()
                        postcode = cols[3].text.strip()
                        all_data.append({
                            'Location': location,
                            'Post Office': post_office,
                            'State': state,
                            'Postcode': postcode
                        })

                        time.sleep(5)

            # Check if there is a next page
            next_page_link = soup.find('li', class_='hidden-xs active').find_next_sibling('li')
            if next_page_link is None or 'disabled' in next_page_link.get('class', []):
                break
            
            page_number += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_url}: {e}")
            time.sleep(0.5)
        except AttributeError as ae:
            print(f"AttributeError: {ae}")
            time.sleep(0.5)

    return all_data

# Function to save data as Excel CSV
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    download_path = ""  # Adjust path as per your system
    file_path = fr"{download_path}\{filename}.csv"
    df.to_csv(file_path, index=False, header=True)
    print(f"Data saved to {download_path}")

if __name__ == "__main__":
    area_urls = extract_area_urls(main_url)
    if not area_urls:
        print("No area URLs found or CAPTCHA detected. Please check manually.")
    else:
        for area_url in area_urls:
            post_office_urls = extract_post_office_urls(area_url)
            if not post_office_urls:
                print(f"No post office URLs found for area: {area_url} or CAPTCHA detected. Please check manually.")
                continue

            all_data = []
            for post_office_url in post_office_urls:
                data = extract_data_from_page(post_office_url)
                if not data:
                    print(f"No data extracted from: {post_office_url} or CAPTCHA detected. Please check manually.")
                    continue
                all_data.extend(data)

            if all_data:
                save_to_csv(all_data, "postcode_data")


