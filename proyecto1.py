import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout

#time for delete user as server attempts to delete before it is created
import time
#ssl
import ssl

if sys.version_info < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf8')
else:
    raw_input = input
#client class
class ChatBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password,):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        #recipient
        #self.recipient = recipient
        #message
        self.add_event_handler("message", self.message, threaded=True)
        #start
        self.add_event_handler("session_start", self.start, threaded=True)
        #register
        self.add_event_handler("register", self.register, threaded=True)

    def start(self, event):
          self.send_presence()
          self.get_roster()
          #send msg
          #self.send_message(mto=self.recipient, mbody = self.msg, mtype = 'chat')
          #disconnect
          #self.disconnect(wait=True)

    def register(self,event):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        try:
            resp.send(now=True)
            logging.info("Account created for %s!" % self.boundjid)
        except IqError as e:
            logging.error("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()

    def remove_item(self):
        #remove user
        self.del_roster_item(self.jid)

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print ("%(body)s" % msg)

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

        #if opts.jid is None:
          #      opts.jid = raw_input("Username: ")
        
        #if opts.password is None:
          #      opts.password = getpass.getpass("Password: ")
        #if opts.to is None:
                #opts.to = raw_input("Send To: ")
        #if opts.message is None:
                #opts.message = raw_input("Message: ")

#initialize
        print("Press 1 to register")
        print("Press 2 to login")
        login_register = raw_input(">: ")

                
        opts.jid = raw_input("Username: ")
        opts.password = getpass.getpass("Password: ")
        
        xmpp = ChatBot(opts.jid, opts.password,)

        if(login_register == str(2)):
                xmpp.del_event_handler("register", xmpp.register)
        
        #plugins
        xmpp.register_plugin('xep_0030') # Service Discovery
        xmpp.register_plugin('xep_0004') # Data forms
        xmpp.register_plugin('xep_0060') # PubSub
        xmpp.register_plugin('xep_0199') # XMPP Ping
        #registration related
        xmpp.register_plugin('xep_0066') # Out-of-band Data
        xmpp.register_plugin('xep_0077') # In-band Registration

        
        #authentication over an unencrypted connection
        xmpp['feature_mechanisms'].unencrypted_plain = True
        xmpp.ssl_version = ssl.PROTOCOL_TLS

        
        if xmpp.connect(('alumchat.xyz', 5222)):
        #if xmpp.connect():
                xmpp.process(block=False)
                #xmpp.remove_item()
                time.sleep(5)
                while True:
                        print("press 1 to disconnect")
                        print("press 2 to eliminate the account from the server")
                        print("press 3 to see all users")
                        print("press 4 to add a user")
                        print("press 5 to see details of a user")
                        print("press 6 to join a group chat")
                        print("press 7 to set presence message")
                        print("press 8 to send a message")
                        #may fuse with send message
                        print("press 9 to send a file")
                        ch = raw_input(">: ")
                #disconnect
                        if(ch == str(1)):
                                print("disconnecting")
                                xmpp.disconnect()
                                break
                #eliminate account
                        elif(ch == str(2)):
                                print("in progress")
                #see all contacts
                        elif(ch == str(3)):
                                print("showing all contacts\n")
                                print(xmpp.client_roster)
                                print(" ")
                #request subscription to user
                        elif(ch ==str(4)):
                                print("enter the name of the user")
                                friend_request = raw_input(":> ")
                                xmpp.send_presence(pto=friend_request, ptype='subscribe')
                #send a message
                        elif(ch==str(8)):
                                print("who is the message for?")
                                user_to_send = raw_input(">: ")
                                print("what is your message?")
                                msg_to_send = raw_input(">: ")
                                print("sending msg")
                                xmpp.send_message(mto=user_to_send, mbody = msg_to_send, mtype = 'chat')
                                #xmpp.message(msg.type='chat')

        else:
                print("Unable to connect.")









        
