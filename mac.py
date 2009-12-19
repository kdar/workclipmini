import subprocess
import re
import appscript
import sys
import louie
import time

import AppKit
from PyObjCTools import AppHelper
from Carbon.CarbonEvt import RegisterEventHotKey, GetApplicationEventTarget
from Carbon.Events import cmdKey, controlKey, shiftKey, optionKey

import HotKey

kEventHotKeyPressedSubtype = 6
kEventHotKeyReleasedSubtype = 9

if sys.version_info < (2,6):
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

#def _name(name):
#  return ord(name[0]) << 24 | \
#         ord(name[1]) << 16 | \
#         ord(name[2]) << 8 | \
#         ord(name[3])

#import ctypes
##HIToolbox = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Carbon.framework/Frameworks/HIToolbox.framework/HIToolbox')
#class HKCommand(ctypes.Structure):
#  _fields_ = [
#    ('signature', ctypes.c_uint32),
#    ('id', ctypes.c_uint32)
#  ]
#  
#class ExtractAddress(ctypes.Structure):
#  _fields_ = [
#    ('ob_refcnt', ctypes.c_size_t),
#    ('ob_type', ctypes.c_int32),
#    ('ob_itself', ctypes.c_int32)
#  ]

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
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(text)
    p.stdin.close()
    retcode = p.wait()
  
  #===============================
  def copy_selected_text(self):
    # Sleep so as to give the user time to let go of the keys so we can send
    # the copy text shortcut. Is there an API for copying selected text?
    time.sleep(0.3)
    appscript.app('System Events').keystroke('c', using=appscript.k.command_down)

#-------------------------------
class HotKeyApp(AppKit.NSApplication):
  launched = louie.Signal()
  event = louie.Signal()
  
  #===============================
  def finishLaunching(self):
    louie.send(HotKeyApp.launched)
    super(HotKeyApp, self).finishLaunching()

  #===============================
  def sendEvent_(self, theEvent):
    if theEvent.type() == AppKit.NSSystemDefined and theEvent.subtype() == kEventHotKeyReleasedSubtype:
      #self.activateIgnoringOtherApps_(True)
      
      louie.send(HotKeyApp.event, theEvent=theEvent)
      
      #command = HKCommand()
      #carbon.GetEventParameter(
      #  theEvent,
      #  _name('----'),
      #  _name('hkid'),
      #  ctypes.c_void_p(),
      #  ctypes.sizeof(command),
      #  ctypes.c_void_p(),
      #  
      #  command
      #)
      
      #print theEvent
      #print ctypes.byref(theEvent)
      #
      #i = ctypes.c_int32()
      #carbon.GetEventParameter(
      #  theEvent,
      #  _name('kcod'),
      #  _name('magn'),
      #  ctypes.c_void_p(),
      #  ctypes.sizeof(i),
      #  ctypes.c_void_p(),
      #  ctypes.byref(i)
      #)
    else: 
      super(HotKeyApp, self).sendEvent_(theEvent)

#-------------------------------
class Hotkey(object):
  #===============================
  def __init__(self):
    self.binds = []    
    self.event = louie.Signal()
    self.app = HotKeyApp.alloc().init()
    
    louie.connect(self.on_key, HotKeyApp.event)
    louie.connect(self.on_launched, HotKeyApp.launched)
  
  #===============================
  def add_bind(self, name, string):
    keys = re.findall(r'(\w+)', string)
    
    modifiers = 0
    
    # Process the keys
    for modifier in keys[:-1]:
      if modifier == 'control':
        modifiers |= controlKey
      elif modifier == 'alt':
        #FIXME: Temporary
        #modifiers |= optionKey
        modifiers |= shiftKey
      elif modifier == 'cmd':
        modifiers |= cmdKey
      elif modifier == 'shift':
        modifiers |= shiftKey
     
    self.binds.append({
      'name': name,
      'key': keys[-1],
      'modifiers': modifiers
    })
  
  #===============================
  def on_key(self, theEvent):
    for bind in self.binds:
      if bind['ref_address'] == theEvent.data1():
        louie.send(self.event, sender=self.__class__, name=bind['name'])
        break
  
  #===============================
  def on_launched(self):
    # This list is incomplete. Use AsyncKeys to find the rest.
    mac_map = ['a','s','d','f','h','g','z','x','c','v','','b','q','w','e','r','y','t']
    
    for bind in self.binds:
      key = mac_map.index(bind['key'].lower())
     
      bind['hotkeyref'] = RegisterEventHotKey(key, bind['modifiers'], (0, 0), GetApplicationEventTarget(), 0)
      #Save the address. That's how we figure out what key was hit.
      bind['ref_address'] = HotKey.HotKeyAddress(bind['hotkeyref']) 
  
  #===============================
  def loop(self):    
    AppHelper.runEventLoop()
    