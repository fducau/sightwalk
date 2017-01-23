from __future__ import unicode_literals

import os
import sys
import inspect
from django.apps import AppConfig

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
base_dir = "/".join(current_dir.split('/')[:-2])
sys.path.insert(0, base_dir)

from Graph.path_optimization import City, initialize

file_path = '../Graph/data_by_edge_final.pkl'

class PathsConfig(AppConfig):
    name = 'paths'

    def __init__(self, app_name, app_module):
        AppConfig.__init__(self, app_name, app_module)
        self.city = None

    def ready(self):
    	if not self.city:
    		self.city = initialize(file_path)

