import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class info_pack_letter_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(info_pack_letter_report, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'time': datetime.datetime.now().strftime("%d %B %Y"),
        })
        
report_sxw.report_sxw('report.info.pack.letter',
                      'cmc.assessment',
                      'addons/eMobility/report/info_pack_letter.rml', parser=info_pack_letter_report)