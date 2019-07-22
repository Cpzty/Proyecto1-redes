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
class EchoBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        super(EchoBot, self).__init__(jid, password)
        
        #session start
        self.add_event_handler('session_start', self.start)
        #message handler
        self.add_event_handler('message', self.message)
        
    #presence notifies other users that you are online and get_roster fetches users
    def start(self, event):
        self.send_presence()
        self.get_roster()

    #message
    def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            self.send_message(mto=msg['from'], mbody='Thanks for sending: \n%s' % msg['body'])
            
    
    

if __name__ == '__main__':
    optp = OptionParser()

    optp.add_option('-d', '--debug', help='set logging to DEBUG', action= 'store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO)
    optp.add_option("-j", "--jid", dest="jid", help="JID to use")
    optp.add_option("-p", "--password", dest="password", help="password to use")

    opts, args = optp.parse_args()

    logging.basicConfig(level=opts.loglevel, format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")

    xmpp = EchoBot(opts.jid, opts.password)
    #service discovery
    xmpp.register_plugin('xep_0030')
    #ping
    xmpp.register_plugin('xep_0199')

    #xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    if xmpp.connect():
        xmpp.process(block=True)
        print("Connected")
    else:
        print("Unable to connect")


    
    






