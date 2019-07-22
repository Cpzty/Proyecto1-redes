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
    def __init__(self, jid, password, recipient, message):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        #recipient
        self.recipient = recipient
        #message
        self.msg = message
         #start
        self.add_event_handler('session_start', self.start)

    def start(self, event):
          self.send_presence()
          self.get_roster()
          #send msg
          self.send_message(mto=self.recipient, mbody = self.msg, mtype = 'chat')
          #remove user
          self.del_roster_item(self.jid)
          #disconnect
          self.disconnect(wait=True)

if __name__ == '__main__':
        optp = OptionParser()

        #verbose
        optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
        
        optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
        
        optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

        #user
        optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
        
        optp.add_option("-p", "--password", dest="password",
                    help="password to use")
        
        optp.add_option("-t", "--to", dest="to",
                    help="JID to send the message to")
        
        optp.add_option("-m", "--message", dest="message",
                    help="message to send")

        opts, args = optp.parse_args()

        #logging config
        logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

        if opts.jid is None:
                opts.jid = raw_input("Username: ")
        
        if opts.password is None:
                opts.password = getpass.getpass("Password: ")
        if opts.to is None:
                opts.to = raw_input("Send To: ")
        if opts.message is None:
                opts.message = raw_input("Message: ")

#initialize
        xmpp = ChatBot(opts.jid, opts.password, opts.to, opts.message)
        #plugins
        xmpp.register_plugin('xep_0030') # Service Discovery
        xmpp.register_plugin('xep_0199') # XMPP Ping

        if xmpp.connect():
                xmpp.process(block=True)
                print("Done")
        else:
                print("Unable to connect.")









        
