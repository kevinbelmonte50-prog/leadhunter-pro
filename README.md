**LeadHunter Pro** es una herramienta de generación de leads B2B que utiliza la API oficial de Google Maps (Places API) para extraer información pública de negocios.

Incluye:
- 🧠 Script en Python para extracción real de datos  
- 🎨 Interfaz web (demo) para visualización de leads  

---

## 🚀 Características

- 🔎 Búsqueda por rubro e ubicación  
- 📊 Extracción de datos de negocios desde Google Maps  
- ☎️ Obtención de teléfono, dirección y sitio web  
- 📁 Exportación automática a CSV y Excel  
- ⚡ Interfaz demo tipo SaaS (HTML)  
- ✔ Uso de API oficial (sin scraping ilegal)  

---

## 📂 Estructura del proyecto


.
├── google_maps_scraper.py # Script principal (extracción real)
├── leadscramer.html # Interfaz demo (UI)
├── README.md


---

## 🛠️ Tecnologías

- Python 3  
- Requests  
- Pandas  
- OpenPyXL  
- HTML / CSS / JavaScript  
- Google Places API  

---

## ⚙️ Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/kevinbelmonte50-prog/leadhunter-pro.git
cd leadhunter-pro
Instalar dependencias:
pip install requests pandas openpyxl
🔑 Configuración

Este proyecto requiere una API Key de Google Places.

Pasos:
Ir a: https://console.cloud.google.com
Crear un proyecto
Activar Places API
Crear una API Key
Configurar en el código

En google_maps_scraper.py:

GOOGLE_API_KEY = ""

👉 Pegá tu API Key ahí (solo en local, nunca subirla a GitHub)

▶️ Uso

Ejecutar el script:

python google_maps_scraper.py

Antes de ejecutar, podés configurar:

BUSQUEDA = "agencias de marketing"
CIUDAD   = "Buenos Aires, Argentina"
CANTIDAD = 60
📊 Output

El script genera automáticamente:

leads_*.csv
leads_*.xlsx

Incluye:

Nombre del negocio
Dirección
Teléfono
Sitio web
Rating
Cantidad de reseñas
🖥️ Interfaz Web (Demo)

Abrir en el navegador:

leadscramer.html

👉 Esta interfaz:

Simula generación de leads
Muestra resultados en tiempo real
Permite exportar CSV

⚠️ Es una demo visual (no scrapea datos reales)

⚖️ Legalidad

Este proyecto:

✔ Usa únicamente APIs oficiales
✔ Extrae datos públicos
✔ Respeta los términos de uso de Google

⚠️ No realiza scraping ilegal ni automatización agresiva.

🚀 Próximas mejoras
Integración con APIs de emails (Hunter.io, Apollo)
Dashboard interactivo (Streamlit)
Filtros avanzados de leads
Automatización de outreach
👨‍💻 Autor

Desarrollado por Kevin Belmonte
