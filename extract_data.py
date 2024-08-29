# Libraries
import os
import json
import re
import requests
import pandas as pd
from datetime import date
from os.path import join, exists
from os import makedirs
from dotenv import load_dotenv
load_dotenv()


def build_data(start_date, end_date, max_pages=10):
    MY_HOME = os.path.expanduser('~')
    ARTICLES_DIR = join(MY_HOME, 'NLP_O2024/tempdata')
    RESULTS_DIR = join(MY_HOME, 'NLP_O2024/results')
    TEXTOS_DIR = join(MY_HOME, 'NLP_O2024/textos')
    API_ENDPOINT = "http://content.guardianapis.com/search"
    
    makedirs(ARTICLES_DIR, exist_ok=True)
    makedirs(RESULTS_DIR, exist_ok=True)
    makedirs(TEXTOS_DIR, exist_ok=True)
    
    try:
        MY_API_KEY = os.getenv('API_KEY')
    except FileNotFoundError:
        return "ERROR: API key file not found."

    def get_date(text):
        pattern = r"(\d{4})-(\d{2})-(\d{2})"
        match = re.search(pattern, text)
        if match:
            return match.group()
        else:
            from datetime import datetime
            current_datetime = datetime.now()
            return f"Unnamed{current_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    def create_categories_folders(categories):
        for category in categories:
            category_dir = join(TEXTOS_DIR, category)
            makedirs(category_dir, exist_ok=True)
    
    def count_txt_files(folder_path):
        return sum(1 for entry in os.scandir(folder_path) if entry.is_file() and entry.name.endswith('.txt'))
    
    def get_direction_csv(category):
        return os.path.join(TEXTOS_DIR, category)
    
    api_params = {
        'from-date': "",
        'to-date': "",
        'order-by': "newest",
        'show-fields': "bodyText",
        'page-size': 200,
        'api-key': MY_API_KEY
    }

    date_str = start_date.strftime("%Y-%m-%d")
    date2_str = end_date.strftime("%Y-%m-%d")
    filename = join(ARTICLES_DIR, date_str + '.json')

    if not exists(filename):
        resultados = []
        api_params['from-date'] = date_str
        api_params['to-date'] = date2_str
        current_page = 1
        total_pages = max_pages

        while current_page <= total_pages:
            api_params['page'] = current_page
            resp = requests.get(API_ENDPOINT, params=api_params)
            data = resp.json()
            resultados.extend(data['response']['results'])
            current_page += 1
            total_pages = min(data['response']['pages'], max_pages)
        
        with open(filename, 'w') as f:
            f.write(json.dumps(resultados, indent=2))
    
    if not os.path.exists(ARTICLES_DIR):
        return "ERROR: El directorio especificado no existe"

    archivos = os.listdir(ARTICLES_DIR)
    if not archivos:
        return "ERROR: El directorio está vacío"

    filename = join(ARTICLES_DIR, archivos[0])
    with open(filename) as archivo:
        datos = json.load(archivo)

    titulos = [articulo['webTitle'] for articulo in datos]
    contenidos = [articulo['fields']['bodyText'] for articulo in datos]
    seccion = [articulo['sectionName'] for articulo in datos]

    df = pd.DataFrame(titulos, columns=['Encabezado'])
    df['Contenido'] = contenidos
    df['Seccion'] = seccion

    output = join(RESULTS_DIR, f"articulos-{get_date(filename)}.csv")
    df.to_csv(output, index=False)

    if not os.path.exists(RESULTS_DIR):
        return "ERROR: El directorio especificado no existe"

    archivos = os.listdir(RESULTS_DIR)
    if not archivos:
        return "ERROR: El directorio está vacío"

    filename = join(RESULTS_DIR, archivos[0])
    datos = pd.read_csv(filename)
    contenidos = list(datos['Contenido'])

    create_categories_folders(datos['Seccion'].unique())

    for i in range(len(datos)):
        seccion = datos['Seccion'][i]
        folder = os.path.join(TEXTOS_DIR, seccion)
        indice = count_txt_files(folder) + 1
        filename = os.path.join(folder, f"article{indice}.txt")
        
        with open(filename, "w") as f:
            f.write(str(contenidos[i]))

    return "Data extracted successfully.\n"

def text_to_list(directory_path):
    all_lines = []

    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a .txt file
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            
            # Read the .txt file and load each line into a list
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Strip newline characters from each line and append to the list
            lines = [line.strip() for line in lines]
            all_lines.extend(lines)

    return all_lines


