import wizard
import time
from tools.misc import debug
import string
from string import Template
import pooler
import base64


class cmc_main_brochure(wizard.interface):
    
    states = {
        'init': {
            'actions': [],
            'result': {'type':'print', 'report':'cmc.main.brochure', 'state':'end'}
            }
            
        
    }

cmc_main_brochure('cmc.main.brochure.wizard')
