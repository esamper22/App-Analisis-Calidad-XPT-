import requests
from bs4 import BeautifulSoup

def obtener_iconos_bootstrap():
    """
    Obtiene una lista de nombres de iconos de Bootstrap desde su sitio web,
    extrayendo el atributo 'data-name' de cada <li> en el listado de iconos.
    """
    url = "https://icons.getbootstrap.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Busca todos los <li> dentro del <ul id="icons-list">
    icon_items = soup.select('ul#icons-list li[data-name]')
    # Extrae el valor del atributo data-name de cada <li>
    
    # Verifica que no tenga valores None ni esté vacía
    iconos_bootstrap = [f'bi bi-{item['data-name']}' for item in icon_items]
    
    # if iconos_bootstrap is None:
    #     iconos_bootstrap = []
    # else:
    #     # Filtra valores None o no string
    #     iconos_bootstrap = [icon for icon in iconos_bootstrap if isinstance(icon, str) and icon]
    
    return iconos_bootstrap

if __name__ == "__main__":
    iconos = obtener_iconos_bootstrap()
    print(iconos)
    print(f"Total de iconos encontrados: {len(iconos)}")
