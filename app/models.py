from flask_appbuilder import Model
from flask import Markup
from flask_appbuilder.models.decorators import renders
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime


class Certificates(Model):
    id = Column(Integer, primary_key=True)
    dns_name = Column(String(100), nullable=False)
    endpoint_ip = Column(String(16))
    subject = Column(String(100))
    grade = Column(String(4))
    issuer = Column(String(100))
    last_scan_dtg = Column(DateTime)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    expires_in_days = Column(Integer)
    key_value = Column(String(50))
    sha1_fingerprint = Column(String(100))
    
    @renders('grade')
    def grade_formatter(self):
        if self.grade is not None:
            if ('A') in self.grade:
                return Markup('<B><font color=Green>' + self.grade + '</font></B>')
            elif ('B' or 'C') in self.grade:
                return Markup('<B><font color=Orange>' + self.grade + '</font></B>')
            elif ('D' or 'F') in self.grade:
                return Markup('<B><font color=Red>' + self.grade + '</font></B>')
            else: 
                return self.grade
        else: 
            return self.grade

    @renders('expiration_in_days')
    def expiration_formatter(self):
        if self.valid_to is not None:
            print (self.valid_to.timestamp())
            print (str(datetime.datetime.utcnow().timestamp()))
            x = int((self.valid_to.timestamp() - datetime.datetime.utcnow().timestamp()) / 60 / 60 / 24)
            print ("X = ", str(x))
            if x < 30:
                return Markup('<B><font color=Red>' + str(x) + ' days</font></B>')
            elif x < 90:
                return Markup('<B><font color=Orange>' + str(x) + ' days</font></B>')
            else:
                return (str(x) + " days")
        else: 
            return self.valid_to

    @renders('url')
    def url_formatter(self):
        return Markup('<a href=https://www.ssllabs.com/ssltest/analyze.html?d=' + self.dns_name + '&hideResults=on rel=noopener target=_blank>' + self.dns_name + '</a>')

    def __repr__(self):
        return "%s" % self.dns_name
