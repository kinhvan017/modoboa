# coding: utf-8

from django.db import models
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _, ugettext_noop
from modoboa.admin.models import User

limits_tpl = [
    ("domain_admins_limit", ugettext_noop("Domain admins")),
    ("domains_limit", ugettext_noop("Domains")),
    ("domain_aliases_limit", ugettext_noop("Domain aliases")),
    ("mailboxes_limit", ugettext_noop("Mailboxes")),
    ("mailbox_aliases_limit", ugettext_noop("Mailbox aliases"))
    ]

class LimitsPool(models.Model):
    user = models.OneToOneField(User)

    def create_limits(self):
        for ltpl in limits_tpl:
            l = Limit()
            l.name = ltpl[0]
            l.pool = self
            l.save()

    def getcurvalue(self, lname):
        l = self.limit_set.get(name=lname)
        return l.curvalue

    def getmaxvalue(self, lname):
        l = self.limit_set.get(name=lname)
        return l.maxvalue

    def inc_curvalue(self, lname, nb=1):
        l = self.limit_set.get(name=lname)
        l.curvalue += nb
        l.save()

    def dec_curvalue(self, lname, nb=1):
        l = self.limit_set.get(name=lname)
        if not l.curvalue:
            return
        l.curvalue -= nb
        l.save()

    def dec_limit(self, lname, nb=1):
        l = self.limit_set.get(name=lname)
        l.curvalue -= nb
        if l.maxvalue > -1:
            l.maxvalue -= nb
        l.save()

    def inc_limit(self, lname, nb=1):
        l = self.limit_set.get(name=lname)
        l.curvalue += nb
        if l.maxvalue > -1:
            l.maxvalue += nb
        l.save()

    def will_be_reached(self, lname, nb=1):
        l = self.limit_set.get(name=lname)
        if l.maxvalue <= -1:
            return False
        if l.curvalue + nb > l.maxvalue:
            return True
        return False

    def get_limit(self, lname):
        try:
            return self.limit_set.get(name=lname)
        except Limit.DoesNotExist:
            return None

class Limit(models.Model):
    name = models.CharField(max_length=255)
    curvalue = models.IntegerField(default=0)
    maxvalue = models.IntegerField(default=-2)
    pool = models.ForeignKey(LimitsPool)

    class Meta:
        unique_together = (("name", "pool"),)

    @property
    def usage(self):
        if self.maxvalue < 0:
            return -1
        if self.maxvalue == 0:
            return 0
        return int(float(self.curvalue) / self.maxvalue * 100)

    @property
    def label(self):
        for l in limits_tpl:
            if l[0] == self.name:
                return l[1]
        return ""

    def __str__(self):
        if self.maxvalue == -2:
            return _("undefined")
        if self.maxvalue == -1:
            return _("unlimited")
        return "%d%%" % self.usage