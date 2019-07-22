import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp

#ssl
import ssl

if sys.version_info < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf8')
else:
    raw_input = input
#client class
class ChatBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, room, nick):
        #room
        self.room = room
        #nickname
        self.nick = nick

#handlers
        #session start
        self.add_event_handler("session_start", self.start)
        #group msg
        self.add_event_handler("groupchat_message", self.muc_message)
        #room presence
        self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)

  def start(self, event):
          self.get_roster()
          self.send_presence()
          self.plugin['xep_0045'].joinMUC(self.room, self.nick, wait=True)

  def muc_message(self, msg):
          #auto reply when mentioned
          if msg['mucnick'] != self.nick and self.nick in msg['body']:
              self.send_message(mto=msg['from'].bare, mbody="I heard that, %s." % msg['mucnick'], mtype='groupchat')

  #greetings
  def muc_online(self, presence):
      if presence['muc']['nick'] != self.nick:
          self.send_message(mto=presence['from'].bare, mbody="Hello, %s %s" % (presence['muc']['role'], presence['muc']['nick']), mtype='groupchat')

    
    






