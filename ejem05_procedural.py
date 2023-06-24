import requests
from bs4 import BeautifulSoup

def obtener_datos(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    productos = []

    for producto in soup.find_all('div', class_='product'):
        nombre = producto.find('h4', class_='product-name').text.strip()
        precio = producto.find('div', class_='price').text.strip()
        productos.append({'nombre': nombre, 'precio': precio})

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
