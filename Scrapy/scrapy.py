#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from model import Data
from pony.orm import *
from time import sleep

# Save data in database
# Require model.py for mapping the entities in database
@db_session
def add_data(sub, pred, obj):
    try:
        Data(sujeto = sub.strip(),
        predicado = pred.strip(),
        objeto = obj.strip()
        )
    except Exception as e:
        print e
        pass

def main():
    # Driver needed for acces and manipulate the web site with Google- Chrome Browser
    driver = webdriver.Chrome(executable_path="chromedriver")
    # REDIB
    redib(driver)
    # LATINDEX
    latindex(driver)



def redib(driver):
    # Acces to web site
    driver.get("https://goo.gl/hTMYS5")
    # Mapping the web get the URL of information journals
    listsJournals = driver.find_elements_by_class_name("titleSerial")
    containerJournal = []
    for oneJournal in listsJournals:
        # Save the URL
        containerJournal.append(oneJournal.get_attribute('href'))

    # get the web which contains the informacion
    for journal in containerJournal:
        driver.get(journal)
        journalName = driver.find_element_by_class_name("titleRecord").text
        elementJournal = driver.find_elements_by_class_name("table-striped")
        formatsJorunals = driver.find_elements_by_class_name("indicador1")
        formats = getFormats(formatsJorunals)
        add_data(journalName, "formatos", formats)
        for element in elementJournal:
            tabla = element.find_elements_by_tag_name("tr")
            for value in tabla:
                info = value.text.split(":")
                predicado = info[0]
                objeto = value.text.replace(info[0]+": ", "")
                add_data(journalName, predicado, objeto)


def latindex(driver):
    # Acces to web site
    driver.get("http://www.latindex.org/latindex/tablaRegion?id=92&id2=0")
    sleep(10)
    # Mapping the web get the URL of information journals
    # this loop is necessary for load all data that uses javaScript
    for i in range(0, 200):
        print i
        tabla = driver.find_element_by_id("load")
        driver.execute_script("return arguments[0].scrollIntoView();", tabla)
        sleep(2)

    listsJournals0 =  driver.find_elements_by_class_name("td1_tema")
    containerJournal = []
    for i in range(1, len(listsJournals0)):
        a =  driver.find_element_by_xpath("//*[@id='example']/div["+ str(i) +"]/div[1]/a")
        containerJournal.append(a.get_attribute("href"))

    # get the web which contains the informacion
    for journal in containerJournal:
        driver.get(journal)
        journalName = driver.find_element_by_xpath("//*[@id='bloque1']/tbody/tr[1]/td[2]").text
        rows = driver.find_elements_by_class_name("datosrevista")
        for row in rows:
            tr = row.find_elements_by_tag_name("tr")
            for t in tr:
                rr = t.find_elements_by_tag_name("td")
                if len(rr) == 2:
                    predicado = rr[0].text
                    objeto = rr[1].text
                    add_data(journalName, predicado, objeto)

if __name__ == '__main__':
    main()
