# Tokenizar y comparar vectores basados en textos (txt)

### Si solo quieres correr el codigo ve al archivo main.py y ejecuta el codigo. Eso hara toda la actividad por ti pero si lo que quieres es entender que esta haciendo el documento te lo dejo más sencillo en este README donde te dejo lo que hace el codigo y como esta compuesto
---
# Extract Data (extract_data.py)

Que funciones tengo?
- build_data
- text_to_list

## build_data
Build data toma como parametros una fecha inicial (start_date), una fecha final (end_date) y maximo de paginas (max_pages) que por defecto esta igualada a 10

### Parte 1

```python
MY_HOME = os.path.expanduser('~') #-> Encuentra el root la carpeta inicial digamos

ARTICLES_DIR = join(MY_HOME, 'NLP_O2024/tempdata') #-> Crea una carpeta dentro de NLP02024 que se llama tempadata

RESULTS_DIR = join(MY_HOME, 'NLP_O2024/results') #-> Crea una carpeta dentro de NLP02024 que se llama tempadata

TEXTOS_DIR = join(MY_HOME, 'NLP_O2024/textos') #-> Crea una carpeta dentro de NLP02024 que se llama tempadata

API_ENDPOINT = "http://content.guardianapis.com/search" #-> El endpoint del api para que funcione
```

### Parte 2

```python
makedirs(ARTICLES_DIR, exist_ok=True)
makedirs(RESULTS_DIR, exist_ok=True)
makedirs(TEXTOS_DIR, exist_ok=True)

try:
    MY_API_KEY = os.getenv('API_KEY')
except FileNotFoundError:
    return "ERROR: API key file not found."

```

Basicamente esta parte solo revisa que los directorios que se crearon existan y que el APIKEY este dentro de tu archivo .env

### Parte 3
```python
def get_date(text):
    pattern = r"(\d{4})-(\d{2})-(\d{2})"
    match = re.search(pattern, text)
    if match:
        return match.group()
    else:
        from datetime import datetime
        current_datetime = datetime.now()
        return f"Unnamed{current_datetime.strftime('%Y-%m-%d %H:%M')}"
```

Esta parte extrae la fecha basada en un patron de regex

### Parte 4
```python
def create_categories_folders(categories):
    for category in categories:
        category_dir = join(TEXTOS_DIR, category)
        makedirs(category_dir, exist_ok=True)
```

Crea las categorias y crea un directorio __mkdir__ para cada categoria lo que termina en las carpetas que tendras dentro del textos de la siguiente forma:

    |-textos
    |---arte
    |---deportes
    |---etc

### Parte 5
```python
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

```
Utiliza la api para extraer las noticias y guardarlas en sus respectivas carpetas

## texts_to_list
Text to List es una funcion que nace de guardar los archivos txt que tenemos descargados en nuestras carpetas a una lista que contenga el texto del archivo como string

### Parte 1
```python
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
```

Basicamente itera sobre todos los archivos del directorio y los extrae como un documento para leerlo y guardarlo en la variable lines luego se hace un strip para quedarse con el string y se apendea a la lista lines

# Tokenice (tokenice.py)

Que funciones tengo?
- data_cleaning
- vocab_to_dict
- bag_of_words
- cocine_similarity

## data_cleaning
Data cleaning recibe como parametro una lista (data:list) y se encarga de crear una lista de vocabulario unico es decir sin palabras repetidas adicionalmente puede recibir un parametro booleano (rm_stop_words:bool) que le indica a la funcion eliminar las stop-words


estas son las dos formas de llamar a la función:
```python
vocab, len_vector,sentences = data_cleaning(data=myList)
vocab, len_vector,sentences = data_cleaning(data=myList, rm_stop_words=True)
```

### Parte 1
```python
#clean the corpus.
sentences = []
vocab = []
for sent in data:
    x = word_tokenize(sent)
    sentence = [w.lower() for w in x if w.isalpha() ]
    sentences.append(sentence)
    for word in sentence:
        if word not in vocab:
            vocab.append(word)

#number of words in the vocab
len_vector = len(vocab)

return vocab, len_vector, sentences
```

Este codifo itera sobre la lista con un ciclo for, ese ciclo for limpia de forma basica revisando que las letras esten en minusculas etc etc y despues los appendea a una nueva lista sentences para revisar que no existan repetidos. Esto puede ser remplazado con un set y te ahorras la parte de verificación se dejo asi para su migración a Java/C++

## vocab_to_dict
Vocab to dict recibe como parametro una lista y basada en esa lista crea un diccionario donde le asigna un id numerico a cada palabra del diccionario (Json) regresando algo como esto:
```python
{"word1":0,
    "word2":1,
        "word3":2}
```
De forma que podemos crear posteriormente una lista numerica basada en el contenido del diccionario

### Parte 1
```python
index_word = {}
for i,word in enumerate(vocab):
    index_word[word] = i

return index_word
```
Simplemente agrega un indice en el diccionario. No hay mucho que explicar aqui

## bag_of_words
bag of words recibe como parametros una frase (sent) el tamaño del vector (len_vector) y el indice diccionario de vocabulario. La forma correcta de llamar la función es la siguiente:
```python
vector = bag_of_words(sent=sentences[0],len_vector=len_vector, index_word=index_word)
vector1 = bag_of_words(sent=sentences[1],len_vector=len_vector, index_word=index_word)
vector2 = bag_of_words(sent=sentences[2],len_vector=len_vector, index_word=index_word)
```
Esto me va a regresar un vector numerico en formato lista
