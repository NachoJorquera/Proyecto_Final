import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import sys

B_VERBOSE_DEBUG = True
B_VERBOSE_RESULT = True

L_FIND = ['notebook hp', 'tablet samsung', 'impresora 3D', 'MacBook Pro', 'jkljkljkl']

def runScript():
    main()
    
def mySleep(nTimeOut):
    nTimeInit = time.time()
    nTimeDifference = time.time() - nTimeInit
    while nTimeDifference < nTimeOut:
        nTimeDifference = time.time() - nTimeInit

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
    fOutputHtml = open(sFile, 'w')
    fOutputHtml.write(lxmlData.prettify())
    fOutputHtml.close()

def main():
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

if (__name__ = '__main__'):
    runScript()
