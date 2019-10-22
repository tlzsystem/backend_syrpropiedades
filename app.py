from flask import Flask, request, json
from flask_cors import CORS

import requests
import datetime
from bs4 import BeautifulSoup

URL_BASE = "https://api.mercadolibre.com/"
URL_SEARCH = 'sites/MLC/search?real_estate_agency=no'

app = Flask(__name__)
CORS(app)

@app.route('/')
def main():
    category = request.args.get('category')
    city = request.args.get('city')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    offset = 0 
    max_data = 1
    payload = {'category': category, 'city': city}
    r = requests.get(URL_BASE + URL_SEARCH, params = payload)
    data =  r.json()
    max_data = data['paging']['total']
    lista_ids = []
    lista_json = []
    
    while offset <= max_data:
        payload = {'category': category, 'city': city, 'offset': offset}
        r = requests.get(URL_BASE + URL_SEARCH, params = payload)
        data =  r.json()
        offset+=50
        if data['results']:
            for result in data['results']:
                lista_ids.append(result['id'])
    
    for idd in lista_ids:
        r = requests.get(URL_BASE + 'items/'+idd )
        data = r.json()
        fecha_desde_string = data['start_time'] 
        date_time_obj = datetime.datetime.strptime(fecha_desde_string[:10],'%Y-%m-%d')
        fecha_inicio_obj  = datetime.datetime.strptime(fecha_inicio, '%d-%m-%Y')
        fecha_fin_obj  = datetime.datetime.strptime(fecha_fin, '%d-%m-%Y')
        if date_time_obj>=fecha_inicio_obj  and date_time_obj <= fecha_fin_obj:
            result = requests.get(data['permalink'])
            if result.status_code == 200:
                c = result.content
                soup = BeautifulSoup(c, 'lxml')

                url = data['permalink']
                valor = soup.select('span.price-tag-fraction:nth-child(2)')[0].string
                nombre_vendedor = soup.select('p.card-description:nth-child(3) > span:nth-child(1)')[0].string
                telefono_uno = soup.select('span.profile-info-phone-value:nth-child(1)')[0].string
                telefono_dos = ''
                fecha_publicacion = fecha_desde_string[:10]
                if soup.select('span.profile-info-phone-value:nth-child(2)'):
                    telefono_dos = soup.select('span.profile-info-phone-value:nth-child(2)')[0].string
                retorno_json = {
                    'url':url,
                    'fecha_publicacion':fecha_publicacion,
                    'valor': valor,
                    'nombre_vendedor': nombre_vendedor,
                    'telefono_uno': telefono_uno,
                    'telefono_dos': telefono_dos
                }
                lista_json.append(retorno_json)

    response = app.response_class(
        response= json.dumps(lista_json),
        status = 200,
        mimetype='application/json'
    )     
    return response
