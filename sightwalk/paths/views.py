import json
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from django.apps import apps
from Graph.path_optimization import City

class Query:
    def __init__(self, query_params, type_='shortest'):
        self.origin = [float(elem.strip()) for elem in query_params['origin'].split(',')][::-1]
        self.destination = [float(elem.strip()) for elem in query_params['destination'].split(',')][::-1]
        self.type_ = type_
        if not type_ == 'shortest':
            self.touristic = float(query_params['touristic'])
            self.popular = float(query_params['popular'])
            self.time = float(query_params['time'])

    def get_input_params(self):
        if self.type_ == 'shortest':
            res = [self.origin, self.destination]
        else:
            res = [self.origin, self.destination, self.touristic, self.popular, self.time]
        return res

def index(request):
    context = {
        "test_list": []
    }
    return render(request, 'paths/index.html', context)

def score(request):
    geoJSON = open('../Graph/score_edges.geojson', 'r').read()
    return HttpResponse(json.dumps(geoJSON), content_type='application/json')


def shortest(request):
    query_params = Query(request.GET)
    print()

    city = apps.get_app_config('paths').city
    shortest_path = city.shortest_path(*query_params.get_input_params())
    return HttpResponse(json.dumps(shortest_path), content_type='application/json')

def interesting(request):
    request_params = request.GET
    query_params = Query(request_params, 'interesting')
    city = apps.get_app_config('paths').city

    print 'query_params', query_params

    if request_params['rand'] == 'true': # Randomized Dijkstra
        interesting_paths = city.randomized_optimal_path(*query_params.get_input_params())
    else: # A*
        interesting_paths = city.heuristic_optimal_path(*query_params.get_input_params())

    return HttpResponse(json.dumps(interesting_paths), content_type='application/json')

