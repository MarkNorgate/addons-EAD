import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class print_assessment_paperwork_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_assessment_paperwork_report, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'time': datetime.datetime.now().strftime("%d %B %Y"),
        })
        
report_sxw.report_sxw('report.print.assessment.paperwork',
                      'cmc.assessment',
                      'addons/eMobility/report/print_assessment_paperwork.rml', parser=print_assessment_paperwork_report)