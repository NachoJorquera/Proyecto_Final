import time
import os
import csv
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import sys

B_VERBOSE_DEBUG = True
B_VERBOSE_RESULT = True

def obtener_uf():
    # Driver y carga de página
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://www.bcentral.cl')

    #
    # Obtener UF por content Selenium + lxml BeautifulSoup
    #
    weUFContent = driver.find_element(By.XPATH, '/html/body/div[1]/section/div/div[2]/div/div/div[1]/section/div/div[2]/div/div/div/div/div[1]/div/div')
    htmlData = weUFContent.get_attribute('innerHTML')
    lxmlData = BeautifulSoup(htmlData, 'lxml')

    listTC = lxmlData.find_all('p', class_='basic-text fs-2 f-opensans-bold text-center c-blue-nb-2')

    # Captura UF
    sUF = listTC[0].string
    sUF = sUF.replace('$', '').replace('.', '').replace(',', '.')
    nUF = float(sUF)

    # Grabar en archivo CSV
    fecha_actual = date.today().strftime('%d/%m/%Y')
    datos_uf = [fecha_actual, nUF]

    with open('parametros.csv', 'a', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv, delimiter=';')

        if archivo_csv.tell() == 0:
            escritor_csv.writerow(['Fecha', 'Valor UF'])
        escritor_csv.writerow(datos_uf)

    # Cierre del driver
    driver.quit()

    print("Información almacenada en parametros.csv") 
    return nUF

def read_search_patterns(file_path):
    with open(file_path, 'r') as file:
        patterns = [line.strip() for line in file]
    return patterns

def runScript(file_path):
    L_FIND = read_search_patterns(file_path)
    main(L_FIND)

def mySleep(nTimeOut):
    time.sleep(nTimeOut)

def mySleepUntilObject(nTimeOut, driver, sXpath):
    while nTimeOut > 0:
        try:
            contentData = driver.find_element(By.XPATH, sXpath)
            return
        except:
            pass
        time.sleep(1)
        nTimeOut -= 1

def clickWithWait(nTimeOut, driver, sXpath):
    while nTimeOut > 0:
        try:
            btnToBeClick = driver.find_element(By.XPATH, sXpath)
            btnToBeClick.click()
            return True
        except:
            pass
        time.sleep(1)
        nTimeOut -= 1
    return False

def outputHtml(sFile, lxmlData):
    with open(sFile, 'w') as fOutputHtml:
        fOutputHtml.write(lxmlData.prettify())

def main(L_FIND):
    listResult = []
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    for S_FIND in L_FIND:
        if B_VERBOSE_DEBUG:
            print('=' * len('Patrón de búsqueda: {}'.format(S_FIND)))
            print('Patrón de búsqueda: {}'.format(S_FIND))
            print('=' * len('Patrón de búsqueda: {}'.format(S_FIND)))

        driver.get('https://www.falabella.com/falabella-cl')
        mySleep(2)
        inputText = driver.find_element(By.XPATH, '//*[@id="testId-SearchBar-Input"]')
        inputText.send_keys(S_FIND)
        inputText.send_keys(Keys.ENTER)
        mySleep(1)

        bOkExistData = False
        try:
            sXpath = '//*[@id="testId-searchResults-products"]'
            btnPage1 = driver.find_element(By.XPATH, sXpath)
            bOkExistData = True
        except:
            if B_VERBOSE_DEBUG:
                print('No hay datos')
            pass

        nPage = 1
        while bOkExistData:
            if B_VERBOSE_DEBUG:
                print('{}: Página {}'.format(S_FIND, nPage))

            try:
                sXpath = '//*[@id="testId-searchResults-products"]'
                mySleepUntilObject(20, driver, sXpath)
                mySleep(2)

                sXpath = '//*[@id="testId-searchResults-products"]'
                contentData = driver.find_element(By.XPATH, sXpath)
                htmlData = contentData.get_attribute('innerHTML')
                lxmlData = BeautifulSoup(htmlData, 'lxml')

                outputHtml('falabella_{}_{}.html'.format(S_FIND, nPage), lxmlData)

                nContentType = 0
                sNames = lxmlData.find_all('div', class_='jsx-1833870204 jsx-3831830274 pod-details pod-details-4_GRID has-stickers')
                if len(sNames) > 0:
                    nContentType = 1
                else:
                    sNames = lxmlData.find_all('b', class_='jsx-1576191951 title2 primary jsx-2889528833 bold pod-subTitle subTitle-rebrand')
                    if len(sNames) > 0:
                        nContentType = 2
                    else:
                        if B_VERBOSE_DEBUG:
                            print('Contenedor no reconocido')
                if B_VERBOSE_DEBUG:
                    print('Tipo contenedor: {}'.format(nContentType))

                if nContentType == 1:
                    sNames = lxmlData.find_all('div', class_='jsx-1833870204 jsx-3831830274 pod-details pod-details-4_GRID has-stickers')
                    sPrices = lxmlData.find_all('a', class_='jsx-1833870204 jsx-3831830274 pod-summary pod-link pod-summary-4_GRID')
                else:
                    sNames = lxmlData.find_all('b', class_='jsx-1576191951 title2 primary jsx-2889528833 bold pod-subTitle subTitle-rebrand')
                    sPrices = lxmlData.find_all('div', class_='jsx-2112733514 prices prices-4_GRID')

                for i in range(len(sNames)):
                    if nContentType == 1:
                        nPrecio = sPrices[i].div.ol.li.div.span.string.replace('$', '').replace(' ', '').replace('.', '')
                        listResult.append({'patron_busqueda': S_FIND, 'nombre': sNames[i].a.span.b.string, 'precio': nPrecio})
                    else:
                        nPrecio = sPrices[i].ol.li.div.span.string.replace('$', '').replace(' ', '').replace('.', '')
                        listResult.append({'patron_busqueda': S_FIND, 'nombre': sNames[i].string, 'precio': nPrecio})

                    if B_VERBOSE_DEBUG:
                        print(listResult[len(listResult) - 1])

                    #Grabar en archivo CSV
                    multitienda = 'Falabella'
                    descripcion = listResult[-1]['nombre']
                    precio_clp = float(listResult[-1]['precio'])
                    precio_uf = precio_clp / valor_uf

                    with open('todosolo.csv', 'a', newline='') as archivo_csv:
                        escritor_csv = csv.writer(archivo_csv, delimiter=';')

                        if archivo_csv.tell() == 0:
                            escritor_csv.writerow(['Patron de búsqueda', 'Multitienda', 'Descripción', 'Precio CLP', 'Precio UF'])
                        escritor_csv.writerow([S_FIND, multitienda, descripcion, int(precio_clp), round(precio_uf, 2)])

                try:
                    sXpath = '//*[@id="testId-pagination-bottom-arrow-right"]/i'
                    contentData = driver.find_element(By.XPATH, sXpath)

                    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                    bOkExistData = clickWithWait(2, driver, sXpath)

                    if not bOkExistData:
                        if B_VERBOSE_DEBUG:
                            print('Reintento con scroll fin + F5')

                        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                        driver.get(driver.current_url)

                        bOkExistData = clickWithWait(2, driver, sXpath)
                        if not bOkExistData:
                            if B_VERBOSE_DEBUG:
                                print('No se logró hacer click a la siguiente página')
                except:
                    if B_VERBOSE_DEBUG:
                        print('No hay más páginas de información')
                    bOkExistData = False
            except:
                if B_VERBOSE_DEBUG:
                    print('Caída al capturar contenedor')
                bOkExistData = False

            nPage += 1

    driver.close()
    driver.quit()

    if B_VERBOSE_RESULT:
        print('=' * len('Lista total:'))
        print('Lista total:')
        print('=' * len('Lista total:'))
        [print('"{}";"{}";{}'.format(item['patron_busqueda'], item['nombre'], item['precio'])) for item in listResult]

    if B_VERBOSE_DEBUG:
        print('Proceso finalizado')

if (__name__ == '__main__'):
    obtener_uf()
    valor_uf = obtener_uf()
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        runScript(file_path)
    else:
        print("Debe proporcionar la ruta del archivo txt con los patrones de búsqueda.")
