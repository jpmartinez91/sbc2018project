#!/usr/bin/python
# -*- coding: utf-8 -*-
from pony.orm import *
from model import Info
from SPARQLWrapper import SPARQLWrapper, JSON
import unicodedata


def formatString( cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    return s.decode()

def reconciliar(data):
    sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        select  * where {
            VALUES ?keyword {'""" +data +"""'} .
            ?n a <http://schema.org/Language>;
            rdfs:label ?a.
            FILTER CONTAINS(?a, ?keyword)
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print "---------------------------"
    print data
    a = results["results"]["bindings"]
    try:
        return a[0]["n"]["value"]
    except Exception as e:
        pass

@db_session
def main():
    data = Info.select_by_sql("SELECT * FROM info")
    dataPais = []
    for d in data:
        predicado = formatString(d.predicado)
        if predicado == 'Idioma':
            if d.objeto not in dataPais:
                dataPais.append(d.objeto)
    for d in range(0, len(dataPais)-1):
        op = reconciliar(dataPais[d])

if __name__ == '__main__':
    main()
