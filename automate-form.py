from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fuzzywuzzy import process
import time
import csv

# Credentials and URLs
login_url = 'https://www.3dhc.it/gestione/index.html'  # The login page URL
target_url = 'https://www.3dhc.it/gestione/piloti.html'  # The URL of the page with the form
username = 'admin'  # Your login username
password = 'Gianluca@2022'  # Your login password
csv_filename = '3dhc.csv'   # Your CSV file

# Function to read data from CSV
def read_csv_data(csv_filename):
    data = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

# Function to automate login and typing into the webpage
def automate_typing_with_login(csv_filename, login_url, target_url, username, password):
    
    ## All of this just to avoid the default search engine prompt
    # Create an instance of Chrome options
    chrome_options = Options()
    # Use a new user profile to avoid default search engine prompt
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-profile")
    # Disable the default browser check and suppress first-run popups
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    # Set preferences to suppress the search engine popup and others
    chrome_prefs = {
        "profile.default_content_setting_values.notifications": 2,  # Block notifications
        "profile.password_manager_enabled": False,
        "credentials_enable_service": False,
        "browser.default_browser_infobar": False
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)

    ## Initialize WebDriver with the configured options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    ## Step 1: Open the login page
    driver.get(login_url)
    time.sleep(1)  # Wait for the page to load

    ## Step 2: Find and fill the login form (adjust the field names as per the website)
    username_field = driver.find_element(By.NAME, 'username')  # Change 'username' to the actual name attribute
    password_field = driver.find_element(By.NAME, 'password')  # Change 'password' to the actual name attribute
    
    username_field.send_keys(username)  # Input the username
    password_field.send_keys(password)  # Input the password

    ## Step 3: Submit the login form (usually by clicking a login button)
    login_button = driver.find_element(By.ID, 'btaccedi')  # Change 'login' to the actual name of the login button
    login_button.click()

    time.sleep(1)  # Wait for login to complete and page to load

    ## Step 4: Navigate to the target page after login
    driver.get(target_url)
    time.sleep(1)  # Wait for the target page to load

    ## Step 5: Read data from the CSV file
    csv_data = read_csv_data(csv_filename)

    ## Step 6: Automate typing CSV data into the fields
    for row in csv_data:
        add_pilot_button = driver.find_element(By.ID, 'btnuovo')  # Change 'login' to the actual name of the login button
        add_pilot_button.click()
        time.sleep(1)  # Wait for the target page to load

        # Find the form fields (change selectors as per the webpage)
        cognome_field = driver.find_element(By.ID, 'cognome')  # Change 'name' to the actual field name
        nome_field = driver.find_element(By.ID, 'nome')    # Change 'age' to the actual field name
        categoria_field = driver.find_element(By.ID, 'nazionenascita')  # Change 'occupation'
        sponsor_field = driver.find_element(By.ID, 'luogonascita')
        telefono_field = driver.find_element(By.ID, 'telefono')
        email_field = driver.find_element(By.ID, 'email')
        email_field = driver.find_element(By.ID, 'email')

        # Clear any existing text in the fields
        cognome_field.clear()
        nome_field.clear()
        categoria_field.clear()

        # Simulate typing the data from the CSV
        cognome_field.send_keys(row['Last Name - Cognome'])
        nome_field.send_keys(row['First Name - Nome'])
        sponsor_field.send_keys(row['Sponsors'])
        telefono_field.send_keys('+390000000000')
        email_field.send_keys('a@a.it')
        nazionalita_element = driver.find_element(By.ID, 'nazionalita')  # Replace with the actual dropdown ID
        attivo_element = driver.find_element(By.ID, 'attivo')  # Replace with the actual dropdown ID

        # Categoria
        categoria = row['Competition - Competizione']
        if "Advanced" in categoria:
            categoria_to_write = "Advanced"
        elif "Sport" in categoria:
            categoria_to_write = "Sport"
        else:
            categoria_to_write = "Funfly"
        categoria_field.send_keys(categoria_to_write)

        # Nazionalità
        # Locate the dropdown element (by ID in this example)
        # Create a Select object to interact with the dropdown
        nazionalita = Select(nazionalita_element)
        # Get all options in the dropdown
        all_options = [option.text for option in nazionalita.options]
        # String to match
        desired_string = row['Country - Nazionalità']  # The string you want to find the most similar option to
        # Find the closest match using fuzzywuzzy
        best_match, match_score = process.extractOne(desired_string, all_options)
        # Select the best matching option by visible text
        nazionalita.select_by_visible_text(best_match)

        # Attivo
        attivo = Select(attivo_element)
        attivo.select_by_value('0')

        # You can press a button if needed to submit the form (uncomment if necessary)
        submit_button = driver.find_element(By.ID, 'btsalva')  # Change 'submit' to the actual button name
        submit_button.click()
        time.sleep(1)

        # Find the "OK" button within the modal dialog
        ok_button = driver.find_element(By.XPATH, '//div[@id="messagebox"]//button[text()="Ok"]')
        ok_button.click()
        time.sleep(1)  # Small delay between form submissions

    # Close the browser after the process is done
    driver.quit()



data = read_csv_data(csv_filename)
data0 = data[0]
data00 = data[0]['First Name - Nome']

# Call the function to automate login and typing
automate_typing_with_login(csv_filename, login_url, target_url, username, password)
