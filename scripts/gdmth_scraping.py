# Import necessary modules
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import mysql.connector
import time
from divisiones import unique_divisions 
from xPaths import idsGDMTH

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Canada123",
    database="tarifas_anuales_cfe"
)
cur = conn.cursor()

# Set up headless Firefox
options = Options()
options.binary_location = 'C:/Users/ZEW4/AppData/Local/Mozilla Firefox/firefox.exe'
options.headless = True
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)
driver.get('https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRENegocio/Tarifas/GranDemandaMTH.aspx')
wait = WebDriverWait(driver, 15)

# List of months to iterate over
months = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

def get_months_from(start_month, all_months):
    if start_month not in all_months:
        print(f"Invalid start month: {start_month}")
        return []
    return all_months[all_months.index(start_month):]

# Function to select an option from a dropdown safely
def safe_select_dropdown_option(dropdown_xpath, option_text):
    retries = 4
    for attempt in range(retries):
        try:
            wait_for_spinner_to_disappear()
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

# Función para extraer las tarifas de energía (Base, Intermedia, Punta)
def extract_tarifas_energia(table):
    tarifas_energia = {}
    try:
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            variable_th = row.find_elements(By.TAG_NAME, "th")
            if len(variable_th) > 0:
                variable = variable_th[0].text.strip()
                tarifa_columns = row.find_elements(By.TAG_NAME, "td")
                if len(tarifa_columns) > 0:
                    tarifa_value = tarifa_columns[-1].text.strip()
                    if "Base" in variable:
                        tarifas_energia['Base'] = tarifa_value
                    elif "Intermedia" in variable:
                        tarifas_energia['Intermedia'] = tarifa_value
                    elif "Punta" in variable:
                        tarifas_energia['Punta'] = tarifa_value

    except Exception as e:
        print(f"Error al extraer tarifas de energía: {e}")
        tarifas_energia = {'Base': 0, 'Intermedia': 0, 'Punta': 0}

    return tarifas_energia

# Función para extraer los cargos de infraestructura (Distribución, Capacidad)
def extract_cargos_infraestructura(table):
    cargos_infraestructura = {}
    try:
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            tarifa_columns = row.find_elements(By.TAG_NAME, "td")
            if len(tarifa_columns) > 2:
                cargo = tarifa_columns[0].text.strip()
                tarifa_value = tarifa_columns[2].text.strip()
                if "Distribución" in cargo:
                    cargos_infraestructura['Distribución'] = tarifa_value
                elif "Capacidad" in cargo:
                    cargos_infraestructura['Capacidad'] = tarifa_value

    except Exception as e:
        print(f"Error al extraer cargos de infraestructura: {e}")
        cargos_infraestructura = {'Distribución': 0, 'Capacidad': 0}

    return cargos_infraestructura

# Función para procesar una tabla
def process_table(table_css, id_region, anio, mes):
    try:
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_css)))

        tarifas_energia = extract_tarifas_energia(table)
        cargos_infraestructura = extract_cargos_infraestructura(table)

        # Insertar tarifas de energía en la tabla 'tarifas' segmentada por año
        cur.execute(f"""
            INSERT INTO tarifas_anuales_cfe.tarifas_gdmth_{anio} (id_region, mes, base, intermedia, punta)
            VALUES (%s, %s, %s, %s, %s)
            """, (
            id_region,
            mes,
            tarifas_energia.get('Base', 0),
            tarifas_energia.get('Intermedia', 0),
            tarifas_energia.get('Punta', 0)
        ))

        # Insertar cargos de infraestructura en la tabla 'infraestructura' segmentada por año
        cur.execute(f"""
            INSERT INTO tarifas_anuales_cfe.infraestructura_gdmth_{anio} (id_region, mes, distribucion, capacidad)
            VALUES (%s, %s, %s, %s)
            """, (
            id_region,
            mes,
            cargos_infraestructura.get('Distribución', 0),
            cargos_infraestructura.get('Capacidad', 0)
        ))

        conn.commit()

    except Exception as e:
        print(f"Error al procesar la tabla {table_css}: {e}")

# Función para verificar la cantidad de tablas disponibles
def get_table_count():
    try:
        tables = driver.find_elements(By.CSS_SELECTOR, "table.table")
        return len(tables)
    except Exception as e:
        print(f"Error al obtener la cantidad de tablas: {e}")
        return 0


# Function to extract and insert tarifas data
def extract_and_insert_data(table_css, id_region, anio, mes):
    try:
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_css)))
        # Implement extraction and insert functions similar to the original code
        # Assume extract_tarifas_energia() and extract_cargos_infraestructura() are defined as before
        tarifas_energia = extract_tarifas_energia(table)
        cargos_infraestructura = extract_cargos_infraestructura(table)

        # Insert data into 'tarifas' and 'infraestructura' tables as before
        cur.execute(f"""
            INSERT INTO tarifas_anuales_cfe.tarifas_gdmth_{anio} (id_region, mes, base, intermedia, punta)
            VALUES (%s, %s, %s, %s, %s)
            """, (
            id_region,
            mes,
            tarifas_energia.get('Base', 0),
            tarifas_energia.get('Intermedia', 0),
            tarifas_energia.get('Punta', 0)
        ))

        cur.execute(f"""
            INSERT INTO tarifas_anuales_cfe.infraestructura_gdmth_{anio} (id_region, mes, distribucion, capacidad)
            VALUES (%s, %s, %s, %s)
            """, (
            id_region,
            mes,
            cargos_infraestructura.get('Distribución', 0),
            cargos_infraestructura.get('Capacidad', 0)
        ))

        conn.commit()
    except Exception as e:
        print(f"Error processing table: {e}")

def scrape_tarifas_data(anio, start_month):

    year_paths = idsGDMTH.get(str(anio))
    if not year_paths:
        print(f"No paths found for the year: {anio}")
        return
    
    # Filter months from start_month to DICIEMBRE
    selected_months = get_months_from(start_month, months)
    if not selected_months:
        print("No months to scrape. Please check the start month.")
        return

    for mes in selected_months:
        safe_select_dropdown_option(f'//*[@id="{year_paths["year"]}"]', str(anio))
        safe_select_dropdown_option(f'//*[@id="{year_paths["month"]}"]', mes)

        for estado, municipios in unique_divisions.items():
            if safe_select_dropdown_option(f'//*[@id="{year_paths["estado"]}"]', estado):
                
                for municipio, divisiones in municipios.items():
                    if safe_select_dropdown_option(f'//*[@id="{year_paths["municipio"]}"]', municipio):
                        
                        for division in divisiones:
                            if safe_select_dropdown_option(f'//*[@id="{year_paths["division"]}"]', division):
                                
                                # Get or create id_region for the current state/municipio/division
                                cur.execute("""
                                    SELECT id_region FROM tarifas_anuales_cfe.region
                                    WHERE estado = %s AND municipio = %s AND division = %s
                                """, (estado, municipio, division))
                                
                                region_row = cur.fetchone()
                                if region_row is None:
                                    cur.execute("""
                                        INSERT INTO tarifas_anuales_cfe.region (estado, municipio, division)
                                        VALUES (%s, %s, %s)
                                    """, (estado, municipio, division))
                                    id_region = cur.lastrowid
                                else:
                                    id_region = region_row[0]

                                # Process and insert data for the table
                                extract_and_insert_data("table.table-bordered:nth-child(2)", id_region, anio, mes)

start_time = time.time()

try:
    anio = 2024  # Set the year you want to scrape
    start_month = 'ENERO'  # Define the start month here
    scrape_tarifas_data(anio, start_month)

finally:
    # Close database and driver connections
    cur.close()
    conn.close()
    driver.quit()
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Tiempo total de ejecución: {execution_time / 3600:.2f} horas.")

#--------------------------------------------------------------------------------------------------------------
# start_time = time.time()
# # Main scraping and insertion process
# try:
#     anio = 2022  # Set the year you want to scrape
    
#     for mes in months:
#         safe_select_dropdown_option('//*[@id="ContentPlaceHolder1_Fecha_ddAnio"]', str(anio))
#         safe_select_dropdown_option('//*[@id="ContentPlaceHolder1_MesVerano3_ddMesConsulta"]', mes)

#         for estado, municipios in unique_divisions.items():
#             if safe_select_dropdown_option('//*[@id="ContentPlaceHolder1_EdoMpoDiv_ddEstado"]', estado):
                
#                 for municipio, divisiones in municipios.items():
#                     if safe_select_dropdown_option('//*[@id="ContentPlaceHolder1_EdoMpoDiv_ddMunicipio"]', municipio):
                        
#                         for division in divisiones:
#                             if safe_select_dropdown_option('//*[@id="ContentPlaceHolder1_EdoMpoDiv_ddDivision"]', division):
                                
#                                 # Get or create id_region for the current state/municipio/division
#                                 cur.execute("""
#                                     SELECT id_region FROM tarifas_anuales_cfe.region
#                                     WHERE estado = %s AND municipio = %s AND division = %s
#                                 """, (estado, municipio, division))
                                
#                                 region_row = cur.fetchone()
#                                 if region_row is None:
#                                     cur.execute("""
#                                         INSERT INTO tarifas_anuales_cfe.region (estado, municipio, division)
#                                         VALUES (%s, %s, %s)
#                                     """, (estado, municipio, division))
#                                     id_region = cur.lastrowid
#                                 else:
#                                     id_region = region_row[0]

#                                 # Process and insert data for the table
#                                 extract_and_insert_data("table.table-bordered:nth-child(2)", id_region, anio, mes)

# finally:
#     # Close database and driver connections
#     cur.close()
#     conn.close()
#     driver.quit()
#     end_time = time.time()

#     execution_time = end_time - start_time

#     print(f"Tiempo total de ejecución para {mes} {anio}: {execution_time/3600:.2f} horas.")
