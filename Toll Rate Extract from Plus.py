from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Set up the Selenium WebDriver (using Chrome in this example)
# download from this url: https://getwebdriver.com/chromedriver#stable
driver_path = '' # replace the actual path  
url = "https://www.plus.com.my/"

# Initialize the WebDriver
driver = webdriver.Chrome(executable_path=driver_path)

# Navigate to the URL
driver.get(url)

# Wait for the page to load
time.sleep(3)

# Locate the 'From' and 'To' select elements
from_select_element = Select(driver.find_element_by_id('locFrom'))
to_select_element = Select(driver.find_element_by_id('locTo'))


# Debugging
# from_options = [option.get_attribute('value') for option in from_select_element.options if option.get_attribute('value').startswith('A')]
# to_options = [option.get_attribute('value') for option in to_select_element.options if option.get_attribute('value').startswith('A')]

# Extract options from both 'From' and 'To' dropdowns
from_options = [option.get_attribute('value') for option in from_select_element.options if option.get_attribute('value')]
to_options = [option.get_attribute('value') for option in to_select_element.options if option.get_attribute('value')]

# Dictionary to store toll rates
all_toll_rates = {}
toll_rates_list = []

# Loop through each combination of 'From' and 'To' options
for from_value in from_options:
    all_toll_rates[from_value] = {}
    for to_value in to_options:
        if from_value != to_value:
            # Select the 'From' value
            from_select_element.select_by_value(from_value)
            time.sleep(1)  # Add a short delay for the selection to register

            # Select the 'To' value
            to_select_element.select_by_value(to_value)
            time.sleep(1)  # Add a short delay for the selection to register

            # Scroll the button into view and use JavaScript to click it
            get_result_button = driver.find_element_by_id('myBtn')
            driver.execute_script("arguments[0].scrollIntoView(true);", get_result_button)
            driver.execute_script("arguments[0].click();", get_result_button)

            # Wait for the modal to appear
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'modal-content'))
            )

            # Get the page source and parse with BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract data from the modal popup
            journey_details = soup.find('div', {'class': 'modal-content'})
            from_location = journey_details.find('div', {'id': 'demoFrom'}).text.strip()
            to_location = journey_details.find('div', {'id': 'demoTo'}).text.strip()
            toll_rates = {'From': from_location, 'To': to_location}


            # Extract toll rates for each vehicle class
            for i in range(1, 6):
                class_id = f'demo{i}'
                rate_element = journey_details.find('div', {'id': class_id})
                if rate_element:
                    rate_text = rate_element.text.strip()
                    if rate_text:
                        rate = float(rate_text)
                        toll_rates[f'Class {i}'] = rate
                    else:
                        toll_rates[f'Class {i}'] = None
            
            

            # Add toll rates to the list
            toll_rates_list.append(toll_rates)

# Close the WebDriver
driver.quit()

# Create a DataFrame from the list of toll rates
df = pd.DataFrame(toll_rates_list)

# Define the order of the columns
columns_order = ['From', 'To', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5']
df = df[columns_order]

# Write the DataFrame to an Excel file
excel_file_path = '' # replace the actual path
df.to_excel(excel_file_path, index=False)

print(f"Toll rates have been successfully written to {excel_file_path}")