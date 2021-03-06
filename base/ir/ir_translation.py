# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import tools

TRANSLATION_TYPE = [
    ('field', 'Field'),
    ('model', 'Object'),
    ('rml', 'RML'),
    ('selection', 'Selection'),
    ('view', 'View'),
    ('wizard_button', 'Wizard Button'),
    ('wizard_field', 'Wizard Field'),
    ('wizard_view', 'Wizard View'),
    ('xsl', 'XSL'),
    ('help', 'Help'),
    ('code', 'Code'),
    ('constraint', 'Constraint'),
    ('sql_constraint', 'SQL Constraint')    
]

class ir_translation(osv.osv):
    _name = "ir.translation"
    _log_access = False

    def _get_language(self, cr, uid, context):
        lang_obj = self.pool.get('res.lang')
        lang_ids = lang_obj.search(cr, uid, [('translatable', '=', True)],
                context=context)
        langs = lang_obj.browse(cr, uid, lang_ids, context=context)
        res = [(lang.code, lang.name) for lang in langs]
        for lang_dict in tools.scan_languages():
            if lang_dict not in res:
                res.append(lang_dict)
        return res

    _columns = {
        'name': fields.char('Field Name', size=128, required=True),
        'res_id': fields.integer('Resource ID', select=True),
        'lang': fields.selection(_get_language, string='Language', size=5),
        'type': fields.selection(TRANSLATION_TYPE, string='Type', size=16, select=True),
        'src': fields.text('Source'),
        'value': fields.text('Translation Value'),
    }

    def _auto_init(self, cr, context={}):
        super(ir_translation, self)._auto_init(cr, context)
        #Delete the existing indexes in the system if any.
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('ir_translation_ltns',))
        if cr.fetchone():
            cr.execute('DROP INDEX ir_translation_ltns')
            cr.commit()
        
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('ir_translation_lts',))
        if cr.fetchone():
            cr.execute('DROP INDEX ir_translation_lts')
            cr.commit()
            
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('ir_translation_ltn',))
        if not cr.fetchone():
            cr.execute('CREATE INDEX ir_translation_ltn ON ir_translation (name, lang, type)')
            cr.commit()
        # There is a size limit on btree indexed values so we can't index src column with normal btree.
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('ir_translation_src_hash_idx',))
        if not cr.fetchone():
            cr.execute('CREATE INDEX ir_translation_src_hash_idx ON ir_translation using hash (src)')
            cr.commit()
            
    @tools.cache(skiparg=3, multi='ids')
    def _get_ids(self, cr, uid, name, tt, lang, ids):
        translations = dict.fromkeys(ids, False)
        if ids:
            cr.execute('select res_id,value ' \
                    'from ir_translation ' \
                    'where lang=%s ' \
                        'and type=%s ' \
                        'and name=%s ' \
                        'and res_id in %s',
                    (lang, tt ,name, tuple(ids)))
            for res_id, value in cr.fetchall():
                translations[res_id] = value
        return translations

    def _set_ids(self, cr, uid, name, tt, lang, ids, value, src=None):
        # clear the caches
        tr = self._get_ids(cr, uid, name, tt, lang, ids)
        for res_id in tr:
            if tr[res_id]:
                self._get_source.clear_cache(cr.dbname, uid, name, tt, lang, tr[res_id])
        self._get_source.clear_cache(cr.dbname, uid, name, tt, lang)
        self._get_ids.clear_cache(cr.dbname, uid, name, tt, lang, ids)

        cr.execute('delete from ir_translation ' \
                'where lang=%s ' \
                    'and type=%s ' \
                    'and name=%s ' \
                    'and res_id in %s',
                (lang, tt, name, tuple(ids)))
        for id in ids:
            self.create(cr, uid, {
                'lang':lang,
                'type':tt,
                'name':name,
                'res_id':id,
                'value':value,
                'src':src,
                })
        return len(ids)

    @tools.cache(skiparg=3)
    def _get_source(self, cr, uid, name, tt, lang, source=None):
        """
        Returns the translation for the given combination of name, type, language
        and source. All values passed to this method should be unicode (not byte strings),
        especially ``source``.

        :param name: identification of the term to translate, such as field name
        :param type: type of term to translate (see ``type`` field on ir.translation)
        :param lang: language code of the desired translation
        :param source: optional source term to translate (should be unicode)
        :rtype: unicode
        :return: the request translation, or an empty unicode string if no translation was
                 found and `source` was not passed
        """
        if source:
            cr.execute('select value ' \
                    'from ir_translation ' \
                    'where lang=%s ' \
                        'and type=%s ' \
                        'and name=%s ' \
                        'and src=%s',
                    (lang or '', tt, tools.ustr(name), source))
        else:
            cr.execute('select value ' \
                    'from ir_translation ' \
                    'where lang=%s ' \
                        'and type=%s ' \
                        'and name=%s',
                    (lang or '', tt, tools.ustr(name)))
        res = cr.fetchone()
        trad = res and res[0] or u''
        if source and not trad:
            return tools.ustr(source)
        return trad

    def create(self, cursor, user, vals, context=None):
        if not context:
            context = {}
        ids = super(ir_translation, self).create(cursor, user, vals, context=context)
        for trans_obj in self.read(cursor, user, [ids], ['name','type','res_id','src','lang'], context=context):
            self._get_source.clear_cache(cursor.dbname, user, trans_obj['name'], trans_obj['type'], trans_obj['lang'], source=trans_obj['src'])
            self._get_ids.clear_cache(cursor.dbname, user, trans_obj['name'], trans_obj['type'], trans_obj['lang'], [trans_obj['res_id']])
        return ids

    def write(self, cursor, user, ids, vals, context=None):
        if not context:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = super(ir_translation, self).write(cursor, user, ids, vals, context=context)
        for trans_obj in self.read(cursor, user, ids, ['name','type','res_id','src','lang'], context=context):
            self._get_source.clear_cache(cursor.dbname, user, trans_obj['name'], trans_obj['type'], trans_obj['lang'], source=trans_obj['src'])
            self._get_ids.clear_cache(cursor.dbname, user, trans_obj['name'], trans_obj['type'], trans_obj['lang'], [trans_obj['res_id']])
        return result

    def unlink(self, cursor, user, ids, context=None):
        if not context:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        for trans_obj in self.read(cursor, user, ids, ['name','type','res_id','src','lang'], context=context):
            self._get_source.clear_cache(cursor.dbname, user, trans_obj['name'], trans_obj['type'], trans_obj['lang'], source=trans_obj['src'])
            self._get_ids.clear_cache(cursor.dbname, user, trans_obj['name'], trans_obj['type'], trans_obj['lang'], [trans_obj['res_id']])
        result = super(ir_translation, self).unlink(cursor, user, ids, context=context)
        return result

ir_translation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

