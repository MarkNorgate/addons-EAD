from osv import fields, osv
from tiny_sxw2rml import sxw2rml
from StringIO import StringIO
from report import interface
import base64
import pooler
import tools
import wizard
from tools.misc import debug
import os



class wizard_sxw_rml(wizard.interface):
    _call_history_detail = '''<?xml version="1.0"?>
    <form string="SXW TO RML CONVERTER">
                    <group colspan="2" col="2">
                        <field name="datas_fname" select="2" readonly="0" />
                        <field name="datas" select="2" readonly="0" />
                    </group>
    </form>'''
    
    _call_history_fields = {
        'datas_fname': {'type':'char', 'size':64, 'string':'Filename'},
        'datas':{'type':'binary', 'string':'Data'},
    }
    
    def _save(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        file_sxw = base64.decodestring(data['form']['datas'])
        sxwval = StringIO(file_sxw)
        debug(sxwval)
        file_type = 'sxw'
        if file_type == 'sxw':
            fp = open('D:/workspace/eMobility/wizard/tiny_sxw2rml/normalized_oo2rml.xsl','r')
        if file_type == 'odt':
            fp = tools.file_open('normalized_odt2rml.xsl',
                    subdir='addons/base_report_designer/wizard/tiny_sxw2rml')
        xsl=fp.read()
        fp.close()
        report_content=str(sxw2rml(sxwval, xsl))
        fpp = open('D:/workspace/eMobility/report/test_report.rml','a+')
        fpp.write(report_content)
        debug(report_content)
        fpp.close()
        report_id=112
        report = pool.get('ir.actions.report.xml').write(cr, uid, [report_id], {
            'report_sxw_content': file_sxw,
            'report_rml_content': report_content,
            'report_type':'pdf'
        })
        cr.commit()
        db = pooler.get_db_only(cr.dbname)
        interface.register_all(db)
                                                      
#            'report_rml_content': report_content,})
#        report = pooler.get('ir.actions.report.xml').create(cr, uid, {
#            'auto':False,
#            'model':'cmc.assessment',
#            'type':'ir.actions.report.xml',
#            'report_name':'test.report',
#            'report_sxw_content': file_sxw,
#            'report_rml_content': report_content,
#            'report_rml':'eMobility/report/test_report.rml'
#        })
#        
#        cr.commit()
#        db = pooler.get_db_only(cr.dbname)
#        interface.register_all(db)
        data['form']['name']='CHECK HECKEC'
        debug(data)
        return data['form']
    
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form',
                       'arch':_call_history_detail,
                       'fields':_call_history_fields,
                       'state':[
                                ('end', 'Cancel'),
                                ('check', 'Check'),
                                ]}
        },
        'check': {
            'actions': [_save],
            'result': {'state':'end'}

        }
    }

wizard_sxw_rml('sxw2rml.wizard')



