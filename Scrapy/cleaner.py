#!/usr/bin/python
# -*- coding: utf-8 -*-

from pony.orm import *
from model import Data
from model import Info

def review(sujeto, predicado, objeto):
    objeto = objeto.split("\n")
    for retornoCarro in objeto:
        if retornoCarro != "Materias:":
            add_data(sujeto, predicado, retornoCarro)

@db_session
def add_data(sub, pred, obj):
    try:
        Info(sujeto = sub.strip(),
        predicado = pred.strip(),
        objeto = obj.strip()
        )
    except Exception as e:
        print sub
        print pred
        print obj
        pass

def limpiador(sujeto, predicado, objeto):
    print "original"
    print objeto
    listaObjs = objeto.split(',')
    if len(listaObjs) > 1:
        print len(listaObjs)
        if listaObjs[0].strip() != '':
            for a in listaObjs:
                add_data(sujeto, predicado, a)
    else:
        lista2 = objeto.split("\n")
        if len(lista2) > 1:
            print len(lista2)
            if lista2[0].strip() != '':
                for a in lista2:
                    add_data(sujeto, predicado, a)
        else:
            add_data(sujeto, predicado, objeto)

@db_session
def main():
    data = Data.select_by_sql("SELECT * FROM data")

    limpiar = ['Idioma','País', 'formatos']
    for dato in data:
        sujeto = dato.sujeto
        predicado = dato.predicado
        objeto = dato.objeto
        if predicado in limpiar:
            limpiador(sujeto, predicado, objeto)
        else:
            if predicado == "Materias":
                review(sujeto, predicado, objeto)
            else:
                add_data(sujeto, predicado, objeto)

@db_session
def igualar():
    data = Info.select_by_sql("SELECT * FROM info)
    for d in data:
        if d.predicado == "Entidad editora":
            d.predicado = "Editorial"

        if d.predicado == "Entidad editora":
            d.predicado = "Temas"

if __name__ == '__main__':
    igualar()
    main()
