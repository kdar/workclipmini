import socket
import hashlib
import time
import os

from twisted.internet.protocol import DatagramProtocol

from dispatch.dispatcher import Signal

#-------------------------------
class Network(DatagramProtocol):
  #===============================
  def __init__(self, addr, port):
    self.addr = addr
    self.port = port
    self.nodename = socket.gethostname()
    self.addresses = set()
    self.sha = hashlib.sha1()
    
    self.name = 'miniworkclip'
    self.uid = self.get_uid()
    
    self.command = Signal()

  #===============================
  def startProtocol(self):
    self.transport.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)

  #===============================
  def refresh_list(self):
    self.addresses = set()
    self.ping()
 
  #===============================
  def get_uid(self):
    self.sha.update('{0}{1}{2}{3}'.format(self.nodename, time.time(), os.getpid(), os.getcwd()))
    return self.sha.hexdigest()
 
  #===============================
  def ping(self):
    self.send(self.addr, 'PING')

  #===============================
  def pong(self):
    self.send(self.addr, 'PONG')
  
  #===============================
  def send(self, addr, *args):
    if args:
      self.transport.write('{0}:{1}:{2}:{3}'.format(self.name, self.nodename, self.uid, ' '.join(args)), (addr, self.port))

  #===============================
  def datagramReceived(self, data, address):
    broadcast_packet = False
    parts = str(data).split(':', 3)
    if len(parts) == 4 and parts[0] == self.name and parts[2] != self.uid:
      if parts[3] == 'PING':
        self.addresses.add(address[0])
        self.pong()
        broadcast_packet = True
      elif parts[3] == 'PONG':        
        self.addresses.add(address[0])
        broadcast_packet = True
    
      if not broadcast_packet:
        self.command.send(sender=self.__class__, data=data, address=address[0], nodename=parts[1], uid=parts[2], command=parts[3])
    


