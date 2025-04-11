import streamlit as st
import requests
import time
import pandas as pd
from PIL import Image

# Primero, coloca la configuración de la página
st.set_page_config(page_title="Discogs Finder", page_icon="☠️", layout="centered")

# Contraseña predefinida
correct_password = "103_records"

# Pantalla de inicio con la solicitud de contraseña
password = st.text_input("Por favor, ingresa la contraseña:", type="password")

# Si la contraseña es incorrecta, no deja acceder a la app
if password != correct_password:
    st.warning("Contraseña incorrecta. Acceso denegado.")
    st.stop()  # Detiene la ejecución del programa si la contraseña es incorrecta

# Si la contraseña es correcta, continuamos con el resto de la aplicación
# Logo
try:
    logo = Image.open("logo.png")
    st.image(logo, width=120)
except FileNotFoundError:
    st.warning("Logo no encontrado. Asegúrate de que el archivo 'logo.png' esté en la carpeta.")

# Título
st.markdown("<h1 style='text-align: center; color: white; font-size: 90%;'>☠️ Congratulations you have found the RARE GEMS finder developed by the 103 ...</h1>", unsafe_allow_html=True)

# Descripción
st.markdown(
    """
    <div style='text-align: center; font-size: 18px; color: #ccc;'>You are entering the depths of the Discogs archive...<br>Seek out hidden relics, obscure editions, and long-lost sonic treasures.<br><br>Only the truly curious will discover the rarest gems. 🕵️‍♂️</div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Constantes
TOKEN = 'eGLWhqoSvHtraoWvsAMeHBGmlIJlEcRFxMSnZFoS'
HEADERS = {'User-Agent': 'RareCDsApp/1.0'}
SEARCH_URL = 'https://api.discogs.com/database/search'
GENRES = ["Electronic", "Rock", "Jazz", "Funk / Soul", "Hip Hop", "Pop", "Classical", "Reggae", "Blues", "Latin"]
STYLES = ["Electro", "Techno", "House", "Ambient", "Breakbeat", "IDM", "Dubstep", "Trance", "Drum n Bass", "EBM", "Minimal", "Synth-pop", "New Beat"]

# Filtros
st.markdown("<h4 style='color: #1DB954;'>⚙️ Filtros de búsqueda</h4>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    year_start = st.number_input("Año de inicio", min_value=1950, max_value=2025, value=1995)
    year_end = st.number_input("Año de fin (opcional)", min_value=1950, max_value=2025, value=year_start)  # Año de fin opcional
    have_limit = st.number_input("Máximo número de personas que lo tengan", value=20)
with col2:
    max_versions = st.number_input("Máximo número de versiones permitidas", value=2)
    country = st.text_input("País (ISO)", "")

format_selected = st.selectbox("Formato", ["Todos", "CD", "Vinyl"])
type_selected = st.selectbox("Tipo de búsqueda", ["release", "master", "Todos"])
genres = st.multiselect("Géneros", GENRES)
styles = st.multiselect("Estilos", STYLES)

# Búsqueda
if st.button("🔍 Buscar en Discogs"):
    st.markdown("---")
    st.info("Buscando en Discogs... Esto puede tardar un poco")
    resultados = []
    placeholder = st.empty()
    lista_resultados = st.container()
    contador = 0
    max_retries = 5  # Número máximo de reintentos fallidos para un ítem
    retries = 0  # Contador de reintentos fallidos

    # Si no se ingresa un año de fin, solo usar el año de inicio
    if year_start == year_end:
        params = {
            'token': TOKEN,
            'per_page': 100,
            'page': 1,
            'year': str(year_start),  # Solo el año de inicio
            'sort': 'title',
            'sort_order': 'asc'
        }
    else:
        params = {
            'token': TOKEN,
            'per_page': 100,
            'page': 1,
            'year': f"{year_start}-{year_end}",  # Rango de años
            'sort': 'title',
            'sort_order': 'asc'
        }

    if type_selected != "Todos":
        params['type'] = type_selected
    if format_selected != "Todos" and type_selected != "master":
        params['format'] = format_selected
    if country:
        params['country'] = country
    if genres:
        params['genre'] = genres
    if styles:
        params['style'] = styles

    try:
        response = requests.get(SEARCH_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        total_pages = data['pagination']['pages']  # Sin límite de páginas
    except Exception as e:
        st.error(f"❌ Error en la búsqueda del año {year_start} a {year_end}: {e}")
        st.stop()

    # Crear una barra de progreso
    progress_bar = st.progress(0)

    with st.spinner(f"Procesando resultados de {year_start} a {year_end}..."):
        for page in range(1, total_pages + 1):
            params['page'] = page
            try:
                res = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=10)  # Timeout de 10 segundos
                res.raise_for_status()

                items = res.json().get('results', [])
            except requests.exceptions.RequestException as e:
                st.warning(f"⚠️ Error en la página {page}: {e}, saltando...")
                continue  # Saltamos esta página y seguimos con la siguiente
            except ValueError:
                st.warning(f"⚠️ Respuesta no válida de la página {page}, continuando con la siguiente...")
                continue  # Saltamos esta página y seguimos con la siguiente
            except Exception as e:
                st.warning(f"⚠️ Error inesperado en la página {page}: {e}, continuando...")
                continue  # Saltamos esta página y seguimos con la siguiente

            for item in items:
                resource_url = item.get("resource_url")
                if not resource_url:
                    continue
                time.sleep(1.2)
                try:
                    details = requests.get(resource_url, headers=HEADERS, timeout=10).json()

                    # Si la respuesta está vacía, seguimos con el siguiente ítem
                    if not details:
                        st.warning(f"⚠️ Detalles vacíos para el ítem {item['title']}, saltando...")
                        continue

                    have = details.get('community', {}).get('have', 9999)
                    if have >= have_limit:
                        continue

                    release_year = details.get('year', 0)
                    if release_year < year_start or release_year > year_end:
                        continue

                    release_styles = details.get('styles', [])
                    if styles and not all(s in release_styles for s in styles):  # Aquí comparamos si todos los estilos están presentes
                        continue

                    master_id = details.get('master_id')
                    num_versions = 1
                    if master_id and max_versions:
                        try:
                            versions_url = f"https://api.discogs.com/masters/{master_id}/versions"
                            versions_resp = requests.get(versions_url, headers=HEADERS, timeout=10)
                            versions_resp.raise_for_status()
                            versions_data = versions_resp.json()
                            num_versions = versions_data['pagination']['items']
                            if num_versions > max_versions:
                                continue
                        except:
                            continue

                    cd_data = {
                        "Título": details.get('title'),
                        "Artista": details.get('artists_sort'),
                        "Año": release_year,
                        "Have": have,
                        "Géneros": ", ".join(details.get('genres', [])),
                        "Estilos": ", ".join(details.get('styles', [])),
                        "Enlace": details.get('uri'),
                        "Imagen": item.get("thumb", "")
                    }
                    resultados.append(cd_data)
                    contador += 1

                    placeholder.markdown(
                        f"**{contador}.** [{cd_data['Título']}]({cd_data['Enlace']}) - {cd_data['Artista']} ({cd_data['Año']}) | Have: {cd_data['Have']}"
                    )

                    with lista_resultados:
                        st.markdown(f'''
                        <div style='margin-bottom: 20px; display: flex; align-items: center;'>
                            <img src="{cd_data['Imagen']}" style='width: 90px; height: auto; border-radius: 8px; margin-right: 15px;'>
                            <div>
                                <strong>{contador}. <a href="{cd_data['Enlace']}" target="_blank">{cd_data['Título']}</a></strong><br>
                                {cd_data['Artista']} ({cd_data['Año']})<br>
                                🎧 <em>{cd_data['Estilos']}</em> | 👥 Have: {cd_data['Have']}
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)

                    # Actualizamos la barra de progreso después de procesar cada ítem
                    progress_bar.progress(contador / len(items))

                except Exception as e:
                    st.warning(f"⚠️ Error al obtener detalles del ítem: {e}, esperando 1 minuto antes de continuar...")
                    time.sleep(60)  # Esperar 1 minuto antes de continuar
                    continue  # Saltamos este ítem y seguimos con el siguiente

        st.markdown("---")
        if resultados:
            st.success(f"🎯 {len(resultados)} resultados encontrados.")
            df = pd.DataFrame(resultados)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Descargar CSV",
                data=csv,
                file_name='discogs_resultados.csv',
                mime='text/csv',
            )
        else:
            st.warning("No se encontraron resultados con esos filtros.")
