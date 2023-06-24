import csv
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# MAIN
if (__name__ == "__main__"):
    # Driver y carga de página
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://www.bcentral.cl')

    #
    # Obtener UF por content Selenium + lxml BeautifulSoup
    #
    #weUFContent = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/section/div/div[2]/div/div/div[1]/section/div/div[2]/div/div/div/div/div[1]/div/div')
    weUFContent = driver.find_element(By.XPATH, '/html/body/div[1]/section/div/div[2]/div/div/div[1]/section/div/div[2]/div/div/div/div/div[1]/div/div')
    htmlData = weUFContent.get_attribute('innerHTML')
    lxmlData = BeautifulSoup(htmlData, 'lxml')

    # Generar html
    '''
    fOutputHtml = open ('bcentral_tc.html','w')
    fOutputHtml.write(lxmlData.prettify())
    fOutputHtml.close()
    '''

    listTC = lxmlData.find_all('p', class_='basic-text fs-2 f-opensans-bold text-center c-blue-nb-2')
    #print("Contenedor tipos de cambio:")
    #for sTC in listTC:
    #    print('{}'.format(sTC.string)) #.replace('\n', '').replace('\t', ''))))
    #print("")
    
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

    print("\n")
    print("Información almacenada en parametros.csv")
   
    # Cierre del driver
    #driver.close()
    driver.quit()
