import datetime
from report import report_sxw
from osv import osv
from tools.misc import debug
import pooler

class infopack_chaseup_letter_client(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(infopack_chaseup_letter_client, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'time': datetime.datetime.now().strftime("%d %B %Y"),
        })
        
report_sxw.report_sxw('report.info.pack.chaseup.letter',
                      'cmc.assessment',
                      'addons/eMobility/report/infopack_chaseup_letter_client.rml', parser=infopack_chaseup_letter_client)