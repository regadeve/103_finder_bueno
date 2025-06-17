import streamlit as st
import requests
import time
import pandas as pd
import random
import os
from PIL import Image

# --- Configuración de la página ---
st.set_page_config(page_title="Discogs Finder", page_icon="☠️", layout="centered")

# --- Contraseña y API key del usuario ---
correct_password = "103_records"
password = st.text_input("Por favor, ingresa la contraseña:", type="password")
if password != correct_password:
    st.warning("Contraseña incorrecta. Acceso denegado.")
    st.stop()

# --- Solicita token API personal al usuario ---
user_token = st.text_input("Introduce tu Discogs API Token personal:", type="password")
if not user_token:
    st.warning("Debes introducir tu API Token para continuar.")
    st.stop()

# --- Logo ---
try:
    logo = Image.open("logo.png")
    st.image(logo, width=120)
except FileNotFoundError:
    st.warning("Logo no encontrado. Asegúrate de que el archivo 'logo.png' esté en la carpeta.")

# --- Inicializar estado ---
if 'resultados' not in st.session_state:
    if os.path.exists('temp_resultados.csv'):
        st.session_state.resultados = pd.read_csv('temp_resultados.csv').to_dict(orient='records')
        st.success(f"✅ Se han recuperado {len(st.session_state.resultados)} resultados anteriores del archivo temporal.")
    else:
        st.session_state.resultados = []

# --- Constantes ---
HEADERS = {'User-Agent': 'RareCDsApp/1.0'}
SEARCH_URL = 'https://api.discogs.com/database/search'
GENRES = ["Electronic", "Rock", "Jazz", "Funk / Soul", "Hip Hop", "Pop", "Classical", "Reggae", "Blues", "Latin"]
STYLES = ["Pop Rock", "House", "Vocal", "Experimental", "Punk", "Alternative Rock", "Synth-pop", "Techno", "Indie Rock", "Ambient", "Soul", "Disco", "Hardcore", "Folk", "Ballad", "Country", "Hard Rock", "Electro", "Rock & Roll", "Chanson", "Romantic", "Trance", "Heavy Metal", "Psychedelic Rock", "Folk Rock", "Soundtrack", "Downtempo", "Noise", "Schlager", "Prog Rock", "Funk", "Classic Rock", "Easy Listening", "Black Metal", "Tech House", "Blues Rock", "Rhythm & Blues", "Deep House", "New Wave", "Industrial", "Classical", "Death Metal", "Drum n Bass", "Progressive House", "Euro House", "Soft Rock", "Garage Rock", "Abstract", "Gospel", "Europop", "Minimal", "Acoustic", "Baroque", "Thrash", "Modern", "Swing", "Big Band", "Indie Pop", "Dub", "Country Rock", "Drone", "Contemporary Jazz", "Breakbeat", "Progressive Trance", "Opera", "Holiday", "Contemporary", "IDM", "Dancehall", "African", "Breaks", "Dark Ambient", "Reggae", "Art Rock", "Post-Punk", "Contemporary R&B", "Fusion", "Gangsta", "Doom Metal", "Dance-pop", "Religious", "Pop Rap", "Avantgarde", "RnB/Swing", "Beat", "Electro House", "Hard Trance", "Acid", "Instrumental", "Rockabilly", "Score", "Jazz-Funk", "Comedy", "Lo-Fi", "Roots Reggae", "Theme", "Grindcore", "Leftfield", "Ska", "Post Rock", "Spoken Word", "Soul-Jazz", "Bolero", "Psy-Trance", "Power Pop", "Dubstep", "Glam", "Salsa", "New Age", "Hip Hop", "Bop", "Conscious", "Goth Rock", "Modern Classical", "Jazz-Rock", "Cumbia", "Hard House", "Emo", "Free Improvisation", "J-pop", "Musical", "Trip Hop", "Latin Jazz", "Stoner Rock", "Volksmusik", "EBM", "Italo-Disco", "Shoegaze", "MPB", "Surf", "Jungle", "Field Recording", "Doo Wop", "Hard Bop", "Story", "Hardstyle", "Free Jazz", "Synthwave", "Pop Punk", "Tango", "Choral", "Oi", "Samba", "Garage House", "Trap", "Darkwave", "Radioplay", "Cool Jazz", "Celtic", "Bluegrass", "Vaporwave", "Post Bop", "Laïkó", "Eurodance", "Happy Hardcore", "UK Garage", "Metalcore", "Tribal", "Polka", "Novelty", "Smooth Jazz", "Hardcore Hip-Hop", "Flamenco", "Grunge", "Progressive Metal", "Italodance", "AOR", "Dixieland", "Arena Rock", "Kayōkyoku", "Nu Metal", "Southern Rock", "Symphonic Rock", "Hindustani", "Boom Bap", "Rumba", "Future Jazz", "Parody", "Latin", "Glitch", "Harsh Noise Wall", "Power Metal", "Cha-Cha", "Audiobook", "Merengue", "Space Rock", "Krautrock", "Dub Techno", "Bossa Nova", "Gabber", "Speed Metal", "Neo-Classical", "Breakcore", "Hi NRG", "Jazzy Hip-Hop", "Ranchera", "Post-Hardcore", "Poetry", "Power Electronics", "Reggae-Pop", "Bollywood", "Avant-garde Jazz", "Acid House", "Boogie", "Dungeon Synth", "Marches", "Renaissance", "Minimal Techno", "Musique Concrète", "Sludge Metal", "Electric Blues", "Mod", "Mambo", "Bossanova", "Chiptune", "Nu-Disco", "Country Blues", "Freestyle", "Acid Jazz", "Bass Music", "Interview", "Thug Rap", "Tribal House", "Big Beat", "Berlin-School", "Math Rock", "Indian Classical", "Light Music", "Modal", "Calypso", "Psychedelic", "Chicago Blues", "Broken Beat", "Education", "Neofolk", "Rocksteady", "Ethereal", "Impressionist", "Mandopop", "Neo Soul", "Crust", "Afrobeat", "Operetta", "Afro-Cuban", "Guaracha", "Britpop", "Lounge", "Video Game Music", "Chillwave", "Grime", "G-Funk", "Hip-House", "Ragtime", "Éntekhno", "Goregrind", "Euro-Disco", "Goa Trance", "Melodic Death Metal", "Canzone Napoletana", "Gothic Metal", "Lovers Rock", "Brass Band", "Deep Techno", "Nursery Rhymes", "Psychobilly", "Symphonic Metal", "Rhythmic Noise", "Neo-Romantic", "Dialogue", "Tech Trance", "Dream Pop", "Medieval", "Son", "Cut-up/DJ", "Hard Techno", "Pacific", "Atmospheric Black Metal", "K-pop", "Speedcore", "Twist", "Guaguancó", "Ragga", "Nordic", "Eurobeat", "Promotional", "Military", "Honky Tonk", "Organ", "Educational", "Ragga HipHop", "New Jack Swing", "Space-Age", "Mariachi", "Melodic Hardcore", "Fado", "Political", "Funk Metal", "Deathcore", "Music Hall", "Romani", "Sound Collage", "Acid Rock", "Hawaiian", "City Pop", "Highlife", "Soukous", "Soca", "Folk Metal", "Hands Up", "J-Rock", "Reggaeton", "Zouk", "Makina", "Freetekno", "Anison", "Afro-Cuban Jazz", "Speech", "Witch House", "Horrorcore", "Monolog", "Noisecore", "Post-Metal", "Jazzdance", "Piano Blues", "Delta Blues", "Vallenato", "Modern Electric Blues", "Coldwave", "Luk Thung", "Norteño", "Public Broadcast", "Bubblegum", "Cubano", "Electroacoustic", "New Beat", "Forró", "Italo House", "Gypsy Jazz", "Corrido", "Bhangra", "Enka", "Sound Art", "No Wave", "Viking Metal", "Therapy", "Harmonica Blues", "Jumpstyle", "Porro", "Alternative Metal", "Texas Blues", "Boogaloo", "Alt-Pop", "Cajun", "Special Effects", "Speed Garage", "Pub Rock", "Oratorio", "Yé-Yé", "Noise Rock", "Industrial Metal", "Post-Modern", "Tejano", "Cloud Rap", "Andean Music", "P.Funk", "Jump Blues", "Hillbilly", "Karaoke", "Depressive Black Metal", "Power Violence", "Illbient", "Pachanga", "Bassline", "Rebetiko", "Groove Metal", "Technical Death Metal", "Descarga", "Guajira", "Boogie Woogie", "Cantopop", "Chinese Classical", "Screw", "Raï", "Beguine", "Donk", "Son Montuno", "Louisiana Blues", "Deathrock", "Hokkien Pop", "Nueva Cancion", "Min'yō", "Séga", "Russian Pop", "Charanga", "Western Swing", "Copla", "Dansband", "Crunk", "Horror Rock", "Juke", "Klezmer", "Jangle Pop", "Latin Pop", "Sermon", "Levenslied", "Aboriginal", "Pasodoble", "Compas", "Technical", "Catalan Music", "Carnatic", "Electroclash", "DJ Battle Tool", "Disco Polo", "Bachata", "Tropical House", "Appalachian Music", "Ethno-pop", "Health-Fitness", "Conjunto", "Ghetto", "Danzon", "Concert Film", "Népzene", "Funeral Doom Metal", "Música Criolla", "Progressive Breaks", "Halftime", "Turntablism", "Minneapolis Sound", "Swingbeat", "Sea Shanties", "Batucada", "Musette", "Indo-Pop", "Huayno", "Pornogrind", "Zydeco", "Bounce", "Bayou Funk", "Free Funk", "Bakersfield Sound", "Quechua", "Footwork", "Balearic", "Early", "Dark Electro", "Liscio", "Cretan", "Lambada", "J-Core", "Steel Band", "Baião", "Sound Poetry", "Go-Go", "Swamp Pop", "Doomcore", "Movie Effects", "Choro", "Axé", "Skiffle", "Miami Bass", "Schranz", "Ghetto House", "Pipe & Drum", "Glitch Hop", "Plena", "Bleep", "Ghazal", "Plunderphonics", "Gamelan", "Kwaito", "Hyperpop", "Erotic", "Cabaret", "Zarzuela", "Mizrahi", "Kolo", "Persian Classical", "Chamamé", "Spiritual Jazz", "Rōkyoku", "Baroque Pop", "Barbershop", "Bengali Music", "Chacarera", "Blackgaze", "Gaita", "Crossover thrash", "Britcore", "Exotica", "Phonk", "Future House", "Spirituals", "UK Street Soul", "Public Service Announcement", "Dangdut", "Rock Opera", "Group Sounds", "Sunshine Pop", "Neo Trance", "Chutney", "K-Rock", "Memphis Blues", "Beatdown", "Occitan", "Drill", "Ghettotech", "Qawwali", "Joropo", "Reggae Gospel", "Tamil Film Music", "Favela Funk", "Luk Krung", "Future Bass", "East Coast Blues", "Twelve-tone", "Nhạc Vàng", "Marimba", "Gusle", "Slowcore", "Villancicos", "Banda", "Kaseko", "Keroncong", "Timba", "Hyphy", "Andalusian Classical", "Shidaiqu", "Guarania", "Dub Poetry", "Dark Jazz", "Ambient House", "UK Funky", "Izvorna", "Morna", "Hiplife", "Piedmont Blues", "Cape Jazz", "Milonga", "Maloya", "Baltimore Club", "Toasting", "Jibaro", "Overtone Singing", "Electro Swing", "Medical", "French House", "Mento", "Mathcore", "Sephardic", "Jota", "Caipira", "Vaudeville", "Deconstructed Club", "Marcha Carnavalesca", "Lento Violento", "Salegy", "Galician Traditional"]
SLEEP_TIME_DETAILS = 1.2
GUARDAR_CADA_N = 10
MAX_RETRIES = 3

# --- Filtros ---
st.markdown("<h4 style='color: #1DB954;'>⚙️ Filtros de búsqueda</h4>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    year_start = st.number_input("Año de inicio", min_value=1950, max_value=2025, value=1995)
    year_end = st.number_input("Año de fin (opcional)", min_value=1950, max_value=2025, value=year_start)
    have_limit = st.number_input("Máximo número de personas que lo tengan", value=20)
with col2:
    max_versions = st.number_input("Máximo número de versiones permitidas", value=2)
    country = st.text_input("País (ISO)", "")

format_selected = st.selectbox("Formato", ["Todos", "CD", "Vinyl"])
type_selected = st.selectbox("Tipo de búsqueda", ["release", "master", "Todos"])
genres = st.multiselect("Géneros", GENRES)
styles = st.multiselect("Estilos", STYLES)

# Opciones de búsqueda de estilos
st.markdown("#### Modo de búsqueda de estilos:")
style_match_mode = st.radio(
    "",
    ["Estricto (exactamente estos estilos y nada más)", 
     "Inclusivo (contiene estos estilos y puede tener otros)"]
)
strict_genre = st.checkbox("🎯 Solo mostrar resultados que tengan exclusivamente estos géneros")

# Mostrar configuración actual
if styles:
    if style_match_mode == "Inclusivo (contiene estos estilos y puede tener otros)":
        st.info(f"📌 Búsqueda optimizada: Se buscarán resultados con '{styles[0]}' y luego se filtrarán los que además contengan {', '.join(styles[1:]) if len(styles) > 1 else ''}.")
    else:
        st.info(f"📌 Búsqueda estricta: Resultados que tengan exactamente estos estilos: {', '.join(styles)}")

# --- Botón para borrar resultados ---
if st.button("🗑 Borrar resultados anteriores"):
    st.session_state.resultados = []
    if os.path.exists('temp_resultados.csv'):
        os.remove('temp_resultados.csv')
    st.success("Resultados y archivo temporal eliminados.")

# --- Función para mostrar un resultado ---
def mostrar_resultado(cd_data, contador):
    # Destacar estilos coincidentes
    estilos_texto = cd_data['Estilos']
    if styles:
        for style in styles:
            if style in estilos_texto:
                estilos_texto = estilos_texto.replace(style, f"<span style='background-color: #1DB95433; font-weight: bold;'>{style}</span>")
    
    return f'''
    <div style='margin-bottom: 20px; display: flex; align-items: center;'>
        <img src="{cd_data['Imagen']}" style='width: 90px; height: auto; border-radius: 8px; margin-right: 15px;'>
        <div>
            <strong>{contador}. <a href="{cd_data['Enlace']}" target="_blank">{cd_data['Título']}</a></strong><br>
            {cd_data['Artista']} ({cd_data['Año']})<br>
            🎧 <em>{estilos_texto}</em> | 👥 Have: {cd_data['Have']}
        </div>
    </div>
    '''

# Función mejorada para hacer solicitudes HTTP con reintentos
def make_request(url, params=None, max_retries=MAX_RETRIES):
    wait_message = st.empty()
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=15)
            
            # Si recibimos error de límite de ratio, esperar y reintentar
            if response.status_code == 429:
                wait_time = 65  # 65 segundos para asegurarnos
                for i in range(wait_time, 0, -1):
                    wait_message.warning(f"⚡ Límite de peticiones alcanzado. Esperando {i} segundos para continuar...")
                    time.sleep(1)
                continue  # Reintentar después de esperar
            
            response.raise_for_status()  # Lanzar excepción para otros códigos de error
            wait_message.empty()  # Limpiar mensaje de espera
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)  # Backoff exponencial
                wait_message.warning(f"Error en la solicitud: {e}. Reintentando en {wait_time} segundos...")
                time.sleep(wait_time)
            else:
                wait_message.error(f"Error después de {max_retries} intentos: {e}")
                return None
    
    return None

# --- Búsqueda ---
dejar_buscar = st.button("🔍 Buscar en Discogs")
if dejar_buscar:
    st.markdown("---")
    
    # Reiniciamos los resultados
    st.session_state.resultados = []
    contador = 0
    
    # Si no hay estilos seleccionados, no tiene sentido continuar
    if not styles:
        st.warning("Por favor, selecciona al menos un estilo para continuar.")
        st.stop()
    
    # Explicación clara del modo de búsqueda
    if style_match_mode == "Estricto (exactamente estos estilos y nada más)":
        st.info(f"🔍 Buscando lanzamientos que tengan EXACTAMENTE estos estilos: {', '.join(styles)}")
    else:
        if len(styles) > 1:
            st.info(f"🔍 Buscando lanzamientos con '{styles[0]}' que también contengan: {', '.join(styles[1:])}")
        else:
            st.info(f"🔍 Buscando lanzamientos que contengan '{styles[0]}'")
    
    # Contenedores para mostrar información y estado
    status_container = st.empty()
    progress_container = st.empty()
    
    # Contenedor para mostrar resultados en tiempo real
    resultados_container = st.container()
    resultados_container.markdown("### 🎵 Resultados:")
    results_display = resultados_container.empty()
    resultados_html = ""
    
    # Vamos a necesitar resultados únicos
    unique_resource_urls = set()
    all_results = []  # Almacena todos los resultados
    
    # Determinar parámetros de búsqueda según el modo
    if style_match_mode == "Estricto (exactamente estos estilos y nada más)":
        # Para modo estricto, buscamos con todos los estilos a la vez
        search_style = styles
    else:
        # Para modo inclusivo, buscamos solo con el primer estilo seleccionado
        search_style = [styles[0]]
    
    # Parámetros base para la búsqueda actual
    base_params = {
        'token': user_token,
        'per_page': 100,
        'year': str(year_start) if year_start == year_end else f"{year_start}-{year_end}"
    }
    
    if type_selected != "Todos":
        base_params['type'] = type_selected
    if format_selected != "Todos" and type_selected != "master":
        base_params['format'] = format_selected
    if country:
        base_params['country'] = country
    if genres:
        base_params['genre'] = genres
    
    # Agregamos el estilo a la búsqueda
    base_params['style'] = search_style
    
    # Intentar obtener la primera página para verificar el total
    estilo_texto = ", ".join(search_style) if isinstance(search_style, list) else search_style
    status_container.info(f"Buscando resultados con estilo: {estilo_texto}")
    
    initial_data = make_request(SEARCH_URL, params={**base_params, 'page': 1})
    if not initial_data:
        st.error(f"❌ Error al buscar estilo '{estilo_texto}'. Por favor, intenta nuevamente.")
        st.stop()
    
    total_pages = initial_data['pagination']['pages']
    total_items = initial_data['pagination']['items']
    
    status_container.info(f"Encontrados {total_items} resultados en {total_pages} páginas para '{estilo_texto}'. Procesando todas las páginas...")
    
    # Barra de progreso para páginas
    progress_pages = progress_container.progress(0)
    
    # Procesar cada página - TODAS LAS PÁGINAS sin límite
    for page in range(1, total_pages + 1):
        progress_pages.progress(page / total_pages)
        status_container.info(f"📄 Procesando página {page}/{total_pages} para '{estilo_texto}'")
        
        # Usar la página ya obtenida para la primera iteración
        if page == 1 and 'results' in initial_data:
            page_results = initial_data.get('results', [])
        else:
            # Obtener las demás páginas
            page_data = make_request(SEARCH_URL, params={**base_params, 'page': page})
            if not page_data:
                status_container.warning(f"⚠️ Error al obtener la página {page}. Continuando...")
                continue
            page_results = page_data.get('results', [])
        
        # Filtrar resultados duplicados por resource_url
        for item in page_results:
            resource_url = item.get('resource_url')
            if resource_url and resource_url not in unique_resource_urls:
                unique_resource_urls.add(resource_url)
                all_results.append(item)
    
    status_container.info(f"Procesando {len(all_results)} resultados únicos...")
    
    # Nuevo progreso para procesamiento de detalles
    details_progress = progress_container.progress(0)
    
    # Ahora procesa cada ítem único
    contador = 0
    processed_count = 0
    
    for item in all_results:
        processed_count += 1
        details_progress.progress(processed_count / len(all_results))
        
        resource_url = item.get('resource_url')
        if not resource_url:
            continue
        
        time.sleep(SLEEP_TIME_DETAILS)
        
        # Mostrar info sobre el elemento actual
        item_title = item.get('title', '')[:50]
        status_container.info(f"Analizando ({processed_count}/{len(all_results)}): {item_title}...")
        
        # Obtener detalles con la función mejorada
        details = make_request(resource_url)
        
        if not details:
            continue  # Si hay error, pasar al siguiente
        
        # Filtro 1: Have
        have = details.get('community', {}).get('have', 9999)
        if have >= have_limit:
            continue
        
        # Filtro 2: Año
        release_year = details.get('year', 0)
        if release_year < year_start or release_year > year_end:
            continue
        
        # Obtener estilos del lanzamiento
        release_styles = details.get('styles', [])
        
        # IMPORTANTE: Verificación de estilos según el modo
        if style_match_mode == "Estricto (exactamente estos estilos y nada más)":
            # En modo estricto, debe tener exactamente los estilos seleccionados
            if set(release_styles) != set(styles):
                continue
        else:
            # En modo inclusivo, debe contener TODOS los estilos seleccionados (pero puede tener otros)
            if not all(style in release_styles for style in styles):
                continue
        
        # Filtro 3: Géneros (solo si hay géneros seleccionados)
        if genres:
            release_genres = details.get('genres', [])
            # Si strict_genre está activado, verificar que sean exactamente los géneros seleccionados
            if strict_genre and set(release_genres) != set(genres):
                continue
        
        # Filtro 4: Versiones
        master_id = details.get('master_id')
        if master_id and max_versions > 0:
            try:
                versions_url = f"https://api.discogs.com/masters/{master_id}/versions"
                versions_data = make_request(versions_url)
                if not versions_data:
                    continue
                num_versions = versions_data['pagination']['items']
                if num_versions > max_versions:
                    continue
            except:
                continue
        
        # Si pasa todos los filtros, agregar a los resultados
        cd_data = {
            "Título": details.get('title', ''),
            "Artista": details.get('artists_sort', ''),
            "Año": release_year,
            "Have": have,
            "Géneros": ", ".join(details.get('genres', [])),
            "Estilos": ", ".join(release_styles),
            "Enlace": details.get('uri', ''),
            "Imagen": item.get('thumb', '')
        }
        
        # Mostrar un mensaje claro sobre el resultado encontrado
        status_container.success(f"✅ Resultado #{contador+1} encontrado: {cd_data['Título']} con estilos: {cd_data['Estilos']}")
        
        # Añadir a la sesión y mostrar inmediatamente
        st.session_state.resultados.append(cd_data)
        contador += 1
        
        # Agregar este resultado al HTML acumulativo
        resultados_html += mostrar_resultado(cd_data, contador)
        
        # Actualizar el display de resultados en tiempo real
        results_display.markdown(resultados_html, unsafe_allow_html=True)
        
        # Guardar progreso cada cierto número de resultados
        if contador % GUARDAR_CADA_N == 0:
            df_temp = pd.DataFrame(st.session_state.resultados)
            df_temp.to_csv('temp_resultados.csv', index=False)
            status_container.success(f"✅ Progreso guardado: {contador} resultados")
    
    # Finalizar búsqueda
    progress_container.empty()  # Eliminar las barras de progreso
    status_container.empty()    # Limpiar mensajes de estado
    
    st.markdown("---")
    if st.session_state.resultados:
        df = pd.DataFrame(st.session_state.resultados)
        df = df.drop_duplicates(subset=["Título", "Artista"])
        st.success(f"🌟 {len(df)} resultados únicos encontrados.")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar CSV Final",
            data=csv,
            file_name='discogs_resultados.csv',
            mime='text/csv',
        )
    else:
        st.warning("No se encontraron resultados con esos filtros.")