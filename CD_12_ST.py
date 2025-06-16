import streamlit as st
import requests
import time
import pandas as pd
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="Discogs Finder", page_icon="☠️", layout="centered")

# Contraseña
correct_password = "103_records"
password = st.text_input("Por favor, ingresa la contraseña:", type="password")
if password != correct_password:
    st.warning("Contraseña incorrecta. Acceso denegado.")
    st.stop()

# Logo
try:
    logo = Image.open("logo.png")
    st.image(logo, width=120)
except FileNotFoundError:
    st.warning("Logo no encontrado. Asegúrate de que el archivo 'logo.png' esté en la carpeta.")

# Título y descripción
st.markdown("<h1 style='text-align: center; color: white; font-size: 90%;'>☠️ Congratulations you have found the RARE GEMS finder developed by the 103 ...</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; font-size: 18px; color: #ccc;'>You are entering the depths of the Discogs archive...<br>Seek out hidden relics, obscure editions, and long-lost sonic treasures.<br><br>Only the truly curious will discover the rarest gems. 🕵️‍♂️</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Inicializar estado
if 'resultados' not in st.session_state:
    st.session_state.resultados = []

# Constantes
TOKEN = 'eGLWhqoSvHtraoWvsAMeHBGmlIJlEcRFxMSnZFoS'
HEADERS = {'User-Agent': 'RareCDsApp/1.0'}
SEARCH_URL = 'https://api.discogs.com/database/search'
GENRES = ["Electronic", "Rock", "Jazz", "Funk / Soul", "Hip Hop", "Pop", "Classical", "Reggae", "Blues", "Latin"]
STYLES = ["Electro","Industrial","Acid House","Abstract","Goa Trance","Tech House", "Techno", "House", "Ambient", "Breakbeat", "IDM", "Dubstep", "Trance", "Drum n Bass", "EBM", "Minimal", "Synth-pop", "New Beat","Experimental","Progressive House","Progressive Trance","Dub","New Wave","Electroclash","Acid"]

# Filtros
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
strict_genre = st.checkbox("🎯 Solo mostrar resultados que tengan **exclusivamente** estos géneros")
strict_style = st.checkbox("🎯 Solo mostrar resultados que tengan **exclusivamente** estos estilos")

# Botón para borrar resultados
if st.button("🗑 Borrar resultados anteriores"):
    st.session_state.resultados = []

# Búsqueda
dejar_buscar = st.button("🔍 Buscar en Discogs")
if dejar_buscar:
    st.markdown("---")
    st.info("Buscando en Discogs... Esto puede tardar un poco")
    st.session_state.resultados = []
    placeholder = st.empty()
    lista_resultados = st.container()
    contador = 0

    params = {
        'token': TOKEN,
        'per_page': 100,
        'page': 1,
        'year': str(year_start) if year_start == year_end else f"{year_start}-{year_end}"
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
        total_pages = data['pagination']['pages']
    except Exception as e:
        st.error(f"❌ Error en la búsqueda del año {year_start} a {year_end}: {e}")
        st.stop()

    progress_bar = st.progress(0)

    with st.spinner(f"Procesando resultados de {year_start} a {year_end}..."):
        for page in range(1, total_pages + 1):
            st.write(f"🔄 Procesando página {page} de {total_pages}")
            params['page'] = page
            try:
                res = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=10)

                # 👇 Mejora 4: Manejo de rate limit
                if res.status_code == 429:
                    st.error("⛔ Has alcanzado el límite de peticiones por minuto de la API de Discogs. Espera unos minutos e inténtalo de nuevo.")
                    break

                res.raise_for_status()
                items = res.json().get('results', [])
            except requests.exceptions.RequestException as e:
                st.warning(f"⚠️ Error en la página {page}: {e}, reintentando tras 5 segundos...")
                time.sleep(5)
                continue
            except Exception as e:
                st.warning(f"⚠️ Error inesperado en la página {page}: {e}, continuando...")
                continue

            for item in items:
                resource_url = item.get("resource_url")
                if not resource_url:
                    continue
                time.sleep(1.2)
                try:
                    details = requests.get(resource_url, headers=HEADERS, timeout=10).json()
                    if not details:
                        continue

                    have = details.get('community', {}).get('have', 9999)
                    if have >= have_limit:
                        continue

                    release_year = details.get('year', 0)
                    if release_year < year_start or release_year > year_end:
                        continue

                    release_styles = details.get('styles', [])
                    release_genres = details.get('genres', [])

                    if styles and not all(s in release_styles for s in styles):
                        continue
                    if strict_style and set(release_styles) != set(styles):
                        continue
                    if strict_genre and set(release_genres) != set(genres):
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
                        "Géneros": ", ".join(release_genres),
                        "Estilos": ", ".join(release_styles),
                        "Enlace": details.get('uri'),
                        "Imagen": item.get("thumb", "")
                    }
                    st.session_state.resultados.append(cd_data)
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

                except Exception as e:
                    st.warning(f"⚠️ Error al obtener detalles del ítem: {e}, saltando...")
                    continue

            progress_bar.progress(page / total_pages)

        st.markdown("---")
        if st.session_state.resultados:
            st.success(f"🌟 {len(st.session_state.resultados)} resultados encontrados.")
            df = pd.DataFrame(st.session_state.resultados)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Descargar CSV",
                data=csv,
                file_name='discogs_resultados.csv',
                mime='text/csv',
            )
        else:
            st.warning("No se encontraron resultados con esos filtros.")
