from osv import fields, osv
from osv.orm import except_orm
from string import Template
from tools.misc import debug
from tools.translate import _
import tools
import datetime
import string
import tools
import pooler
import base64


days = 'Monday Tuesday Wednesday Thursday Friday Saturday Sunday'.split()
days_1 = {d: n for n, d in enumerate(days)}
class cmc_appointments(osv.osv):
    _name = 'cmc.appointments'
    _description = 'cmc.appointments'
    _rec_name = 'apmnt_start_date'
    
    def driving_name(self, type):
        t ={
            'full_driving_assessment': 'FULL DRIVING ASSESSMENT',
            'wheelchair_assessment':'WHEELCHAIR ASSESSMENT',
            'drive_from_wheelchair_assessment':'DRIVE FROM WHEELCHAIR ASSESSMENT',
            'passenger_adult':'Passenger Adult','passenger_child':'Passenger Child',
            'car_seat_harness_assessment':'CAR SEAT HARNESS ASSESSMENT',
            'driving_legal_assessment':'Driving Legal Assessment',
            'drive_safer_for_longer_assessment':'Drive Safer For Longer Assessment',
            'driving_adaptation_assessment':'Driving Adaptation Assessment',
            'mo_map_adapdation_assessment':'MO MAP Adaptation Assessment',
            'review_assessment':'Review Assessment',
            'wheel_walker':'Wheeled Walker',
            'chair_assessment':'Chair Assessment',
            'bathing_assessment':'Bathing Assessment',
            'other_ilme_equipment_assessment':'Other ILME Equipment Assessment',
            'buggy_assessment':'Buggy Assessment',
            'scooter_assessment':'Scooter Assessment',
            'pct_wheelchair_buggy':'PCT Wheelchair/Buggy',
            'hoist_demo':'Hoist Demo',
            'momap_access':'MO MAP Access',
            'pressure_mapping_assessment':'Pressure Mapping Assessment'}
        return t.get(type, '')
    def searchNew(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False,filter_uid=None):
        #get the ids as usual from super class applying domain
        ids = self.search(cr, uid, args, offset, limit,
                order, context=context, count=count)
        #dictionary to return 
        ret={}
        ret['events'] = {}
        ret['users']={}
        ret['equipments']={}
        ret['equipments_id']={}
        
        day = {}
        day_today = datetime.datetime.now().strftime("%Y-%m-%d")
        events = self.browse(cr, uid, ids)
        if not (isinstance(events, (list))):
            events=[events]
        day = {}
        #debug(filter_uid)
        #debug(events)
        for event in set(events):
            #find owner name and add this event to the ret{'username':[] array 
            #create a dictionary event object with key values to return
            week_list = {
                'Monday':[],
                'Tuesday':[],
                'Wednesday':[],
                'Thursday':[],
                'Friday':[],
                'Saturday':[],
                'Sunday':[]}
            color='white'
            event_title=""
            type="general"
            job_no=""
            if event.assessment_id:
                color='#A4A4A4'
                type="assessment"
                event_title=event.assessment_id.driving_assessment_type+'-'+event.assessment_id.client_person_id.display_name if event.assessment_id.client_person_id.display_name else "" 
            elif event.equipment_supply_process_id:
                type="supply"
                color='#5858FA'
                event_title=event.equipment_supply_process_id.equipment_supply_id+'-'+event.equipment_supply_process_id.client_id.display_name
            elif event.workshop_id:
                type="workshop"
                color='#F781BE'
                event_title=event.workshop_id.equipment_id.make+'-'+event.workshop_id.equipment_id.model+('-'+event.workshop_id.equipment_id.serial_no if event.workshop_id.equipment_id.serial_no else "")
                job_no=event.workshop_id.job_no
            else:
                event_title=event.title
            event_attendees=[]
            equipments_list=[]
            for user in event.user_ids:
                event_attendees.append(user.name)
            if len(event_attendees)>0:
                event_attendees=", ".join(event_attendees)
            else:
                event_attendees=""
            event_equipments=[]
            for equip in event.equipment_ids:
                event_equipments.append(equip.make+' '+equip.model+(' '+equip.serial_no if equip.serial_no else ""))
            if len(event_equipments)>0:
                equipments_list=event_equipments
                event_equipments=", ".join(event_equipments)
            else:
                event_equipments=""
            evt = {
                'id':event.id,
                'color':color,
                'title':event_title,
                'location':event.location if event.location else "", 
                'Attendees':event.owner.name+", "+event_attendees,
                'Equipments':event_equipments,
                'state':event.apmnt_status,
                'owner':event.owner.name,
                'apmnt_start_time':event.start_time_hour+":"+event.start_time_minutes,
                'apmnt_end_time':event.end_time_hour+":"+event.end_time_minutes,
                'date':event.apmnt_start_date,
                'type':type,
                'event':event.event if event.event else "",
                'job_no':job_no
            }
            days=[]
            start_date=datetime.datetime.strptime(event.apmnt_start_date,"%Y-%m-%d")
            end_date=datetime.datetime.strptime(event.apmnt_date_end,"%Y-%m-%d")
            date_range=self.date_range(start_date, end_date)
            for d in date_range:
                days.append(self.day_return(d))
            days=days[:7]
            if 'Sunday' in days:
                days=days[0:days.index('Sunday')+1]
            event_members={}
            event_members[event.owner.id]=event.owner.name
            for user in event.user_ids:
                event_members[user.id]=user.name
            ret['users'][event.owner.name]=event.owner.id
            # debug(event_members)
#            else:
#                single_user=pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
#                debug(single_user)
#                event_members[single_user.id]=single_user.name
#                ret['users'][single_user.name]=single_user.id
            if context.get('single_user',False):
                single_user=pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
                ret['users'][single_user.name]=single_user.id
                if single_user.name in ret['events']: 
                    for day in days:
                        if evt not in ret['events'][single_user.name][day]:
                            ret['events'][single_user.name][day].append(evt)#add this event to the name key
                            ret['events'][single_user.name][day]=sorted(ret['events'][single_user.name][day],key=lambda x:x['apmnt_start_time'])
                else:
                    week_dup=week_list
                    for day in days:
                        week_dup[day].append(evt)# create a new event list
                    ret['events'][single_user.name]=week_dup
            else:
                for user_id,user_name in event_members.items():
                        week_list = {
                        'Monday':[],
                        'Tuesday':[],
                        'Wednesday':[],
                        'Thursday':[],
                        'Friday':[],
                        'Saturday':[],
                        'Sunday':[]
                        }
                        if user_name in ret['events']:
                            for day in days:
                                if evt not in ret['events'][user_name][day]:
                                    ret['events'][user_name][day].append(evt)#add this event to the name key
                                    ret['events'][user_name][day]=sorted(ret['events'][user_name][day],key=lambda x:x['apmnt_start_time'])
                        else:
                            week_dup=week_list
                            for day in days:
                                week_dup[day].append(evt)# create a new event list
                            ret['events'][user_name]=week_dup
                #===================================================================
                # Equipments
                #===================================================================
                
                euiqpments={}
                if not context.get('single_user',False):
                    for equip in event.equipment_ids:
                        week_list = {
                        'Monday':[],
                        'Tuesday':[],
                        'Wednesday':[],
                        'Thursday':[],
                        'Friday':[],
                        'Saturday':[],
                        'Sunday':[]
                        }
                        if (equip.make+" "+equip.model) in ret['equipments']:
                            for day in days:
                                ret['equipments'][equip.make+" "+equip.model][day].append(evt)
                        else:
                            week_dup=week_list
                            ret['equipments_id'][equip.make+" "+equip.model]=equip.id
                            for day in days:
                                week_dup[day].append(evt)# create a new event list
                            ret['equipments'][equip.make+" "+equip.model]=week_dup
                        #debug(ret['equipments'])
        
        if context.get('app_data',False):
            if not context['app_data']['all_search']:
                user_ids=context['app_data']['user'][0][2]
                equip=context['app_data']['equipment'][0][2]
                event_equip={}
                query=[]
                if len(user_ids)>0:
                    query.append('select name,id from res_users where id in ('+','.join([str(u) for u in user_ids])+')')
                if context['app_data']['user_group']:
                    query.append('select name,id from res_users where id in (select uid from res_groups_users_rel where gid=%s)' %(str(context['app_data']['user_group'])))
                if len(equip)>0:
                    cr.execute('select make,model from cmc_equipment where id in ('+','.join([str(e) for e in equip])+')')
                    #debug(cr.fetchall())
                    equip_all=[x[0]+" "+x[1] for x in cr.fetchall()]
                    # debug(equip_all)
                    for name in equip_all:
                        if name in ret['equipments']:
                            event_equip[name]=ret['equipments'][name]
                ret['equipments']=event_equip
                    
                if len(query)>1:
                    cr.execute(' union '.join(query))
                elif len(query)==1:
                    # debug(ret['events'])
                    cr.execute(query[0])
                my_appointments = cr.fetchall()
                # app_users=[x[0] for x in my_appointments]
                app_users=[]
                user_list={}
                for x in my_appointments:
                    app_users.append(x[0])
                    user_list[x[0]]=x[1]
                event={}
                for name in app_users:
                    if name in ret['events']:
                        event[name]=ret['events'][name]
                ret['events']=event
                ret['users']=user_list
                    # debug(event)
                # debug(my_appointments)
        
        return ret
    def day_return(self, date1):
        return date1.strftime("%A")
        #return datetime.datetime.strptime(date1, "%Y-%m-%d %H:%M:%S").strftime("%A")
    def date_range(self,start, end):
        r = (end+datetime.timedelta(days=1)-start).days
        return [start+datetime.timedelta(days=i) for i in range(r)]
    def weekdays_between(self,s, e): 
        s, e = days_1[s], days_1[e]
        return [days[n % 7] for n in range(s, e + (1 if e > s else 8))]
    def formation(self, vals):
        dates = []
        start_date = vals['apmnt_start_date']
        end_date = vals['apmnt_date_end']
        start_time_hour = vals['start_time_hour']
        start_time_minutes = vals['start_time_minutes']
        end_time_hour = vals['end_time_hour']
        end_time_minutes = vals['end_time_minutes']
        start_time = start_time_hour + ":" + start_time_minutes + ":" + "00"
        end_time = end_time_hour + ":" + end_time_minutes + ":" + "00"
        dates.append(vals['apmnt_start_date'] + " " + start_time)
        dates.append(vals['apmnt_date_end'] + " " + end_time)
        return dates
    def description_formation(self, cr, vals):
        euip_names = ''
        user_names = ''
        owner_name_name = ''
        description = ''
        #description = "From:" + vals['apmnt_start_date_time'] + " - " + vals['apmnt_end_date_time'] + '\n'
        if 'equipment_ids' in vals:
            if len(vals['equipment_ids'][0][2]) > 0 :
                query = "select model from cmc_equipment where id in (" + ','.join([str(u) for u in vals['equipment_ids'][0][2]]) + ")"
                try:
                    cr.execute(query)
                    model_names = cr.fetchall()
                    euip_names = ','.join([u[0] for u in model_names])
                except:
                    euip_names = ""
        if 'user_ids' in vals:
            for id in vals['user_ids'][0][2]:
                query = "SELECT name FROM res_users WHERE id=" + (str(id))
                cr.execute(query)
                owner_name = cr.fetchone()
                user_names += owner_name[0] + ','
        if 'owner' in vals:
            query = "SELECT name FROM res_users WHERE id=" + (str(vals['owner']))
            cr.execute(query)
            owner_name = cr.fetchone()
            owner_name_name += owner_name[0] + ','
        description += ("Location:" + vals['location'] + '\n') if vals['location'] else ""
        description += ("Owner:" + owner_name_name + '\n') if len(owner_name_name) > 0 else "" 
        description += ("Attendees:" + user_names + '\n') if len(user_names) > 0 else ""  
        description += ("Equipment:" + euip_names + '\n') if len(euip_names) > 0 else ""
        return description 
    def search_list(self, cr, uid, id, domain):
        # debug(cr)
        # debug(uid)
        # debug(id)
        # debug(domain)
        return [1]
    def btn_create_new_record(self,cr,uid,id,domain):
        return 
    def clashing (self, cr, uid, vals, owner_clash, equipment_clash, user_clash, context={}):
        clash = False
        error = []
        if owner_clash:
            cr.execute("select id from cmc_appointments where (state='active' or state='active_clash') and (('%s' BETWEEN apmnt_start_date_time and apmnt_end_date_time) or ('%s' BETWEEN apmnt_start_date_time and apmnt_end_date_time) or ('%s' <= apmnt_start_date_time and '%s' >=apmnt_end_date_time)) and (owner='%s' or id in (select appointment_id from user_appointment_rel where user_id='%s'))" %(vals['apmnt_start_date_time'],vals['apmnt_end_date_time'],vals['apmnt_start_date_time'],vals['apmnt_end_date_time'],vals['owner'],vals['owner']))
            owner_state = cr.fetchall()
            debug(owner_state)
            if len(owner_state) > 0:
                if not vals['save_clash']:
                    error.append('Owner Has Clashing Appointment')
                else:
                    clash = True
        #=======================================#
        # Checking Users Conflict 
        #=======================================#
        if user_clash:
            users = vals['user_ids'][0][2]
            if len (users) > 0 :
                users_check_list=','.join([str(u) for u in users])
                debug(users_check_list)
                cr.execute("select id from cmc_appointments where (id in (select appointment_id from user_appointment_rel where user_id in (%s))) and (state='active' or state='active_clash') and (('%s' BETWEEN apmnt_start_date_time and apmnt_end_date_time) or ('%s' BETWEEN apmnt_start_date_time and apmnt_end_date_time) or ('%s' <= apmnt_start_date_time and '%s' >=apmnt_end_date_time))" %(users_check_list,vals['apmnt_start_date_time'],vals['apmnt_end_date_time'],vals['apmnt_start_date_time'],vals['apmnt_end_date_time']))
                user_clash_ids = cr.fetchall()
                cr.execute("select id from cmc_appointments where (owner in (%s)) and (state='active' or state='active_clash') and (('%s' BETWEEN apmnt_start_date_time and apmnt_end_date_time) or ('%s' BETWEEN apmnt_start_date_time and apmnt_end_date_time) or ('%s' <= apmnt_start_date_time and '%s' >=apmnt_end_date_time))" %(users_check_list,vals['apmnt_start_date_time'],vals['apmnt_end_date_time'],vals['apmnt_start_date_time'],vals['apmnt_end_date_time']))
                owner_clash_ids = cr.fetchall()
                if len(user_clash_ids) > 0:
                    #===========================================================
                    # As Attendees clashing appointments
                    #===========================================================
                    user_clash_query = "select name from res_users where id in (select user_id from user_appointment_rel where appointment_id in (" + ','.join([str(u[0]) for u in user_clash_ids]) + "))"
                    cr.execute(user_clash_query)
                    user_names = cr.fetchall()
                    if len(user_names) > 0 and not vals['save_clash']:
                        users_names = ','.join([str(u[0]) for u in user_names])
                        error.append(users_names + (' has' if len(user_names) == 1 else ' have') + ' another appointments at this time')
                    else:
                        clash = True 
                    
                    #===========================================================
                    # As Owner clashing appointments
                    #===========================================================
                if len(owner_clash_ids) > 0:
                    user_clash_query = "select name from res_users where id in (" + ','.join([str(u[0]) for u in owner_clash_ids]) + ")"
                    cr.execute(user_clash_query)
                    user_names = cr.fetchall()
                    if len(user_names) > 0 and not vals['save_clash']:
                        users_names = ','.join([str(u[0]) for u in user_names])
                        error.append(users_names + (' has' if len(user_names) == 1 else ' have') + ' another appointments as owner at this time')
                    else:
                        clash = True 
        #=======================================#
        # Checking Equipment Conflict 
        #=======================================#
        if equipment_clash:
            equipment = vals['equipment_ids'][0][2]
            equipment_check_list=','.join([str(u) for u in equipment])
            if len(equipment) > 0 :
                cr.execute("select id from cmc_appointments where id in (select appointment_id from equipment_appointment_rel where equipment_id in (%s)) and (state='active' or state='active_clash') and (('%s' BETWEEN apmnt_start_date_time and apmnt_end_date_time) or ('%s' BETWEEN apmnt_start_date_time and apmnt_end_date_time) or ('%s' <= apmnt_start_date_time and '%s' >=apmnt_end_date_time))" %(equipment_check_list,vals['apmnt_start_date_time'],vals['apmnt_end_date_time'],vals['apmnt_start_date_time'],vals['apmnt_end_date_time']))
                equip_ids = cr.fetchall()
                if len(equip_ids) > 0 :
                    equipment_clash_query = "select model from cmc_equipment where id in (select equipment_id from equipment_appointment_rel where appointment_id in (" + ','.join([str(u[0]) for u in equip_ids]) + ") and equipment_id in (" + ','.join([str(u) for u in equipment]) + "))"
                    cr.execute(equipment_clash_query)
                    equipment_names = cr.fetchall()
                    if len(equipment_names) > 0 and not vals['save_clash']:
                        equipments_names = ','.join([str(u[0]) for u in equipment_names])
                        error.append('Equipment ' + equipments_names + (' has' if len(equipments_names) == 1 else ' have') + ' another appointments at this time')
                    else:
                        clash = True 
        if error is not None and len(error) > 0 :
            error.append('You have to Enter the Attendees and Equipment details Again')
            error = '\n\t'.join(error)
            raise osv.except_osv ('Warning', error)
        return clash
    def create(self, cr, uid, vals, context={}):
        #=======================================================================
        # Checking appointment start date should be before appointment End date 
        #=======================================================================
        debug(vals)
        if not context.get('by_pass', False):
            vals['apmnt_start_date_time'] = self.formation(vals)[0]
            vals['apmnt_end_date_time'] = self.formation(vals)[1]
            
            if vals['apmnt_end_date_time'] < vals['apmnt_start_date_time']:
                 raise osv.except_osv(' Appointment Error!', 'The appointment cannot start before finish date and time.\n You Have to Re Enter the Attendees and Equipments Details Again')
            
            vals['owner']=vals['owner_dup']
            if not vals['owner']:
                    raise osv.except_osv(' Appointment Error!', 'The Appointment must have one Assessor Selected.')
            vals['description'] = self.description_formation(cr, vals)
            if 'type' in vals and vals['type']=='reminder':
                return super(cmc_appointments, self).create(cr, uid, vals, context)
            equipment_clash = user_clash=False
            if 'from_appointment' in vals and vals['from_appointment']:
                if vals['from_appointment'] =='cmc.assessment':
                    vals['assessment_id']=int(vals['parent_id'])
                elif vals['from_appointment'] =='cmc.workshop.process':
                    vals['workshop_id']=int(vals['parent_id'])
                elif vals['from_appointment']=='cmc.equipement.supply.process':
                    vals['equipment_supply_process_id']=int(vals['parent_id'])
            if 'assessment_id' in vals and vals['assessment_id']:
                equipment_clash = user_clash = False
                assessment_br = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, vals['assessment_id'])
                if assessment_br.driving_assessment_type != 'Driving Tution' and assessment_br.driving_assessment_type != 'MoMap Familiarisation' and \
                assessment_br.driving_assessment_type != 'Drive From Wheelchair Tution':
                    if 'equipment_ids' in vals:
                        if vals['equipment_ids'][0][2]:
                            equipment_clash = True
                        if vals['user_ids'][0][2]:
                            user_clash = True
                        vals['clash'] = self.clashing(cr, uid, vals, True, equipment_clash, user_clash, context)
                        attach_ids = pooler.get_pool(cr.dbname).get('cmc.appointments').search(cr, uid, [("assessment_id", "=", vals['assessment_id'])])
                        attach_ids_state = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, attach_ids)
                        if attach_ids_state is not None and len(attach_ids_state) > 0:
                            for state_status in attach_ids_state:
                                if state_status.state == 'active' or state_status.state == 'active_clash':
                                   if vals['apmnt_start_date_time'] >= state_status.apmnt_start_date_time and vals['apmnt_start_date_time'] <= state_status.apmnt_end_date_time:
                                       if not vals['save_clash'] :
                                           raise osv.except_osv('Warning', 'This appointment dates are clashing with one of the active appointment\n You Have to Re Enter the Attendees and Equipments Details Again')
                                       else :
                                           vals['clash'] = True
                        vals['description'] = self.description_formation(cr, vals)
                        
                        if vals['clash']:
                            vals['state'] = 'active_clash'
                        else:
                            vals['state'] = 'active'
                else:
                    if assessment_br.no_hours == 0:
                        raise osv.except_osv ('Warning', 'This asssessment doesnt have hour to make appointment')
                    attach_ids = pooler.get_pool(cr.dbname).get('cmc.appointments').search(cr, uid, [("assessment_id", "=", vals['assessment_id'])])
                    attach_ids_state = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, attach_ids)
                    diff = 0
                    if attach_ids_state is not None and len(attach_ids_state) > 0:
                        for state_status in attach_ids_state:
                            if state_status.state == 'active' :
                                diff += self.diff(state_status.apmnt_end_date_time, state_status.apmnt_start_date_time)
                    diff += self.diff(vals['apmnt_end_date_time'], vals['apmnt_start_date_time'])
                    if diff > (assessment_br.no_hours * 60 * 60):
                        raise osv.except_osv ('Warning', 'You Cannot Make Further Appointments')
                    else:
                        vals['state'] = 'active'
            elif 'workshop_id' in vals and vals['workshop_id']:
                equipment_clash = user_clash = False
                if 'equipment_ids' in vals:
                    if vals['equipment_ids'][0][2]:
                        equipment_clash = True
                    if vals['user_ids'][0][2]:
                        user_clash = True
                    vals['clash'] = self.clashing(cr, uid, vals, True, equipment_clash, user_clash, context)
                    attach_ids = pooler.get_pool(cr.dbname).get('cmc.appointments').search(cr, uid, [("workshop_id", "=", vals['workshop_id'])])
                    attach_ids_state = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, attach_ids)
                    if attach_ids_state is not None and len(attach_ids_state) > 0:
                        for state_status in attach_ids_state:
                            if state_status.state == 'active' or state_status.state == 'active_clash':
                               if vals['apmnt_start_date_time'] >= state_status.apmnt_start_date_time and vals['apmnt_start_date_time'] <= state_status.apmnt_end_date_time:
                                   if not vals['save_clash'] :
                                       raise osv.except_osv ('Warning', 'This appointment dates are clashing with one of the active appointment\n You Have to Re Enter the Attendees and Equipments Details Again')
                                   else :
                                       vals['clash'] = True
                vals['description'] = self.description_formation(cr, vals)
            elif 'equipment_supply_process_id' in vals and vals['equipment_supply_process_id']:
                equipment_clash = user_clash = False
                if 'equipment_ids' in vals:
                    if vals['equipment_ids'][0][2]:
                        equipment_clash = True
                    if vals['user_ids'][0][2]:
                        user_clash = True
                    vals['clash'] = self.clashing(cr, uid, vals, True, equipment_clash, user_clash, context)
                    attach_ids = pooler.get_pool(cr.dbname).get('cmc.appointments').search(cr, uid, [("equipment_supply_process_id", "=", vals['equipment_supply_process_id'])])
                    attach_ids_state = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, attach_ids)
                    if attach_ids_state is not None and len(attach_ids_state) > 0:
                        for state_status in attach_ids_state:
                            if state_status.state == 'active' or state_status.state == 'active_clash':
                               if vals['apmnt_start_date_time'] >= state_status.apmnt_start_date_time and vals['apmnt_start_date_time'] <= state_status.apmnt_end_date_time:
                                   if not vals['save_clash'] :
                                       raise osv.except_osv ('Warning', 'This appointment dates are clashing with one of the active appointment\n You Have to Re Enter the Attendees and Equipments Details Again')
                                   else :
                                       vals['clash'] = True
            elif not vals['parent_id']:
                if vals['equipment_ids'][0][2] and 'equipment_ids' in vals:
                    equipment_clash = True
                if vals['user_ids'][0][2]:
                    user_clash = True
                    vals['description'] = self.description_formation(cr, vals)
                vals['clash'] = self.clashing(cr, uid, vals, True, equipment_clash, user_clash, context)
            else:
                if not vals['owner']:
                    vals['owner'] = uid
            if 'clash' in vals and vals['clash']:
                vals['state'] = 'active_clash'
            else:
                vals['state'] = 'active'
            debug(vals)
            if vals['state'] == 'active' or vals['state']=='active_clash':
                 return super(cmc_appointments, self).create(cr, uid, vals, context)
            else:
                return 
    def diff(self, end_time, start_time):
        diff = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        return diff.total_seconds()             
    def write(self, cr, uid, ids, vals, context={}):
        debug('====I AM IN WRITE MODE OF APPOINTMENTS====')
        # debug(vals)
        # debug(context)
        
        if 'apmnt_start_date' in vals and 'apmnt_date_end' in vals : 
            vals['apmnt_start_date_time'] = self.formation(vals)[0]
            vals['apmnt_end_date_time'] = self.formation(vals)[1]
            if vals['apmnt_end_date_time'] <= vals['apmnt_start_date_time']:
                raise except_orm(' Appointment Error!', 'The appointment cannot start before finish date and time.\n You Have to Re Enter the Attendees and Equipments Details Again')
        if type(ids).__name__ == 'int':
            prev_record=self.browse(cr,uid,ids)
        else:
            prev_record = self.browse(cr, uid, ids[0])
        owner_clash = user_clash = equipment_clash = False
        if 'owner_dup' in vals and vals['owner_dup']!=prev_record.owner_dup:
            vals['owner']=vals['owner_dup']
        if prev_record.assessment_id and (prev_record.assessment_id.driving_assessment_type == 'Driving Tution' or prev_record.assessment_id.driving_assessment_type == 'MoMap Familiarisation' or 
        prev_record.driving_assessment_type=='Drive From Wheelchair Tution'):
            #assessment_br= pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, prev_record.assessment_id)
            attach_ids = pooler.get_pool(cr.dbname).get('cmc.appointments').search(cr, uid, [("assessment_id", "=", prev_record.assessment_id.id)])
            attach_ids_state = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, attach_ids)
            diff = 0
            if attach_ids_state is not None and len(attach_ids_state) > 0:
                for state_status in attach_ids_state:
                    if state_status.state == 'active' and state_status.id != prev_record.id:
                        diff += self.diff(state_status.apmnt_end_date_time, state_status.apmnt_start_date_time)
            if 'apmnt_end_date_time' in vals:
                diff += self.diff(vals['apmnt_end_date_time'], vals['apmnt_start_date_time'])
            if diff > (prev_record.assessment_id.no_hours * 60 * 60):
                raise osv.except_osv ('Warning', 'You Cannot Make Further Appointments')
            else:
                return super(cmc_appointments, self).write(cr, uid, ids, vals, context)
        if not prev_record.equipment_supply_process_id:
            if 'owner' in vals:
                    if prev_record.owner.id != vals['owner']:
                        owner_clash = True
                    query = "select equipment_id from equipment_appointment_rel where appointment_id = " + str(prev_record.id)
                    cr.execute(query)
                    ee = cr.fetchall()
                    ee = [u[0] for u in ee]
                    if sorted(ee) != sorted(vals['equipment_ids'][0][2]):
                        equipment_clash = True
                    query1 = 'select user_id from user_appointment_rel where appointment_id = ' + str(prev_record.id)
                    user_clash = False
                    try:
                        cr.execute(query1)
                        eee = cr.fetchall()
                        eee = [u[0] for u in eee]
                        if sorted(eee) != sorted(vals['user_ids'][0][2]):
                            user_clash = True
                    except:
                        pass
                    vals['clash'] = self.clashing(cr, uid, vals, owner_clash, equipment_clash, user_clash, context)
                    if prev_record.assessment_id: 
                        if 'parent_id' in vals:
                            if prev_record.apmnt_start_date_time != vals['apmnt_start_date_time'] or prev_record.apmnt_end_date_time != vals['apmnt_end_date_time']:
                                attach_ids = pooler.get_pool(cr.dbname).get('cmc.appointments').search(cr, uid, [("assessment_id", "=", int(vals['parent_id']))])
                                self.write_check(cr, uid, ids, vals, attach_ids)
                    elif prev_record.workshop_id: 
                            if prev_record.apmnt_start_date_time != vals['apmnt_start_date_time'] or prev_record.apmnt_end_date_time != vals['apmnt_end_date_time']:
                                attach_ids = pooler.get_pool(cr.dbname).get('cmc.appointments').search(cr, uid, [("workshop_id", "=", int(prev_record.workshop_id))])
                                self.write_check(cr, uid, ids, vals, attach_ids)
        return super(cmc_appointments, self).write(cr, uid, ids, vals, context)
    def write_check(self, cr, uid, ids, vals, attach_ids):
        attach_ids_state = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, attach_ids)
        attach_ids_state_present = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, ids[0])
        if not vals['owner']:
            raise osv.except_osv (' Appointment Error!', 'The Appointment must have one Assessor Selected.')
        if attach_ids_state is not None and len(attach_ids_state) > 0:
            for state_status in attach_ids_state:
                if state_status.state == 'active' or state_status.state == 'active_clash':
                   if vals['apmnt_start_date_time'] >= state_status.apmnt_start_date_time and vals['apmnt_start_date_time'] <= state_status.apmnt_end_date_time:
                       if not vals['save_clash']:
                           raise except_orm('Warning', 'This Appointment dates are clashing with one of the active appointment')
                       else:
                           vals['state'] = 'active_clash'
                           vals['clash'] = True
                           break
                   else:
                        vals['state'] = 'active'
                        vals['clash'] = False
        return vals
    def btn_cancel_appointment(self, cr, uid, ids, context={}):
        context['from_where'] = 'appointment_unblock'
        prev_record = self.browse(cr, uid, ids[0])
        #==================================== ==================================
        # When Canceling button is pressed it checks it cancellation 
        #=======================================================================
        # if prev_record.owner.id!=uid:
                # raise except_orm ('Warning','Only the owner of appointment can cancel the appointment')
        self.write(cr, uid, ids, {'state':'cancelled', 'cancel_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, context)
        return
    
    def btn_cofirm_appointment(self, cr, uid, ids, context={}):
        context['from_where'] = 'appointment_unblock'
        prev_record = self.browse(cr, uid, ids[0])
        #=======================================================================
        # Confirmation of apoinment takes place state->confirmed
        #=======================================================================
        if prev_record is not None and (prev_record.state == 'active' or prev_record.state == 'active_clash'):
           if prev_record.workshop_id:
               # debug("Workshop Appointment")
               pooler.get_pool(cr.dbname).get('cmc.workshop.task.history').create(cr, uid, {
                                                                        'date_task':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                        'title':'Appointment',
                                                                        'description':'Appointment has been confirmed',
                                                                        'workshop_id':prev_record.workshop_id.id
                                                                                       })
               self.write(cr, uid, ids, {'state':'confirmed'}, context)
           elif prev_record.assessment_id:
               state_browse = pooler.get_pool(cr.dbname).get('cmc.assessment.state').browse(cr, uid, prev_record.assessment_id.state) 
               pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                         'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         'assessment_id':prev_record.assessment_id.id,
                         'type':'Assessment And Appointment Task',
                         'client_name':prev_record.assessment_id.person_id.id,
                         'user_id':uid,
                         'subject':'Appointment',
                         'message':'State:Appointment::Confirmed',
                        })
               self.write(cr, uid, ids, {'state':'confirmed'}, context)
           elif prev_record.equipment_supply_process_id:
                self.write(cr, uid, ids, {'state':'confirmed'}, context)
           else:
                self.write(cr, uid, ids, {'state':'confirmed'}, context)
        return False
    
    def btn_complete_appointment(self, cr, uid, ids, context={}):
        context['from_where'] = 'appointment_unblock'
        prev_record = self.browse(cr, uid, ids[0])
        #=======================================================================
        # Completion of appointment takes and state->completed
        #=======================================================================
#        if prev_record is not None and prev_record.state == 'confirmed':
#            if prev_record.assessment_id.state == 'pending_assessment':
#                pooler.get_pool(cr.dbname).get('cmc.assessment').write(cr,
#                                                          uid,
#                                                          [prev_record.assessment_id.id],
#                                                          {'state':'pending_report_completion'}, {'from_where': 'unblock'})
        if prev_record.workshop_id:
               # debug("Workshop Appointment")
               pooler.get_pool(cr.dbname).get('cmc.workshop.task.history').create(cr, uid, {
                                                                        'date_task':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                        'title':'Appointment',
                                                                        'description':'Appointment has been completed',
                                                                        'workshop_id':prev_record.workshop_id.id
                                                                                       })
        elif prev_record.assessment_id:
            state_browse = pooler.get_pool(cr.dbname).get('cmc.assessment.state').browse(cr, uid, prev_record.assessment_id.state) 
            pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                 'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'assessment_id':prev_record.assessment_id.id,
                 'type':'Assessment And Appointment Task',
                 'client_name':prev_record.assessment_id.person_id.id,
                 'user_id':uid,
                 'subject':'Appointment',
                 'message':'Appointment Completed'
                })
            vals = {
              'owner':prev_record.owner.id,
              'appointment_completed_date':prev_record.apmnt_end_date_time,
              'appointment_completed_d':prev_record.apmnt_date_end
              }
            debug(vals)
            #pooler.get_pool(cr.dbname).get('cmc.assessment').write(cr, uid, [prev_record.assessment_id.id], vals, {'complete':'Appointment'})
            cr.execute("update cmc_assessment set appointment_completed_d='%s',appointment_completed_date='%s' where id=%d" %(prev_record.apmnt_date_end,prev_record.apmnt_end_date_time,prev_record.assessment_id.id))
        self.write(cr, uid, ids, {'state':'completed'}, context)
        
        
        return
    
    def _get_status(self, cr, uid, ids, field_name, arg=None, context={}):
        values = {}
        status_co = ""
        r_ids = self.read(cr, uid, ids, ['id', 'state', 'apmnt_start_date_time', 'cancel_date'])
        for id in r_ids:
                if id['state'] == 'active':
                    status_co = 'Active'
                elif id['state'] == 'active_clash':
                    status_co = 'Active Clash'
                elif id['state'] == 'confirmed':
                    status_co = 'Confirmed'
                elif id['state']=='cancelled':
				    status_co='Cancelled'
                elif id['state'] == 'cancelled_within_two_days':
                    status_co = 'Cancelled Within 48 Hours'
                elif id['state'] == 'completed':
                    status_co = 'Completed'  
                else:
                    status_co = ''
                values[id['id']] = status_co
        return values
    _columns = {
        'assessment_id':fields.many2one('cmc.assessment',
                                      'Assessment'),
        'type':fields.selection([('general', 'General'), ('reminder', 'Reminder')], 'Type'),
        'title':fields.char('Subject', size=255),
        'apmnt_status' : fields.function(_get_status, method=True, string='Status', type='char', size=32),
        'apmnt_start_date_time':fields.datetime('date'),
        'apmnt_end_date_time':fields.datetime('date'),
        'apmnt_start_date':fields.date('Start',
                              required=True),
        'start_time_hour':fields.selection([('00', '00'), ('01', '01'), ('02', '02'),
                                            ('03', '03'), ('04', '04'),
                                            ('05', '05'), ('06', '06'), ('07', '07'),
                                            ('08', '08'), ('09', '09'),
                                            ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'),
                                            ('14', '14'), ('15', '15'),
                                            ('16', '16'), ('17', '17'),
                                            ('18', '18'), ('19', '19'),
                                            ('20', '20'), ('21', '21'),
                                            ('22', '22'), ('23', '23'),
                                            ], 'Hour', required=True),
        'start_time_minutes':fields.selection([('00', '00'), ('05', '05'), ('10', '10'),
                                             ('15', '15'), ('20', '20'), ('25', '25'),
                                             ('30', '30'), ('35', '35'), ('40', '40'),
                                             ('45', '45'), ('50', '50'), ('55', '55'),
                                            ], 'Minutes', required=True),
                                            
        'owner': fields.many2one('res.users', 'Assessor', required=True),
        'owner_dup':fields.selection([(30,'Isabel Coe'),
                                      (34,'Jane Slocombe'),
                                      (36,'Yvette Bateman'),
                                      (37,'Mel Coe'),
                                      (38,'Alfie Gwynne'),
                                      (79,'JR'),
                                      (90,'Dell'),
                                      (98,'Rob'),
                                      (101,'Caroline S'),
                                      (103,'Carol Tupper'),
                                      (106,'Staurt Brighty'),
                                      (107,'Paul Howard'),
                                      (108,'Danielle'),
                                      ],'Assessor',required=True),
        'parent_id':fields.char('Message', size=255),
        'apmnt_date_end':fields.date('Finish', required=True),
        'end_time_hour':fields.selection([('00', '00'), ('01', '01'), ('02', '02'),
                                            ('03', '03'), ('04', '04'),
                                            ('05', '05'), ('06', '06'), ('07', '07'),
                                            ('08', '08'), ('09', '09'),
                                            ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'),
                                            ('14', '14'), ('15', '15'),
                                            ('16', '16'), ('17', '17'),
                                            ('18', '18'), ('19', '19'),
                                            ('20', '20'), ('21', '21'),
                                            ('22', '22'), ('23', '23'),
                                            ], 'Hour', required=True),
        'end_time_minutes':fields.selection([('00', '00'), ('05', '05'), ('10', '10'),
                                             ('15', '15'), ('20', '20'), ('25', '25'),
                                             ('30', '30'), ('35', '35'), ('40', '40'),
                                             ('45', '45'), ('50', '50'), ('55', '55'),
                                            ], 'Minutes', required=True),

        'event': fields.char('event', size=255, help="If Event is Possible"),
        
        'user_ids': fields.many2many('res.users', 'user_appointment_rel',
                                        'appointment_id',
                                        'user_id'),
        'clash':fields.boolean('Clash'),
        'location':fields.char('Location', size=255),
        'state':fields.selection([
             ('none', 'None'),
             ('active', 'Active'),
             ('active_clash', 'Active Clash'),
             ('cancelled', 'Cancelled'),
             ('cancelled_within_two_days', 'Cancelled Within 48 Hours'),
             ('confirmed', 'Confirmed'),
             ('completed', 'Completed')
             ],
             'Status',
             required=True),
        'reason':fields.text('Reason'),
        'not_booked_further':fields.boolean('Should the Appointment Not Be Booked Further'),
        'communication_id':fields.one2many('cmc.assessment.communication', 'appointment_id', ''),
        'description':fields.char('Description', size=255),
        'is_fail_to_attend':fields.boolean('Fail to Attend'),
        'cancel_date':fields.datetime('Cancellation Date'),
        'save_clash':fields.boolean('Save With Clash', help='This Will save The Appointment If there is a Clash'),
        'from_where':fields.selection([('Workshop', 'Workshop'),
                                       ('Equipment Supply Process', 'Equipment Supply Process')], 'From Where'),
        'cancel_date':fields.datetime('Cancel Time'),
        'complete_date':fields.datetime('Complete Date'),
        'cancel_within_two_days':fields.char('Cancel', size=100),
        'from_appointment':fields.char('From', size=100),
        'is_paid':fields.boolean('Invoice/Paid'),
        
        'ass_type':fields.char('',size=100)
        
    }
    _defaults = {
        'state': lambda * a: 'none',
        'apmnt_start_date':lambda * a: datetime.datetime.now().strftime('%Y-%m-%d'),
        'start_time_hour':lambda * a: '09',
        'owner':lambda self, cr, uid, ctx : uid,
        'clash':lambda * a: True,
        'type':lambda * a: 'general',
        'save_clash':lambda * a: True,
        
     }
    
    def onchange_hour(self, cr, uid, ids, hour, context={}):
        values = {}
        values['value'] = {}
        h = int(hour)
        h = (h + 1) % 24
        values['value']['end_time_hour'] = str(h) if h / 10 > 0 else "0" + str(h)
        return values
    def onchange_minutes(self, cr, uid, ids, minutes, context={}):
        values = {}
        values['value'] = {}
        values['value']['end_time_minutes'] = str(minutes)
        return values
    def onchange_assessor(self, cr, uid, ids, owner, title, parent_id, from_where, context={}):
        values = {}
        values['value'] = {}
        e_b_ids = ""
        if parent_id:
            if from_where == 'cmc.assessment':
                if title != False:
                    query = "SELECT name FROM res_users WHERE id=" + (str(owner))
                    cr.execute(query)
                    # debug(title)
                    owner_name = cr.fetchone()
                    title_check = title.split(" - ")
                    if parent_id:
                           values['value']['title'] = title_check[0] + " - " + title_check[1] + " - " + owner_name[0]
                    else:
                            values['value']['title'] = owner_name[0]
                    #debug(values['value']['title'])
            elif from_where == 'cmc.equipement.supply.process':
                equipment_browse = pooler.get_pool(cr.dbname).get('cmc.equipement.supply.process').browse(cr, uid, int(parent_id))
                values['value']['title'] = equipment_browse.client_id.display_name
                query = "select id from cmc_equipment where state='booked' and id in (select equipment_id from equipment_equipment_rel where supply_id=" + parent_id + ")"
                cr.execute(query)
                e_b_ids = cr.fetchall()
                if e_b_ids is not None:
                    values['value']['equipment_ids'] = [e[0] for e in e_b_ids]
            elif from_where == 'cmc.workshop.process':
                workshop_browse = pooler.get_pool(cr.dbname).get('cmc.workshop.process').browse(cr, uid, int(parent_id))
                values['value']['title'] = (workshop_browse.job_no if workshop_browse.job_no else "")+("-"+workshop_browse.make) + "-" + workshop_browse.model +(("-"+workshop_browse.equipment_id.current_user_id.display_name) if workshop_browse.equipment_id.current_user_id else "")
        else:
            query = "SELECT name FROM res_users WHERE id=" + (str(owner))
            cr.execute(query)
            owner_name = cr.fetchone()
            values['value']['title'] = owner_name[0]
        return values
    def onchange_date(self, cr, uid, ids, date, parent_id, owner, from_where,ass_type=False, context={}):
        values = {}
        values['value'] = {}
        #debug(ids)
        query = "SELECT name FROM res_users WHERE id=" + (str(owner))
        cr.execute(query)
        owner_name = cr.fetchone()
        values['value']['apmnt_date_end'] = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=0)).strftime("%Y-%m-%d")
        if parent_id:
            if from_where == 'cmc.assessment':
                appointments_id = pooler.get_pool(cr.dbname).get('cmc.assessment').search(cr, uid, [("id", "=", int(parent_id))])
                appointments_browse = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, appointments_id[0])
                values['value']['title'] = appointments_browse.ref_id + " - " + appointments_browse.client_person_id.display_name + " - " + owner_name[0]
                values['value']['location'] = appointments_browse.where if appointments_browse.where != 'Other' else appointments_browse.other_where
                values['value']['ass_type']=(appointments_browse.driving_assessment_type if appointments_browse.driving_assessment_type in ('Driving Tution','Drive From Wheelchair Tution','MoMap Familiarisation') else "") if ass_type not in ('Driving Tution','Drive From Wheelchair Tution','MoMap Familiarisation') else ass_type
            elif from_where == 'cmc.workshop.process':
                workshop_id = pooler.get_pool(cr.dbname).get('cmc.workshop.process').search(cr, uid, [("id", "=", int(parent_id))])
                workshop_br = pooler.get_pool(cr.dbname).get('cmc.workshop.process').browse(cr, uid, workshop_id[0])
                values['value']['location'] = 'North East Drive Mobility' if not workshop_br.work_off_site else workshop_br.work_where 
        else:
            values['value']['title'] = owner_name[0]
        return values
    
    
cmc_appointments()


class cmc_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    _columns = {
        'appointments': fields.many2many('cmc.appointments', 'user_appointment_rel',
                                'user_id',
                                'appointment_id'),

         }
cmc_users()
