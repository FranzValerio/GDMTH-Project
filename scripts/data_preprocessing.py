import pandas as pd

anio = 2024
std_path = 'C:/Users/Francisco Valerio/Desktop/Work work/Atco/GDMTH-Project/data'

region_path = std_path + '/region.csv'
tarifas_path = std_path + f'/tarifas_{anio}.csv'
infra_path = std_path + f'/infraestructura_{anio}.csv'
output_path = std_path + f'/final_data/info_{anio}.csv'

def anual_data_processing(region_path, tarifas_path, infra_path, anio, output_csv_path):

    # Cargamos los archivos
    region = pd.read_csv(region_path, encoding = 'ISO-8859-1')
    tarifas_data = pd.read_csv(tarifas_path)
    infra_data = pd.read_csv(infra_path)

    # Añadimos la columna de año

    tarifas_data.insert(2, 'anio', anio)
    infra_data.insert(2, 'anio', anio)

    # Hacemos los merges

    merged_data = pd.merge(tarifas_data, infra_data, on = 'id_region', how = 'inner')
    merged_data = pd.merge(merged_data, region, on = 'id_region', how ='inner')

    # Revisamos valores nulos

    print(f"Valores nulos para los datos del año {anio}:")
    print(merged_data.isnull().sum())

    # Eliminamos duplicados

    merged_data = merged_data.drop_duplicates()

    # Exportamos el CSV del merge

    merged_data.to_csv(output_csv_path, index = False)
    print(f"Archivo CSV para el año {anio} guardado en {output_csv_path}")


anual_data_processing(region_path, tarifas_path, infra_path, anio, output_path)