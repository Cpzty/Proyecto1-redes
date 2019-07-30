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
    def __init__(self, jid, password, room, nick):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        #file send plugin
        self.register_plugin('xep_0047', {
            'auto_accept': True
        })
        #room
        self.room = room
        #nickname
        self.nick = nick
        #recipient
        #self.recipient = recipient
        #message
        self.add_event_handler("message", self.message, threaded=True)
        #start
        self.add_event_handler("session_start", self.start, threaded=True)
        #register
        self.add_event_handler("register", self.register, threaded=True)
        #group chat message
        self.add_event_handler("groupchat_message", self.muc_message, threaded=True)
        #group chat presence
        self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online, threaded=True)
        #file send handlers
        self.add_event_handler("ibb_stream_start", self.stream_opened, threaded=True)
        self.add_event_handler("ibb_stream_data", self.stream_data)

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

    def remove_user(self):
        #remove user
        resp = self.Iq()
        resp['type'] = 'set'
        resp['from'] = self.boundjid.user
        resp['register'] = ' '
        resp['register']['remove'] = ' '
        try:
            print(resp)
            resp.send(now=True)
            print("Account deleted for %s!" % self.boundjid)
        except IqError as e:
            logging.error("Could not delete account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print ("%(body)s" % msg)

    def muc_message(self, msg):
            if msg['mucnick'] != self.nick and self.nick in msg['body']:
                print ("%(body)s" % msg)

    def muc_online(self, presence):
            if presence['muc']['nick'] != self.nick:
                self.send_message(mto=presence['from'].bare,
                mbody="Hello, %s %s" % (presence['muc']['role'],
                presence['muc']['nick']),
                mtype='groupchat')

    def accept_stream(self, iq):
            return True

    def stream_opened(self, stream):
        print('Stream opened: %s from %s' % (stream.sid, stream.peer_jid))

    def stream_data(self, event):
            print(event['data'])

    def send_filerino(self,whotosend, filetosend):
            stream = self['xep_0047'].open_stream(whotosend)
        
            with open(filetosend) as f:
                data = f.read()
                stream.sendall(data)
            

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

        optp.add_option("-r", "--room", dest="room",
                    help="MUC room to join")
        optp.add_option("-n", "--nick", dest="nick",
                    help="MUC nickname")


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
        opts.nick = raw_input("Nickname: ")
        opts.room = raw_input("Room to join: ")
        
        xmpp = ChatBot(opts.jid, opts.password, opts.nick, opts.room)

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
        xmpp.register_plugin('xep_0045') # multichat
        #xmpp.register_plugin('xep_0047') # file

        
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
                        print("press 10 for group message")
                        ch = raw_input(">: ")
                #disconnect
                        if(ch == str(1)):
                                print("disconnecting")
                                xmpp.disconnect()
                                break
                #eliminate account
                        elif(ch == str(2)):
                                xmpp.remove_user()
                                xmpp.disconnect()
                                break
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
                #join a room
                        elif(ch == str(6)):
                                print("joining room")
                                xmpp.plugin['xep_0045'].joinMUC(xmpp.room, xmpp.nick)
                                
                #presence message
                        elif(ch == str(7)):
                                print("what status would u like to show?")
                                status = raw_input(">: ")
                                print("presence show?")
                                show = raw_input(">: ")
                                xmpp.makePresence(pfrom=xmpp.jid, pstatus=status, pshow=show)
                #send a message
                        elif(ch==str(8)):
                                print("who is the message for?")
                                user_to_send = raw_input(">: ")
                                print("what is your message?")
                                msg_to_send = raw_input(">: ")
                                print("sending msg")
                                xmpp.send_message(mto=user_to_send, mbody = msg_to_send, mtype = 'chat')
                                #xmpp.message(msg.type='chat')
                #send file
                        elif(ch==str(9)):
                                print("Who would u like to send a file to?")
                                file_receiver = raw_input(">: ")
                                print("What is the name file?")
                                file_to_send = raw_input(">: ")
                                #stream = xmpp['xep_0047'].open_stream(file_receiver)
                                xmpp.send_filerino(file_receiver, file_to_send)
                                #with open(file_to_send) as f:
                                  #      data = f.read()
                                    #    stream.sendall(data)
                                
                #group message
                        elif(ch==str(10)):
                                print("what would u like to send?")
                                grpmsg = raw_input(">: ")
                                xmpp.send_message(mto='all',
                                mbody=grpmsg,
                                mtype='groupchat')

        else:
                print("Unable to connect.")









        
