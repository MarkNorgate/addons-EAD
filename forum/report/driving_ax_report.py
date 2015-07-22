import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class driving_ax_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(driving_ax_report, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'time': datetime.datetime.now().strftime("%d %B %Y"),
            'date':datetime.datetime.now().strftime("%d %B %Y %H:%M:%S"),
        })
        
report_sxw.report_sxw('report.driving.ax',
                      'cmc.assessment',
                      'addons/eMobility/report/driving_ax_report.sxw', parser=driving_ax_report)