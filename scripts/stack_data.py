import pandas as pd
import os

#std_path = 'C:/Users/Francisco Valerio/Desktop/Work work/Atco/GDMTH-Project/data/final_data'
cwd = os.path.split(os.getcwd())
std_path = os.path.join(cwd[0], 'data', 'final_data')

data_2021 = os.path.join(std_path, 'info_2021.csv')
data_2022 = os.path.join(std_path, 'info_2022.csv')
data_2023 = os.path.join(std_path, 'info_2023.csv')
data_2024 = os.path.join(std_path, 'info_2024.csv')

output = os.path.join(std_path, 'tarifas_gdmth_cfe.csv')


def concatenate_csv(output_csv_path, *csv_files):

    dataframes = [pd.read_csv(csv_file) for csv_file in csv_files]

    df_concatenated = pd.concat(dataframes, axis = 0)

    df_concatenated.reset_index(drop=True, inplace=True)

    df_concatenated.to_csv(output_csv_path, index = False)

    print(f"Archivo CSV concatenado almacenado en {output_csv_path}")

concatenate_csv(output, data_2021, data_2022, data_2023, data_2024)