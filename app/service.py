from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_cors import cross_origin
import numpy as np
from pulp import *
import copy
import json
from pyproj import Transformer

def distance(a, b) -> float:
    """ Função para retornar a distância entre dois pontos.

    Args:
        a (list): lista com coordenadas que descreve um ponto.
        b (list): lista com coordenadas que descreve um ponto.

    Returns:
        float: Distância entre os dois pontos como parâmetro.
    """
    return abs(np.linalg.norm(a-b))

trans = Transformer.from_crs( 
    "epsg:4326",
    "+proj=utm +zone=23 +ellps=WGS84",
    always_xy=True,
)


app = Flask(__name__)
CORS(app)

@app.route("/", methods = ['GET'])
def home_view():
        return "<h1>Welcome to API</h1>"

@app.route('/coordinate/', methods = ['POST'])
def post():
    json_data = request.json

    P = json_data['features'][1]['properties']['equipamentos']

    tam = json_data['features'][0]['properties']['points']
    tam2 = json_data['features'][1]['properties']['points']

    I = list(range(0, tam))
    J = list(range(0, tam2))
    S = 2000.0

    d = []
    originalData = copy.deepcopy(json_data)
    for feature in json_data['features']:
        for index in range(0,len(feature['geometry']['coordinates'])):
            feature['geometry']['coordinates'][index] = list(trans.transform(feature['geometry']['coordinates'][index][1],feature['geometry']['coordinates'][index][0]))

    
    for i in I:
        linha = []
        for j in J:
            #print(distance(np.array(data[i]['geometry']['coordinates']), np.array(data[j]['geometry']['coordinates'])))
            linha.append(distance(np.array(json_data['features'][0]['geometry']['coordinates'][i]), np.array(json_data['features'][1]['geometry']['coordinates'][j])))
        d.append(linha)        
        

    N = [[j for j in J if d[i][j] < S] for i in I]

    
    # Formulate optimisation
    prob = LpProblem("MCLP", LpMaximize)
    x = LpVariable.dicts("x", J, 0)
    y = LpVariable.dicts("y", I, 0)

    # Objective
    prob += lpSum([json_data['features'][0]['properties']['pop'][i]*y[i]*json_data['features'][0]['properties']['impacto'][i] for i in I])

    # Constraints
    for i in I:
        prob += lpSum([x[j] for j in N[i]]) >= y[i]

    for j in J:
        prob += x[j] <= 1
        prob += x[j] >= 0

    for i in I:
        prob += y[i] <= 1
        prob += y[i] >= 0

    prob += lpSum([x[j] for j in J]) == P


    # Solve problem
    prob.solve()

    x_soln = np.array([x[j].varValue for j in J])

    # And print some output
    print (("Status:"), LpStatus[prob.status])
    print ("Population Served is = ", value(prob.objective))
    print ("x = ", x_soln)

    dict = { "type" : "Feature", "properties": {}, "geometry": {"type" : "MultiPoint", "coordinates" : []}}
    polygon = []
    
    for x in range(0, tam2):
        if(x_soln[x] ==  1):
            dict["geometry"]["coordinates"].append(originalData['features'][1]['geometry']['coordinates'][x])

    return json.dumps(dict), 201
