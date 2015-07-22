import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class pending_assessment_agent_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(pending_assessment_agent_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': datetime.datetime.now().strftime("%d %B %Y"),
        })
        
report_sxw.report_sxw('report.pending.assessment.client',
                      'cmc.assessment',
                      'addons/eMobility/report/pending_assessment_agent_report.rml', parser=pending_assessment_agent_report)
