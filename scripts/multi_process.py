from concurrent.futures import ThreadPoolExecutor
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
import mysql.connector
import time

# Conexión a la base de datos MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="PoTtEr15396!",
    database="tarifas_anuales"
)

cur = conn.cursor()

# Configuramos el driver para Firefox
service = Service(GeckoDriverManager().install())
options = webdriver.FirefoxOptions()
options.headless = True  # Ejecutar en modo headless
driver = webdriver.Firefox(service=service, options=options)

wait = WebDriverWait(driver, 30)

driver.get('https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRENegocio/Tarifas/GranDemandaMTH.aspx')

# Función para obtener las opciones del dropdown, excluyendo las opciones predeterminadas y '---Selecciona---'
def safe_get_dropdown_options(dropdown_xpath):
    retries = 3
    for attempt in range(retries):
        try:
            dropdown_element = wait.until(EC.presence_of_element_located((By.XPATH, dropdown_xpath)))
            dropdown = Select(dropdown_element)
            # Excluir opciones que empiezan con "--" o que son '---Selecciona---'
            return [option.text for option in dropdown.options if not option.text.startswith("--") and option.text != '---Selecciona---']
        except selenium.common.exceptions.StaleElementReferenceException:
            time.sleep(2)
            if attempt == retries - 1:
                return []

def wait_for_spinner_to_disappear():
    try:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".css3-spinner")))
    except Exception as e:
        print(f"Error al esperar que el spinner desaparezca: {e}")

# Función para seleccionar un dropdown con tiempo de espera, evitando '---Selecciona---'
def safe_select_dropdown_option(dropdown_xpath, option_text):
    retries = 3
    for attempt in range(retries):
        try:
            # Espera a que el spinner desaparezca
            wait_for_spinner_to_disappear()
            
            if option_text != '---Selecciona---':  # Evitar seleccionar esta opción explícitamente
                dropdown_element = wait.until(EC.presence_of_element_located((By.XPATH, dropdown_xpath)))
                dropdown = Select(dropdown_element)
                dropdown.select_by_visible_text(option_text)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", dropdown_element)
                time.sleep(3)
                return True
        except selenium.common.exceptions.StaleElementReferenceException:
            time.sleep(2)
            if attempt == retries - 1:
                return False

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
            INSERT INTO tarifas_anuales.tarifas_{anio} (id_region, mes, base, intermedia, punta)
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
            INSERT INTO tarifas_anuales.infraestructura_{anio} (id_region, mes, distribucion, capacidad)
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

# Proceso de scraping para un municipio en Aguascalientes
def process_municipio(municipio):
    anio = 2021
    mes = 'ABRIL'  # Cambiado para trabajar en abril

    estado = 'AGUASCALIENTES'  # Estado fijo para este proceso

    try:
        # Selección del estado
        safe_select_dropdown_option('//*[@id="ContentPlaceHolder1_EdoMpoDiv_ddEstado"]', estado)

        # Selección del municipio
        municipio_dropdown_xpath = '//*[@id="ContentPlaceHolder1_EdoMpoDiv_ddMunicipio"]'
        if safe_select_dropdown_option(municipio_dropdown_xpath, municipio):

            # Selección de división
            division_dropdown_xpath = '//*[@id="ContentPlaceHolder1_EdoMpoDiv_ddDivision"]'
            divisiones = safe_get_dropdown_options(division_dropdown_xpath)
            if divisiones:
                for division in divisiones:
                    if safe_select_dropdown_option(division_dropdown_xpath, division):

                        # Verificar si la región ya existe antes de insertar
                        cur.execute("""
                            SELECT id_region FROM tarifas_anuales.region
                            WHERE estado = %s AND municipio = %s AND division = %s
                        """, (estado, municipio, division))

                        region_row = cur.fetchone()
                        if region_row is None:
                            # Insertar los datos de la región en la base de datos
                            cur.execute("""
                                INSERT INTO tarifas_anuales.region (estado, municipio, division)
                                VALUES (%s, %s, %s)
                            """, (estado, municipio, division))
                            id_region = cur.lastrowid  # Obtener el id generado de la región
                        else:
                            id_region = region_row[0]  # Usar el id existente

                        # Procesar solo la primera tabla para otros estados
                        process_table("table.table-bordered:nth-child(2)", id_region, anio, mes)

    except Exception as e:
        print(f"Error durante el procesamiento del municipio {municipio}: {e}")

# Lista de municipios de Aguascalientes
municipios = ['AGUASCALIENTES', 'JESUS MARIA', 'RINCON DE ROMOS', 'CALVILLO', 'PABELLON DE ARTEAGA']

# Ejecutar el scraping en paralelo para los municipios de Aguascalientes
with ThreadPoolExecutor(max_workers=4) as executor:  # Usamos 4 threads
    executor.map(process_municipio, municipios)

# Cerrar cursor y conexión
cur.close()
conn.close()

# Cerrar el navegador
driver.quit()
