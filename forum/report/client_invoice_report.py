import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class client_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(client_invoice, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'date': datetime.datetime.now().strftime("%d %B %Y"),
        })
        
report_sxw.report_sxw('report.client.invoice',
                      'cmc.assessment',
                      'addons/eMobility/report/client_invoice.rml', parser=client_invoice)