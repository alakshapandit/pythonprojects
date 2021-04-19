from django.apps import AppConfig
import sys
sys.path.append('covid19IndiaAnalysis/covid19/')
import project

class Covid19IndiaanalysisConfig(AppConfig):
    name = 'covid19IndiaAnalysis'

    def ready(self):
        project.load_data()
