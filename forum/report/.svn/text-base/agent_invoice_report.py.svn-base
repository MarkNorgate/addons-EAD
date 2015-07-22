import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class agent_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(agent_invoice, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'date': datetime.datetime.now().strftime("%d %B %Y"),
        })
        
report_sxw.report_sxw('report.agent.invoice',
                      'cmc.assessment',
                      'addons/eMobility/report/agent_invoice.rml', parser=agent_invoice)