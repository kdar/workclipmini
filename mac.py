import subprocess
import re
import appscript

import AppKit
from PyObjCTools import AppHelper
from Carbon.CarbonEvt import RegisterEventHotKey, GetApplicationEventTarget
from Carbon.Events import cmdKey, controlKey, shiftKey, optionKey

from dispatch.dispatcher import Signal

kEventHotKeyPressedSubtype = 6
kEventHotKeyReleasedSubtype = 9

import sys
class property(property):
  def __init__(self, fget, *args, **kwargs):
    self.__doc__ = fget.__doc__
    super(property, self).__init__(fget, *args, **kwargs)

  def setter(self, fset):
    cls_ns = sys._getframe(1).f_locals
    for k, v in cls_ns.iteritems():
      if v == self:
        propname = k
        break
    cls_ns[propname] = property(self.fget, fset,
                                self.fdel, self.__doc__)
    return cls_ns[propname]

#-------------------------------
class Clipboard(object):
  #===============================
  @property
  def text(self): 
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    retcode = p.wait()
    text = p.stdout.read()
    return text
  
  #===============================
  @text.setter
  def text(self, text):
    print "pbcopy called"
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(text)
    p.stdin.close()
    retcode = p.wait()
  
  #===============================
  def copy_selected_text(self):
    appscript.app('System Events').keystroke('c', using=appscript.k.command_down)

#-------------------------------
class HotKeyApp(AppKit.NSApplication):
  #===============================
  def finishLaunching(self):
    super(HotKeyApp, self).finishLaunching()
    # register cmd-control-J
    self.hotKeyRef = RegisterEventHotKey(38, cmdKey | controlKey, (0, 0), GetApplicationEventTarget(), 0)

  #===============================
  def sendEvent_(self, theEvent):
    if theEvent.type() == AppKit.NSSystemDefined and theEvent.subtype() == kEventHotKeyPressedSubtype:
      self.activateIgnoringOtherApps_(True)
      
      print theEvent
      
      #for bind in self.binds:
      #  if bind['key'] == event.detail:
      #    self.event.send(sender=self.__class__, name=bind['name'])
      #    break
      
    super(HotKeyApp, self).sendEvent_(theEvent)

#-------------------------------
class Hotkey(object):
  #===============================
  def __init__(self):
    self.binds = []    
    self.event = Signal()
    self.app = HotKeyApp.alloc().init()
  
  #===============================
  def add_bind(self, name, string):
    keys = re.findall(r'(\w+)', string)
    
    modifiers = 0
    
    # Process the keys
    for modifier in keys[:-1]:
      if modifier == 'control':
        modifiers |= controlKey
      elif modifier == 'alt':
        modifiers |= optionKey
      elif modifier == 'cmd':
        modifiers |= cmdKey
      elif modifier == 'shift':
        modifier |= shiftKey
        
    key = ord(keys[-1]) - 38
        
    self.binds.append({
      'name': name,
      'key': key,
      'modifiers': modifiers
    })
  
  #===============================
  def loop(self):    
    AppHelper.runEventLoop()
    