# Author: Kevin Darlington
# License: MIT
# Version: 0.1

import threading
import os
import time
import re
import webbrowser

from twisted.internet import reactor
from twisted.internet import task

from network import Network

if os.name == 'posix':
  try:
    import linux as anyos
  except:
    import mac as anyos
if os.name == 'nt':
  import windows as anyos
  
#-------------------------------
class WorkclipMini(object):
  #===============================
  def __init__(self):
    self.clipboard = anyos.Clipboard()
    self.hotkey = anyos.Hotkey()
    self.hotkey.event.connect(self.on_hotkey)
    self.network = Network('192.168.0.255', 45644)
    self.network.command.connect(self.on_command)
    
    
    self.hotkey.add_bind('CLIPBOARD', '<control><alt>C')
    self.hotkey.add_bind('URL', '<control><alt>B')    
    
    chrome = os.path.join(os.environ.get('LOCALAPPDATA') or '', 'Google\\Chrome\\Application\\chrome.exe')
    extra_browsers = [chrome, 'chrome.exe']
    for browser in extra_browsers:
      if webbrowser._iscommand(browser):
        webbrowser.register(browser, None, webbrowser.BackgroundBrowser(browser), -1)
    
  #===============================
  def run(self):
    thread = threading.Thread(target=self.loop)
    thread.start()
    self.hotkey.loop()
  
  #===============================
  def on_command(self, command, **kwargs):
    command = command.split(' ', 1)
    
    if command[0] == 'CLIPBOARD':
      self.clipboard.text = command[1]
    elif command[0] == 'URL':
      webbrowser.open_new_tab(command[1])
      
  #===============================
  def on_hotkey(self, name, **kwargs):
    self.clipboard.copy_selected_text()
    text = self.clipboard.text
    
    if name == 'CLIPBOARD':
      for address in self.network.addresses:
        self.network.send(address, name, text)
    elif name == 'URL':
      urls = re.findall(r'(([a-zA-Z]+://)?(www.)?[^ ]+\.[^ \n\r]{2,})', text, re.IGNORECASE)
      if not urls:
        urls = [[text,],]
        
      for url in urls:
        for address in self.network.addresses:
          self.network.send(address, name, url[0])

  #===============================
  def loop(self):    
    reactor.listenUDP(45644, self.network)
    refresh = task.LoopingCall(self.network.refresh_list)
    refresh.start(30) # Refresh list at rate defined in config.py
    reactor.run(False)


#===============================
if __name__ == '__main__':
  WorkclipMini().run()
