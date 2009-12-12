import win32clipboard as w 
import win32con
#import wx
import pyHook
import win32api
import time
import re

from dispatch.dispatcher import Signal

#-------------------------------
class Clipboard(object):
  #===============================
  @property
  def text(self): 
    w.OpenClipboard() 
    d=w.GetClipboardData(win32con.CF_TEXT) 
    w.CloseClipboard() 
    return d 
  
  #===============================
  @text.setter
  def text(self, text): 
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(w.CF_TEXT, text) 
    w.CloseClipboard()
  
  #===============================
  def copy_selected_text(self):
    #win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)
    #win32api.keybd_event(win32con.VK_MENU,0,win32con.KEYEVENTF_KEYUP,0)
    #win32api.keybd_event(ord('C'),0,win32con.KEYEVENTF_KEYUP,0)
    
    #time.sleep(0.2)
    
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0); 
    win32api.keybd_event(ord('C'), 0, 0, 0);
    time.sleep(0.2) # Need this delay for it to go into the clipboard
    win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0); 
    win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)

#-------------------------------
class Hotkey(object):
  #===============================
  def __init__(self):
    #self.binds = [{
    #  'name': 'CLIPBOARD',
    #  'keys': ('Lcontrol', 'Lmenu', 'C')
    #}, {
    #  'name': 'URL',
    #  'keys': ('Lcontrol', 'Lmenu', 'B')
    #}]
    self.binds = []
    
    #for bind in self.binds:
    #  bind['truths'] = [False for key in bind['keys']]
    #  bind['final_truths'] = [False for key in bind['keys']]
    
    self.event = Signal()
  
  #===============================
  def add_bind(self, name, string):
    keys = re.findall(r'(\w+)', string)
    
    #modifiers = []
    #members = inspect.getmembers()
    #for modifier in keys[:-1]:
    
    # Process the keys
    for index,key in enumerate(keys):
      if key == 'alt':
        keys[index] = re.compile('^(Lmenu|Rmenu)$')
      elif key == 'control':
        keys[index] = re.compile('^(Lcontrol|Rcontrol)$')
      else:
        keys[index] = re.compile('{0}{1}{2}'.format('^', key, '$') )       
        
    self.binds.append({
      'name': name,
      'keys': keys,
      'truths': [False for key in keys],
      'final_truths': [False for key in keys]
    })
    
  
  #===============================
  def loop(self):    
    hm = pyHook.HookManager()
    # register two callbacks
    #hm.MouseAllButtonsDown = OnMouseEvent
    hm.KeyDown = self.handle_keydown
    hm.KeyUp = self.handle_keyup

    # hook into the mouse and keyboard events
    #hm.HookMouse()
    hm.HookKeyboard()
    import pythoncom
    pythoncom.PumpMessages()
  
  #===============================
  def handle_keydown(self, event):
    for bind in self.binds:
      for count,key in enumerate(bind['keys']):
        if key.match(event.Key):
          bind['truths'][count] = True
      
    return True      
    
  #===============================
  def handle_keyup(self, event):
    for bind in self.binds:
      for count,key in enumerate(bind['keys']):
        if key.match(event.Key):
          if all(bind['truths']):
            bind['final_truths'][count] = True
          else:
            bind['truths'][count] = False
          
      if all(bind['final_truths']):
        bind['truths'] = [False for key in bind['keys']]
        bind['final_truths'] = [False for key in bind['keys']]
        
        self.event.send(sender=self.__class__, name=bind['name'])
    
    return True
    