import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class cmc_main_brochure_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cmc_main_brochure_report, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'time': datetime.datetime.now().strftime("%d %B %Y"),
        })
        
report_sxw.report_sxw('report.cmc.main.brochure',
                      'cmc.assessment',
                      'addons/eMobility/report/cmc_main_brochure.rml', parser=cmc_main_brochure_report)