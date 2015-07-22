import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class admin_check_list_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(admin_check_list_report, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'time': datetime.datetime.now().strftime("%d %B %Y"),
        })
        
report_sxw.report_sxw('report.admin.checklist',
                      'cmc.assessment',
                      'addons/eMobility/report/admin_checklist.rml', parser=admin_check_list_report)