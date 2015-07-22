import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class wheelchair_assessment_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(wheelchair_assessment_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': datetime.datetime.now().strftime("%d %B %Y"),
        })
        
report_sxw.report_sxw('report.wheelchair.assessment',
                      'cmc.assessment',
                      'addons/eMobility/report/wheelchair_assessment.rml', parser=wheelchair_assessment_report)