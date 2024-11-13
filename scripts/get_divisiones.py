import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
from collections import defaultdict

# headless firefox
options = Options()
options.binary_location = 'C:/Users/ZEW4/AppData/Local/Mozilla Firefox/firefox.exe'
options.headless = True
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)
driver.get('https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRENegocio/Tarifas/GranDemandaMTH.aspx')
wait = WebDriverWait(driver, 15)

months = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

# Dictionary to store all municipios and divisions by state
state_municipios_divisions = defaultdict(dict)

# Function to get options from dropdown, excluding default options
def safe_get_dropdown_options(dropdown_xpath):
    retries = 4
    for attempt in range(retries):
        try:
            dropdown_element = wait.until(EC.presence_of_element_located((By.XPATH, dropdown_xpath)))
            dropdown = Select(dropdown_element)
            return [option.text for option in dropdown.options if not option.text.startswith("--") and option.text != '---Selecciona---']
        except selenium.common.exceptions.StaleElementReferenceException:
            time.sleep(2)
            if attempt == retries - 1:
                return []

# Function to select option from dropdown and wait for changes to take effect
def safe_select_dropdown_option(dropdown_xpath, option_text):
    retries = 4
    for attempt in range(retries):
        try:
            wait_for_spinner_to_disappear()  # Wait for spinner to disappear before attempting to click
            dropdown_element = wait.until(EC.presence_of_element_located((By.XPATH, dropdown_xpath)))
            dropdown = Select(dropdown_element)
            dropdown.select_by_visible_text(option_text)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", dropdown_element)
            time.sleep(2)
            return True
        except (selenium.common.exceptions.StaleElementReferenceException, selenium.common.exceptions.NoSuchElementException, selenium.common.exceptions.ElementClickInterceptedException):
            time.sleep(2)
            if attempt == retries - 1:
                print(f"Could not locate element with visible text: {option_text}")
                return False

# Function to wait for spinner to disappear
def wait_for_spinner_to_disappear():
    try:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".css3-spinner")))
    except selenium.common.exceptions.TimeoutException:
        print("Timeout waiting for spinner to disappear.")

# Main scraping logic
try:
    # Set fixed year and month
    anio = 2021
    mes = 'OCTUBRE'
    
    # Select the year and month in dropdowns
    safe_select_dropdown_option('//*[@id="ContentPlaceHolder1_Fecha_ddAnio"]', str(anio))
    safe_select_dropdown_option('//*[@id="ContentPlaceHolder1_MesVerano3_ddMesConsulta"]', mes)

    # Select state and process each municipio
    estado_dropdown_xpath = '//*[@id="ContentPlaceHolder1_EdoMpoDiv_ddEstado"]'
    estados = safe_get_dropdown_options(estado_dropdown_xpath)

    if estados:
        for estado in estados:
            if safe_select_dropdown_option(estado_dropdown_xpath, estado):
                # Get municipios for the state
                municipio_dropdown_xpath = '//*[@id="ContentPlaceHolder1_EdoMpoDiv_ddMunicipio"]'
                municipios = safe_get_dropdown_options(municipio_dropdown_xpath)

                if municipios:
                    for municipio in municipios:
                        if safe_select_dropdown_option(municipio_dropdown_xpath, municipio):
                            # Get divisions for the current municipio
                            division_dropdown_xpath = '//*[@id="ContentPlaceHolder1_EdoMpoDiv_ddDivision"]'
                            divisiones = safe_get_dropdown_options(division_dropdown_xpath)

                            # Store the municipio and its divisions in the dictionary
                            state_municipios_divisions[estado][municipio] = divisiones
                            print(f"State: {estado}, Municipio: {municipio}, Divisions: {divisiones}")

finally:
    # Close driver after processing
    driver.quit()

# Function to filter municipios with unique divisions
def filter_unique_divisions(state_municipios_divisions):
    unique_divisions_by_state = {}
    
    for estado, municipios in state_municipios_divisions.items():
        # Count occurrences of each division configuration in municipios
        division_counts = defaultdict(int)
        for municipio, divisiones in municipios.items():
            division_counts[tuple(divisiones)] += 1
        
        # Find the most common division configuration
        if division_counts:
            most_common_division = max(division_counts, key=division_counts.get)

            # Filter municipios with divisions different from the most common configuration
            unique_divisions_by_state[estado] = {
                municipio: divisiones for municipio, divisiones in municipios.items()
                if tuple(divisiones) != most_common_division
            }

    return unique_divisions_by_state

# Run the filtering function to get municipios with unique divisions
unique_divisions = filter_unique_divisions(state_municipios_divisions)

# Output the unique divisions dictionary
print(unique_divisions)