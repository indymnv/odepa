# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 11:27:21 2020

@author: inavarro
"""

#Cargar todos los paquetes necesarios:

from selenium import webdriver
from importlib import reload
import pandas as pd
import lxml
from selenium.webdriver.support.ui import Select
from pandas import ExcelWriter
import sys
reload(sys)
import time
import warnings

warnings.filterwarnings("ignore")
#Script 1: Elaboración ODEPA

#Especifica directorio donde guarda la información:
directorio="../odepa"

#Abre Chrome y la página web y ejecuta los clicks necesarios:
driver = webdriver.Chrome('/Users/indynavarro/Desktop/projects/odepa/chromedriver')
#driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("http://aplicativos.odepa.cl/recepcion-industria-lactea.do")
driver.find_element_by_id('tipoConsulta2').click()
driver.find_element_by_id('filterByRegionOrPlanta2').click()
driver.find_element_by_id('filterByRegionOrPlanta2').click()
#Extract the list of years
driver.find_element_by_xpath('//*[@id="divFechaDetalleMensual"]/img').click()
driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div[1]/div/select').click()
years = driver.find_elements_by_tag_name("option")
list_years = []
for year in years:
    list_years.append(year.get_attribute('value'))
    
list_years = [element for element in list_years if element != '' and int(element)> 2000]

#Extrae la lista de plantas cargadas:
plantasposibles=driver.find_element_by_id('planta')
plantasposibles=plantasposibles.find_elements_by_tag_name("option")
valoresplantas=[]
nombresplantas=[]

for option in plantasposibles:
    valoresplantas.append(option.get_attribute("value"))
    nombresplantas.append(option.get_attribute("text"))

 
#Extrae el último año que tiene información cargada (y lo guarda para actualizar sólo ese año)
lastyear=driver.find_element_by_id('fechaDetalleMensual').get_attribute("value")
#lastyear = 2022
#Crea una tabla y la rellena con la información de cada planta:
tabla=pd.DataFrame()

driver.find_element_by_xpath('//*[@id="divFechaDetalleMensual"]/img').click()
#driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div[1]/div/select').click()
for lastyear in list_years:    #then replace for list_years:
    for i in range(1,len(valoresplantas)):
        #Solicita la información de la planta correspondiente y el año correspondiente, y luego presiona botón "Ver Informe"
        try: 
            driver.execute_script("document.getElementById('planta').value="+ valoresplantas[i])
            driver.find_element_by_xpath("//*[@id='divFechaDetalleMensual']/img").click()
            time.sleep(1)
            select=Select(driver.find_element_by_xpath("//*[@id='ui-datepicker-div']/div[1]/div/select"))
            select.select_by_visible_text(str(lastyear))        
            driver.find_element_by_xpath("//*[@id='ui-datepicker-div']/div[2]/button").click()
            driver.find_element_by_id('fechaDetalleMensual').send_keys(lastyear)
            timeout=15
            driver.find_element_by_id('btnVerInforme').click()
            timeout=20
            
            #Extrae la información de la tabla html, eliminando filas y columnas innecesarias. Concatena la información de todas las
            #plantas en una tabla llamada "tabla". 
            
            prueba_html=driver.page_source
            df = pd.read_html(prueba_html, flavor='html5lib')[0]
            df=df.drop(df.columns[14:397],axis=1)
            df=df.drop(df.index[0:8],axis=0)
            df=df.drop(df.index[1],axis=0)
            df=df.drop(df.index[8:9],axis=0)
            df['Year']=lastyear
            df['Factory_Name']=nombresplantas[i]
            tabla=pd.concat([tabla,df])
        except:
            #If fail close and open up the window again
            #driver.quit()
            time.sleep(5)
            driver.get("http://aplicativos.odepa.cl/recepcion-industria-lactea.do")
            time.sleep(5)
            driver.find_element_by_id('tipoConsulta2').click()
            driver.find_element_by_id('filterByRegionOrPlanta2').click()
            driver.find_element_by_id('filterByRegionOrPlanta2').click()

print(tabla)
print(tabla.columns.tolist())
#tabla=tabla[['Año', 'Planta', 'Producto', 'Unidad','Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']]

tabla = tabla[['Year','Factory_Name','Producto', 'Unidad', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']]

lista=range(len(tabla.index))
tabla.index=lista

#Dado que los meses estan almacenados en columnas, se hace una transformación para que queden como BBDD:
tablafinal=pd.DataFrame()
tablaparcial=tabla.drop(tabla.columns[4:],axis=1)

for month in tabla.columns[4:len(tabla.columns)]:

    tablaparcial['Month']=month
    tablaparcial['Quantity']=tabla[month]
    tablafinal=pd.concat([tablafinal,tablaparcial]) 

#Cerrar explorador y guardar tabla en el directorio con el año en el nombre de archivo:
driver.quit()    
#writer = ExcelWriter(directorio+'/elaboracion_lactea_chile.xlsx', engine='xlsxwriter')
#tablafinal.to_excel(writer,'Sheet1')
#writer.save()

#tablafinal.to_csv(r'elaboracion_lactea_chile_2.csv',index=False)
####################################################################################################

def delete_dot(number):
    number=number.replace('.','')
    return number
#Lee
#df=pd.read_excel('elaboracion_lactea_chile.xlsx')
#Remueve valores innecesarios
tablafinal=tablafinal[(tablafinal.Quantity !='Otros productos lácteos') &
      (tablafinal.Quantity != 'Fuente: elaborado por Odepa en base a antecedentes proporcionados por las plantas lecheras.') & 
      (tablafinal.Quantity != 'Leche en polvo') & (tablafinal.Quantity != 'Leche fluida elaborada')]
#borra los puntos y transforma a int
tablafinal['Quantity']=tablafinal.apply(lambda x: delete_dot(x['Quantity']), axis=1)

tablafinal['Quantity']=tablafinal['Quantity'].astype(int)
#Dataframe a excel
tablafinal.to_csv(r'elaboracion_lactea_chile_3.csv',index=False)

