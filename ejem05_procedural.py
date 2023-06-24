from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def obtener_datos(url):
    options = Options()
    options.add_argument("--headless")  # Ejecutar Chrome en modo headless, sin interfaz gráfica
    service = Service('path/to/chromedriver')  # Reemplaza 'path/to/chromedriver' por la ubicación de tu chromedriver
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    productos = []

    for producto in soup.find_all('div', class_='product'):
        nombre = producto.find('h4', class_='product-name').text.strip()
        precio = producto.find('div', class_='price').text.strip()
        productos.append({'nombre': nombre, 'precio': precio})

    driver.quit()

    return productos

def imprimir_productos(productos):
    for producto in productos:
        print(f"Nombre: {producto['nombre']}")
        print(f"Precio: {producto['precio']}")
        print("------------")

def main():
    url = 'https://www.falabella.com/falabella-cl/category/cat1350076/Televisores'
    productos = obtener_datos(url)
    imprimir_productos(productos)

if __name__ == "__main__":
    main()
