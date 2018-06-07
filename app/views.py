from flask import render_template, flash, Flask, redirect, request, url_for, jsonify, json, Markup
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, AppBuilder, expose, BaseView, has_access, SimpleFormView
from flask_appbuilder.actions import action
from app import appbuilder, db, app
from .models import Certificates
from os import getenv
import requests
import datetime
import time
import atexit ###
import sys
from apscheduler.schedulers.background import BackgroundScheduler ###
from apscheduler.triggers.interval import IntervalTrigger ###


#### TODO: 
# Chart for grade distribution on HomeView or "grade distribution menu item"
# Chart for expiration (0-30, 30-90, 90-180, 180+) on HomeView
# Combine scans (adhoc or periodic) into a function and call that function instead of copying the code
# Create external alert via email, slack, etc.
# Expire session for logged in user.
# Check "hasWarnings" value and display something to user to follow-up

API = 'https://api.ssllabs.com/api/v2/'

def env_var(name):
    """
    Look up an env var by name.
    If the env var is not defined, print a standard message to STDERR and exit.
    """
    value = getenv(name, None)

    if value is None:
        print("You must set the environment variable", name, file=sys.stderr)
        sys.exit(1)

    return value

def send_external_alert(item):
    ### TODO: Configure for sending alerts via slack, email, or whatever.
    return


#### TESTING SCHEDULING HERE ###
def periodic_scan():
    #print time.strftime("%A, %d. %B %Y %I:%M:%S %p")
    query = db.session.query(Certificates.dns_name.distinct().label("target"))
    targets = [row.target for row in query.all()]
    for target in targets:
        print ("Starting scan of: " + str(target))
        r = requests.get('https://api.ssllabs.com/api/v2/analyze?host=' + target + '&all=on')
        data = r.json()
        while data['status'] != 'READY' and data['status'] != 'ERROR':
            time.sleep(30)
            r = requests.get('https://api.ssllabs.com/api/v2/analyze?host=' + target + '&all=on')
            data = r.json()
        if data['status'] == 'ERROR':
            return 
        print (data)
        host = str(data['host'])
        dtg = datetime.datetime.utcfromtimestamp(int(data['testTime']/1000)).replace(tzinfo=datetime.timezone.utc)
        #### Check if result is valid(ish)
        if any(data['endpoints'][0]['details']['cert']):
            db.session.query(Certificates).filter_by(dns_name=host).delete() ##do this here so it won't delete row unless it is a valid query.
            db.session.commit()            
            for endpoint in data['endpoints']:
                db.session.add(Certificates(dns_name=host, endpoint_ip=str(endpoint['ipAddress']), subject=str(endpoint['details']['cert']['subject']), grade=str(endpoint['grade']), last_scan_dtg=dtg, \
                    issuer=endpoint['details']['cert']['issuerLabel'], valid_from=datetime.datetime.utcfromtimestamp(int(endpoint['details']['cert']['notBefore']) / 1000).replace(tzinfo=datetime.timezone.utc), \
                    valid_to=datetime.datetime.utcfromtimestamp(int(endpoint['details']['cert']['notAfter']) / 1000).replace(tzinfo=datetime.timezone.utc), \
                    key_value=str(endpoint['details']['key']['alg'] + str(endpoint['details']['key']['size'])), sha1_fingerprint=str(endpoint['details']['cert']['sha1Hash']) \
                        ))
                db.session.commit()
                print ("Finished scan of: " + str(target))
        else:
            for endpoint in data['endpoints']:
                db.session.query(Certificates).filter_by(dns_name=host).delete()
                db.session.add(Certificates(dns_name=host, endpoint_ip=str(endpoint['ipAddress']), subject="Scan failure. Validate certificate manually.", grade="X"))
                db.session.commit()
    return

scheduler = BackgroundScheduler()
scheduler.add_job(periodic_scan, 'interval', hours=24)
scheduler.start()
print (str(scheduler.print_jobs()))

atexit.register(lambda: scheduler.shutdown())


################################


class HomeView(BaseView):
    default_view = '/authenticated/'
    route_base = "/home"

    @ expose('/authenticated/')
    def authenticated(self):
        return self.render_template('auth_index.html')


class CertificateModelView(ModelView):
    datamodel = SQLAInterface(Certificates)
    base_order = ('dns_name', 'asc')
    list_columns = ['url_formatter', 'endpoint_ip', 'grade_formatter', 'last_scan_dtg', 'subject', 'issuer', 'valid_from', 'valid_to', 'expiration_formatter', 'key_value', 'sha1_fingerprint']
    add_columns = ['dns_name']
    label_columns = {'url_formatter':'Domain', 'endpoint_ip':'Endpoint IP', 'grade_formatter':'Grade', 'last_scan_dtg':'Last Scan', 'subject':'Subject', 'issuer':'Issuer', 'valid_from':'Valid From', \
    'valid_to':'Valid To', 'expiration_formatter':'Expires In', 'key_value':'Key', 'sha256_fingerprint':'SHA1 Fingerprint'} 
    #page_size=25
    page_size=10
    @action("scan_host", "Scan this host", "This scan may take a few minutes.  Page will reload when complete.  Please be patient...", "fa-question", single=False)
    def scan_host(self, items):
        if isinstance(items, list):
            for item in items:
                r = requests.get('https://api.ssllabs.com/api/v2/analyze?host=' + item.dns_name + '&all=on')
                data = r.json()
                while data['status'] != 'READY' and data['status'] != 'ERROR':
                    time.sleep(30)
                    r = requests.get('https://api.ssllabs.com/api/v2/analyze?host=' + item.dns_name + '&all=on')
                    data = r.json()
                if data['status'] == 'ERROR':
                    flash("Scan failed!  Verify that your URL is valid: " + str(item.dns_name), 'danger')
                    return redirect('/certificatemodelview/list/')
                print (data)
                host = str(data['host'])
                dtg = datetime.datetime.utcfromtimestamp(int(data['testTime']/1000)).replace(tzinfo=datetime.timezone.utc)
                if any(data['endpoints'][0]['details']['cert']):
                    db.session.query(Certificates).filter_by(dns_name=host).delete() ##do this here so it won't delete row unless it is a valid query.
                    db.session.commit()
                    for endpoint in data['endpoints']:
                        db.session.add(Certificates(dns_name=host, endpoint_ip=str(endpoint['ipAddress']), subject=str(endpoint['details']['cert']['subject']), grade=str(endpoint['grade']), last_scan_dtg=dtg, \
                            issuer=endpoint['details']['cert']['issuerLabel'], valid_from=datetime.datetime.utcfromtimestamp(int(endpoint['details']['cert']['notBefore']) / 1000).replace(tzinfo=datetime.timezone.utc), \
                            valid_to=datetime.datetime.utcfromtimestamp(int(endpoint['details']['cert']['notAfter']) / 1000).replace(tzinfo=datetime.timezone.utc), \
                            key_value=str(endpoint['details']['key']['alg'] + str(endpoint['details']['key']['size'])), sha1_fingerprint=str(endpoint['details']['cert']['sha1Hash']) \
                                ))
                        db.session.commit()
                    flash("Scan finished for: " + str(item.dns_name), 'success')
                else:
                    for endpoint in data['endpoints']:
                        db.session.query(Certificates).filter_by(dns_name=host).delete()
                        db.session.add(Certificates(dns_name=host, endpoint_ip=str(endpoint['ipAddress']), subject="Scan failure. Validate certificate manually.", grade="X"))
                        db.session.commit()
        return redirect('/certificatemodelview/list/') 




@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()


### Register Views ###
appbuilder.add_view_no_menu(HomeView)
appbuilder.add_view(CertificateModelView, "Certificates", icon="fa-search", category="Certificates", category_icon="fa-search")


appbuilder.security_cleanup() #cleanup any dangling permissions


