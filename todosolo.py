import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def mySleep(nTimeOut):
    time.sleep(nTimeOut)

def mySleepUntilObject(nTimeOut, driver, sXpath):
    nTimeInit = time.time()
    nTimeDifference = time.time() - nTimeInit
    bContinuar = True
    while nTimeDifference < nTimeOut and bContinuar:
        nTimeDifference = time.time() - nTimeInit
        try:
            contentData = driver.find_element(By.XPATH, sXpath)
            bContinuar = False
        except:
            pass

def clickWithWait(nTimeOut, driver, sXpath):
    nTimeInit = time.time()
    nTimeDifference = time.time() - nTimeInit
    bContinuar = True
    bClickDone = False
    while nTimeDifference < nTimeOut and bContinuar:
        nTimeDifference = time.time() - nTimeInit
        try:
            btnToBeClick = driver.find_element(By.XPATH, sXpath)
            btnToBeClick.click()
            bContinuar = False
            bClickDone = True
        except:
            pass
    return bClickDone

def outputHtml(sFile, lxmlData):
    with open(sFile, 'w') as fOutputHtml:
        fOutputHtml.write(lxmlData.prettify())

def get_valor_uf(driver):
    sXpath_uf = '//*[@id="_BcentralIndicadoresViewer_INSTANCE_pLcePZ0Eybi8_myTooltipDelegate"]/div/div/div[1]/div/div/div[1]/div/p[2]'
    valor_uf = driver.find_element(By.XPATH, sXpath_uf).text
    return valor_uf

def get_fecha_actual(driver):
    sXpath_fecha = '//*[@id="_BcentralIndicadoresViewer_INSTANCE_pLcePZ0Eybi8_myTooltipDelegate"]/div/div/div[1]/p'
    fecha_actual = driver.find_element(By.XPATH, sXpath_fecha).text
    return fecha_actual

def process_falabella_pages(driver, search_terms):
    listResult = []
    for S_FIND in search_terms:
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

        result = {
            'patron_busqueda': S_FIND,
            'multitienda': 'Falabella',
            'descripcion': 'Nombre del producto',
            'precio_pesos': 'Precio del producto'
        }
        listResult.append(result)

    return listResult

def write_to_csv(data, filename):
    keys = data[0].keys() if data else []
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def main():
    B_VERBOSE_DEBUG = True
    B_VERBOSE_RESULT = True

    L_FIND = ['notebook hp', 'tablet samsung', 'impresora 3D', 'MacBook Pro', 'jkljkljkl']

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    listResult = []

    for nPage in range(1, len(L_FIND) + 1):
        S_FIND = L_FIND[nPage - 1]

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
        
        while bOkExistData:
            if B_VERBOSE_DEBUG:
                print('{}: Página {}'.format(S_FIND, nPage))

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

            # Procesar datos según el tipo de contenido

        if not bOkExistData and B_VERBOSE_DEBUG:
            print('No hay datos en la página {}'.format(nPage))

    driver.close()
    driver.quit()

    if B_VERBOSE_RESULT:
        print('=' * len('Lista total:'))
        print('Lista total:')
        print('=' * len('Lista total:'))
        [print('"{}";"{}";{}'.format(item['patron_busqueda'], item['descripcion'], item['precio_pesos'])) for item in listResult]

    if B_VERBOSE_DEBUG:
        print('Proceso finalizado')

    write_to_csv(listResult, 'todosolo.csv')

if __name__ == "__main__":
    main()
