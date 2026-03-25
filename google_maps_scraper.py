"""
LeadHunter Pro — Google Maps Scraper
=====================================
Extrae leads de negocios locales usando la API oficial de Google Places.
100% legal: solo datos públicos, respeta ToS de Google.

Requisitos:
    pip install requests pandas openpyxl

API Key gratuita:
    1. Ir a https://console.cloud.google.com
    2. Crear proyecto nuevo
    3. Habilitar "Places API"
    4. Crear credencial -> API Key
    5. Pegar tu key abajo en GOOGLE_API_KEY
"""

import requests
import pandas as pd
import time
import json
from datetime import datetime

# ============================================================
# CONFIGURACIÓN — editá estos valores antes de correr
# ============================================================

GOOGLE_API_KEY = "AIzaSyADcvhVR_UcgOHjbCa3scGzBTqiKFvVwPU"   # <-- Pegá tu API Key acá

BUSQUEDA = "agencias de marketing"    # Qué tipo de negocio buscar
CIUDAD   = "Buenos Aires, Argentina"  # Dónde buscar
CANTIDAD = 60                         # Cuántos leads querés (máx ~200)

# ============================================================


BASE_URL = "https://maps.googleapis.com/maps/api/place"


def buscar_negocios(query: str, location: str, max_results: int) -> list[dict]:
    """
    Busca negocios usando Places API Text Search.
    Respeta el límite de requests y pagina automáticamente.
    """
    print(f"\n🔍 Buscando: '{query}' en {location}")
    print(f"   Objetivo: {max_results} leads\n")

    resultados = []
    url = f"{BASE_URL}/textsearch/json"
    params = {
        "query": f"{query} en {location}",
        "key": GOOGLE_API_KEY,
        "language": "es",
    }

    pagina = 1
    while len(resultados) < max_results:
        print(f"   📄 Página {pagina}...")
        resp = requests.get(url, params=params)
        data = resp.json()

        status = data.get("status")
        if status == "REQUEST_DENIED":
            print("❌ API Key inválida. Revisá tu key en https://console.cloud.google.com")
            break
        elif status == "ZERO_RESULTS":
            print("⚠️  Sin resultados. Probá con otro rubro o ciudad.")
            break
        elif status not in ("OK", "ZERO_RESULTS"):
            print(f"⚠️  Status inesperado: {status}")
            break

        resultados.extend(data.get("results", []))
        print(f"   ✅ {len(resultados)} negocios encontrados hasta ahora")

        # Paginación: Google devuelve hasta 20 por página (máx 3 páginas = 60)
        next_token = data.get("next_page_token")
        if not next_token or len(resultados) >= max_results:
            break

        # Google requiere esperar 2s antes de usar next_page_token
        time.sleep(2)
        params = {"pagetoken": next_token, "key": GOOGLE_API_KEY}
        pagina += 1

    return resultados[:max_results]


def obtener_detalle(place_id: str) -> dict:
    """
    Obtiene detalles extendidos de un lugar: teléfono, web, horarios, etc.
    Cada llamada consume 1 request de la API.
    """
    url = f"{BASE_URL}/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_phone_number,website,formatted_address,rating,user_ratings_total,business_status,types",
        "key": GOOGLE_API_KEY,
        "language": "es",
    }
    resp = requests.get(url, params=params)
    return resp.json().get("result", {})


def limpiar_website(url: str) -> str:
    """Limpia la URL para mostrarla más prolija."""
    if not url:
        return ""
    return url.replace("https://", "").replace("http://", "").rstrip("/")


def procesar_leads(raw_results: list[dict]) -> list[dict]:
    """
    Convierte los resultados crudos de Google en leads limpios.
    Obtiene detalles adicionales (teléfono, web) para cada uno.
    """
    leads = []
    total = len(raw_results)

    for i, negocio in enumerate(raw_results, 1):
        place_id = negocio.get("place_id", "")
        nombre   = negocio.get("name", "")

        print(f"   [{i:>3}/{total}] Procesando: {nombre[:45]:<45}", end="\r")

        # Obtener detalles (teléfono, web, etc.)
        detalle = obtener_detalle(place_id)

        # Extraer dominio del sitio web (útil para enriquecer con Hunter.io después)
        website = detalle.get("website", "")
        dominio = limpiar_website(website)

        lead = {
            "Nombre del negocio": nombre,
            "Dirección":          detalle.get("formatted_address", negocio.get("formatted_address", "")),
            "Teléfono":           detalle.get("formatted_phone_number", ""),
            "Sitio web":          dominio,
            "Rating Google":      negocio.get("rating", ""),
            "Cantidad reseñas":   negocio.get("user_ratings_total", ""),
            "Estado":             detalle.get("business_status", "OPERATIONAL"),
            "Place ID":           place_id,
        }

        leads.append(lead)

        # Pausa respetuosa entre requests (evita rate limiting)
        time.sleep(0.15)

    print()  # Nueva línea después del carriage return
    return leads


def exportar(leads: list[dict], query: str) -> str:
    """
    Exporta los leads a CSV y Excel.
    Devuelve el nombre base del archivo generado.
    """
    if not leads:
        print("⚠️  No hay leads para exportar.")
        return ""

    df = pd.DataFrame(leads)

    # Filtrar negocios sin teléfono ni web (menos útiles como leads)
    df_completos = df[
        (df["Teléfono"] != "") | (df["Sitio web"] != "")
    ].copy()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    slug      = query.replace(" ", "_").lower()[:20]
    base      = f"leads_{slug}_{timestamp}"

    # Guardar CSV
    csv_path = f"{base}.csv"
    df_completos.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # Guardar Excel con formato
    xlsx_path = f"{base}.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df_completos.to_excel(writer, index=False, sheet_name="Leads")

        # Ajustar ancho de columnas
        ws = writer.sheets["Leads"]
        for col in ws.columns:
            max_len = max(len(str(c.value or "")) for c in col) + 2
            ws.column_dimensions[col[0].column_letter].width = min(max_len, 50)

    print(f"\n📁 Archivos generados:")
    print(f"   • {csv_path}  ({len(df_completos)} leads)")
    print(f"   • {xlsx_path} ({len(df_completos)} leads)")

    # Mostrar resumen
    con_tel  = (df_completos["Teléfono"] != "").sum()
    con_web  = (df_completos["Sitio web"] != "").sum()
    print(f"\n📊 Resumen:")
    print(f"   • Total leads: {len(df_completos)}")
    print(f"   • Con teléfono: {con_tel} ({con_tel/len(df_completos)*100:.0f}%)")
    print(f"   • Con sitio web: {con_web} ({con_web/len(df_completos)*100:.0f}%)")
    print(f"   • Rating promedio: {df_completos['Rating Google'].mean():.1f} ⭐")

    return base


def main():
    print("=" * 55)
    print("  LeadHunter Pro — Google Maps Scraper")
    print("  Solo datos públicos | Respeta ToS de Google")
    print("=" * 55)

    if GOOGLE_API_KEY == "TU_API_KEY_AQUI":
        print("\n❌ Configurá tu API Key primero.")
        print("   1. Ir a https://console.cloud.google.com")
        print("   2. Habilitar Places API")
        print("   3. Crear API Key y pegarlo arriba en el script")
        return

    # 1. Buscar negocios
    raw = buscar_negocios(BUSQUEDA, CIUDAD, CANTIDAD)

    if not raw:
        print("No se encontraron resultados.")
        return

    # 2. Enriquecer con detalles
    print(f"\n🔎 Obteniendo detalles de {len(raw)} negocios...")
    leads = procesar_leads(raw)

    # 3. Exportar
    exportar(leads, BUSQUEDA)

    print("\n✅ ¡Listo! Podés abrir el Excel y entregar los leads al cliente.")
    print("💡 Próximo paso: agregar Hunter.io para obtener emails por dominio.\n")


if __name__ == "__main__":
    main()