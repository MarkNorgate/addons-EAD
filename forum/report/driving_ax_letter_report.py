import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class driving_ax_letter_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(driving_ax_letter_report, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'date': datetime.datetime.now().strftime("%d %B %Y"),
            'time': datetime.datetime.now()
        })
        
report_sxw.report_sxw('report.driving.ax.letter',
                      'cmc.assessment',
                      'addons/eMobility/report/driving_ax_letter.rml', parser=driving_ax_letter_report)