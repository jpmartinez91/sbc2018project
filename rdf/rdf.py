#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rdflib import BNode, ConjunctiveGraph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import FOAF, DC, DCTERMS, SKOS, OWL, XSD, RDFS
from model import Info
import re
from pony.orm import *
import unicodedata

# storefn = os.path.expanduser('~/movies.n3')
storeuri = '_____dir____/ultima.xml'

dbo = Namespace("http://dbpedia.org/ontology/")
bibo = Namespace("http://purl.org/ontology/bibo/")
vivo = Namespace("http://vivoweb.org/ontology/core#")
ns = Namespace("http://utpl.edu.ec/sbc2018/jpmartinez91/resource/")

class Generator():
    """docstring for Generator."""
    def __init__(self):
        self.graph = ConjunctiveGraph()
        self.graph.bind('dct', DCTERMS)
        self.graph.bind('owl', OWL)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('foaf', FOAF)
        self.graph.bind('skos', SKOS)
        self.graph.bind('dbo', dbo)
        self.graph.bind('vivo', vivo)
        self.graph.bind('bibo', bibo)
        self.graph.bind('sbc', ns)

    def save(self):
        self.graph.serialize(storeuri, format='xml')

    # quitar acentos y caracteres especiales de utf-8
    def formatString(self, cadena):
        try:
            s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
            return s.decode()
        except Exception as e:
            return cadena


    # remplazar caracteres no validos en URLs
    def cleanString(self, cadena):
        quitar = [".","-",'"',"/",",", "'",":",";","@","[","]","{","}", "(",")"]
        st = cadena.strip().replace(" ","_")
        for q in quitar:
            st = st.replace(q,"")
        return self.formatString(st.title())


    def resourceOrg(self, titulo, alternativo, pais, web, desc, editorial, direccion, email, formatos, idioma, notas, temas, subtemas, DOI):
        nombreOrgDoc = self.cleanString(titulo)
        nombreEdit = self.cleanString(editorial)
        # Create Resource Organization
        org = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Org/%s/' % nombreOrgDoc)
        # Create Resource Documento
        doc = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Doc/%s/' % nombreOrgDoc)
        # Create Resource Editorial
        edi = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Edit/%s/' % nombreEdit)

        ### <----============ E D I T O R A L  ============----> ###
        #   Editorial tipo Editorial
        self.graph.add((edi, RDF.type, vivo.Publisher))
        #   Editorial nombre ___
        self.graph.add((edi, FOAF.name, Literal(editorial.title().strip(), datatype=XSD.string)))
        #   Si hay email => Editorial mail ___
        if email != None:
            self.graph.add((edi, FOAF.mbox, Literal(email, datatype=XSD.string)))
        if direccion != None:
            dir = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Dir/%s/' % self.cleanString(direccion))
            self.graph.add((dir, RDF.type, dbo.Place))
            self.graph.add((dir, RDFS.label, Literal(direccion.title(), datatype=XSD.string)))
            self.graph.add((edi, dbo.address, dir))

        ### <----============ D O C U M E N T O  ============----> ###
        #   Documento Tipo revista
        self.graph.add((doc, RDF.type, bibo.Journal))
        #   Documento nombre ___
        self.graph.add((doc, DCTERMS.title, Literal(titulo.title().strip(), datatype=XSD.string)))
        #   Documento tiene Editorial ___
        self.graph.add((doc, DCTERMS.publisher, edi))
        if notas != None:
            self.graph.add((doc, SKOS.note, Literal(notas, datatype=XSD.string)))
        self.graph.add((doc, bibo.doi, Literal(DOI, datatype=XSD.string)))
        ##### E N T I D A D --> O T R O S N O M B R E S ######
        if alternativo != None:
            for i in alternativo:
                self.graph.add((doc, DCTERMS.alternative, Literal(i.title().strip(), datatype=XSD.string)))


        ##### D O C U M E N T ---> T E M A S  ######
        if temas != None:
            for i in temas:
                nueva = i.split(" -->")
                if len(nueva) > 1:
                    temaName = self.cleanString(nueva[0])
                    temaName2 = self.cleanString(nueva[1])
                    # Create Resource subject
                    tem = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Tema/%s/' % temaName)
                    tem2 = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Tema/%s/' % temaName2)
                    self.graph.add((tem, RDF.type, SKOS.Concept))
                    self.graph.add((tem, RDFS.label, Literal(nueva[0].title().strip(), datatype=XSD.string)))
                    self.graph.add((tem2, RDF.type, SKOS.Concept))
                    self.graph.add((tem2, RDFS.label, Literal(nueva[1].title().strip(),datatype=XSD.string)))
                    self.graph.add((tem, SKOS.broader, tem2))
                    # Add subject to listaTemas
                    self.graph.add((doc, DCTERMS.subject, tem))
                else:
                    temaName = self.cleanString(i)
                    tem = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Tema/%s/' % temaName)
                    self.graph.add((tem, RDF.type, SKOS.Concept))
                    self.graph.add((tem, RDFS.label, Literal(i.title().strip(), datatype=XSD.string)))
                    # si hay subtema agregalo
                    if subtemas != None:
                        for a in subtemas:
                            tem2 = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Tema/%s/' % self.cleanString(a))
                            self.graph.add((tem2, RDF.type, SKOS.Concept))
                            self.graph.add((tem2, RDFS.label, Literal(a.title().strip(), datatype=XSD.string)))
                            self.graph.add((tem, SKOS.broader, tem2))
                    # Add subject to listaTemas
                    self.graph.add((doc, DCTERMS.subject, tem))

        ##### D O C U M E N T ---> I D I O M A S ######
        if idioma != None:
            for d in idioma:
                # Formatear Idioma
                idiom = self.cleanString(d["propio"])
                idm = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Idioma/%s/' % idiom)
                self.graph.add((idm, OWL.sameAs, URIRef(d["recon"])))
                self.graph.add((idm, RDFS.label, Literal(d["propio"].title().strip(), datatype=XSD.string)))
                # Si hay idioma en es.dbpedia agregalo
                self.graph.add((idm, RDF.type, dbo.Language))
                # Agregar a Documento
                self.graph.add((doc, dbo.language, idm))

        ### <----============ O R G A N I Z A C I O N   ============----> ###
        # Entidad tipo org
        self.graph.add((org, RDF.type, FOAF.Organization))
        # Entidad tipo Association
        self.graph.add((org, RDF.type, vivo.Association))
        # Entidad nombre _____
        self.graph.add((org, FOAF.name, Literal(titulo.title(), datatype=XSD.string)))

        if pais != None:
            for p in pais:
                pp = self.cleanString(p["propio"])
                pa = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Pais/%s/' % pp)
                self.graph.add((pa, RDF.type, dbo.Country))
                self.graph.add((pa, RDFS.label, Literal(p["propio"].title().strip(), datatype=XSD.string)))
                self.graph.add((pa, OWL.sameAs, URIRef(p["recon"])))
                self.graph.add((org, dbo.country, pa))

        if web != None:
            page = URIRef('http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Web/%s/' % web)
            self.graph.add((page, RDF.type, FOAF.Document))
            self.graph.add((page, RDFS.label, Literal(web.lower().strip(), datatype=XSD.string)))
            self.graph.add((org, FOAF.homapage, page))
        if desc != None:
            self.graph.add((org, DCTERMS.description, Literal(desc)))
        self.graph.add((org, FOAF.made, doc))
        self.save()

@db_session
def main():
    gen = Generator()
    titulos = select(p.sujeto for p in Info)
    for titulo in titulos:
        editorail = None
        direccion = None
        email = None
        alternativo = []
        pais = None
        inicio = None
        fin = None
        web = None
        desc = None
        notas = None
        frecuencia = None
        formatos = []
        idioma = []
        DOI = None
        temas = []
        paisl = []
        subtemas = []
        dbpIdioma = []
        dataJournal = Info.select(lambda p: p.sujeto == titulo)
        for data in dataJournal:
            predicado = gen.formatString(data.predicado)
            objeto = data.objeto
            if (predicado == "Entidad editora") or (predicado == "Editorial"):
                editorail = objeto
            if (predicado == "Direccion del editor"):
                direccion = objeto
            if (predicado == "Correo electronico"):
                email = objeto
            if (predicado == "Otros Títulos") or (predicado == "Tiitulo posterior"):
                alternativo.append(objeto)
            if (predicado == "Pais"):
                pai = {"propio": objeto,"recon": data.reconciliation}
                paisl.append(pai)
            if (predicado == "Ano de inicio"):
                inicio = objeto
            if (predicado == "Ano de Terminacion"):
                fin = objeto
            if (predicado == "Web de la revista"):
                web = objeto
            if (predicado == "Descripcion"):
                desc = objeto
            if (predicado == "Notas"):
                notas = objeto
            if (predicado == "Periodicidad") or (predicado == "Frecuencia"):
                frecuencia = objeto
            if (predicado == "formatos") or (predicado == "Soporte"):
                formatos.append(objeto)
            if (predicado == "Idioma"):
                pai = {"propio": objeto,"recon": data.reconciliation}
                idioma.append(pai)
            if (predicado == "DOI"):
                DOI = objeto
            if (predicado == "Materias") or (predicado == "Temas"):
                temas.append(objeto)
            if (predicado == "Subtemas"):
                subtemas.append(objeto)
        gen.resourceOrg(titulo, alternativo, paisl, web, desc, editorail, direccion, email, formatos, idioma, notas, temas, subtemas, DOI)

if __name__ == '__main__':
    main()
