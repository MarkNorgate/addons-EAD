import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class dvla_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(dvla_invoice, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'date': datetime.datetime.now().strftime("%d %B %Y"),
        })
        
report_sxw.report_sxw('report.dvla.invoice',
                      'cmc.assessment',
                      'addons/eMobility/report/dvla_invoice.rml', parser=dvla_invoice)