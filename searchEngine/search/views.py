# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.generic import View
from SPARQLWrapper import SPARQLWrapper, JSON
from models import Resource
from django.http import JsonResponse, HttpResponse, HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse
import unicodedata

# Create your views here.
class Index(View):
    template_name = 'index.html'

    def get(self, request):
        data = {
        'head_title': 'UTPL-SBC|2018',
        }
        return render(request, self.template_name, data)

class Fuentes(View):
    template_name = 'fuentes.html'

    def get(self, request):
        data = {
        'head_title': 'FUENTES-SBC|2018',
        }
        return render(request, self.template_name, data)


class Buscador(View):
    template_name = 'buscador.html'
    def get(self, request):
        data = {
        'head_title': 'FUENTES-SBC|2018'
        }
        return render(request, self.template_name, data)

def formatString(cadena):
    try:
        s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
        return s.decode()
    except Exception as e:
        return cadena

@csrf_exempt
def SimpleSearch(request):
    valor = None
    preQ = ""
    if "Revista" in request.POST:
        valor = request.POST["Revista"]
        preQ = """
        SELECT DISTINCT * WHERE {
        ?s rdf:type foaf:Organization;
        foaf:name ?n;
        dbo:country ?p.
        ?p rdfs:label ?m.
        }"""
    if "Editorial" in request.POST:
        valor = request.POST["Editorial"]
        preQ = """
        SELECT DISTINCT * WHERE {
        ?s rdf:type vivo:Publisher;
        foaf:name ?n.
        OPTIONAL{
            ?s foaf:mbox ?mail.
        }
        }"""
    if "Pais" in request.POST:
        valor = request.POST["Pais"]
        preQ = """
        PREFIX data: <http://utpl.edu.ec/sbc2018/jpmartinez91/resource/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX bibo: <http://purl.org/ontology/bibo/>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT * WHERE {
        {
            ?s rdf:type dbo:Country;
            rdfs:label ?n;
            owl:sameAs ?dbo.
        }
            SERVICE <http://es.dbpedia.org/sparql>{
            ?dbo rdf:type dbo:Country;
            rdfs:comment ?resena.
            }
        }
        """
    template_name = 'buscador.html'
    info = []
    endPoint = SPARQLWrapper("http://localhost:8890/sparql/sbc2018")
    endPoint.setQuery("""
        PREFIX data: <http://utpl.edu.ec/sbc2018/jpmartinez91/resource/>
        PREFIX core: <http://utpl.edu.ec/sbc2018/jpmartinez91/onto#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX bibo: <http://purl.org/ontology/bibo/>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        """ + preQ
        )
    endPoint.setReturnFormat(JSON)
    results = endPoint.query().convert()
    datos = results["results"]["bindings"]
    pais = []
    for result in datos:
        if "Editorial" in request.POST:
            resource = Resource(result["s"]["value"])
            resource.recurso = result["s"]["value"]
            resource.nombre = result["n"]["value"]
            resource.email = result["mail"]["value"] if ("mail" in result) else None
            info.append(resource)
        if "Pais" in request.POST:
            resource = Resource(result["s"]["value"])
            resource.recurso = result["s"]["value"]
            resource.nombre = result["n"]["value"]
            resource.resena = result["resena"]["value"]
            info.append(resource)
        if "Revista" in request.POST:
            resource = Resource(result["s"]["value"])
            nueva = result["s"]["value"]
            nueva = nueva.split("http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Org/")
            resource.recurso = formatString(nueva[1])
            resource.nombre = result["n"]["value"]
            resource.pais = result["m"]["value"]
            info.append(resource)
    # data['results'] = info
    da = {
    'head_title': valor+'-SBC|2018',
    'results': info,
    'tipo' : valor
    }
    return render(request, 'buscador.html', da)

def api_pais_search(request):
    pais = request.GET["pais_id"]
    pais = pais.split("#")[1]
    info = []
    endPoint = SPARQLWrapper("http://localhost:8890/sparql/sbc2018")
    endPoint.setQuery("""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX bibo: <http://purl.org/ontology/bibo/>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
         SELECT DISTINCT ?s ?des ?n ?pm ?mb ?h ?ppp WHERE {
        ?s dbo:country <http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Pais/"""+pais +"""/>;
        rdf:type foaf:Organization;
        foaf:name ?n;
        foaf:homapage ?h;
        dct:description ?des;
        foaf:made ?b.
        ?h rdfs:label ?ppp.
        ?b dct:publisher ?p.
        ?p foaf:name ?pm;
        foaf:mbox ?mb.
        }
        """
        )
    endPoint.setReturnFormat(JSON)
    results = endPoint.query().convert()
    datos = results["results"]["bindings"]
    for result in datos:
        a = {}
        a["recurso"] = result["s"]["value"]
        a["nombre"] = result["n"]["value"]
        a["editor"] = result["pm"]["value"]
        a["emb"] = result["mb"]["value"]
        a["hm"] = result["ppp"]["value"]
        a["des"] = result["des"]["value"]
        info.append(a)
    return JsonResponse({"data":info}, safe=False)

def api_revista(request, revista):
    template = loader.get_template('detalle.html')
    info = []
    print "http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Org/"+revista
    endPoint = SPARQLWrapper("http://localhost:8890/sparql/sbc2018")
    endPoint.setQuery("""
        PREFIX data: <http://utpl.edu.ec/sbc2018/jpmartinez91/resource/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX bibo: <http://purl.org/ontology/bibo/>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {
        {
        <http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Org/"""+revista+"""/>   a foaf:Organization;
        foaf:name ?n;
        foaf:made ?made;
        dbo:country ?pais.
        ?pais rdfs:label ?p.
        ?made dct:publisher ?pub.
        ?pub foaf:name ?pubName.
        OPTIONAL{
        ?made dbo:language ?lan.
        ?lan rdfs:label ?language.
        }
        OPTIONAL{
        ?pub foaf:mbox ?mail.
        }
        OPTIONAL{
              {
              <http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Org/"""+revista+"""/> dct:description ?des;
              foaf:homapage ?w.
              ?w rdfs:label ?web.
              ?made dct:subject ?sub;
              bibo:doi ?doi.
              ?sub rdfs:label ?subject.
              }

               }
          }
          OPTIONAL{
            <http://utpl.edu.ec/sbc2018/jpmartinez91/resource/Org/"""+revista+"""/> dbo:country ?pais.
            ?pais owl:sameAs ?dbo.
            SERVICE <http://es.dbpedia.org/sparql>
            {
            ?dbo rdf:type dbo:Country;
            rdfs:comment ?resena.
            }
          }
        }
        """
        )
    endPoint.setReturnFormat(JSON)
    results = endPoint.query().convert()
    datos = results["results"]["bindings"]
    des = None
    hom = None
    name = None
    doi = None
    pais = None
    resena = None
    language =None
    pubName = None
    mail = None
    for result in datos:
        print result
        a = {}
        name = result["n"]["value"]
        des = result["des"]["value"] if ("des" in result) else "Descripcion no disponible"
        hom = result["web"]["value"] if ("web" in result) else "Sin registro de dirección web "
        pais = result["p"]["value"] if ("p" in result) else None
        doi = result["doi"]["value"] if ("doi" in result) else "DOI no identificado"
        resena = result["resena"]["value"]  if ("resena" in result) else "Información no disponible "
        a["tema"] = result["subject"]["value"] if ("subject" in result) else "Sin temas que mostar"
        a["language"] = result["language"]["value"] if ("language" in result) else "No se encontrarón idiomas"
        pubName = result["pubName"]["value"] if ("pubName" in result) else None
        mail = result["mail"]["value"] if ("mail" in result) else "Sin email que mostrar"
        info.append(a)

    da = {
    'head_title': 'Revista-SBC|2018',
    'results': info,
    'nombre': name,
    'des': des,
    'home':hom,
    'doi':doi,
    "pais": pais,
    "resena":resena,
    "pubName":pubName,
    "mail" : mail
    }
    return HttpResponse(template.render(da, request))

def api_temas(request):
    titulo = request.GET["tituo_n"]
    print titulo
    return JsonResponse({"data":'info'}, safe=False)
