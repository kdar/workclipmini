#Copy from the clipboard:
import os
import Xlib
import Xlib.X
import Xlib.XK
import Xlib.display
import Xlib.keysymdef.xkb
import time
import re

from dispatch.dispatcher import Signal

#-------------------------------
class Clipboard(object):
  #===============================
  @property
  def text(self):
    fp = os.popen('xsel')
    string = fp.read()
    fp.close()
    return string
  
  #===============================
  @text.setter
  def text(self, text): 
    fp = os.popen('xsel', 'w')
    fp.write(text)
    fp.close()

  #===============================
  def copy_selected_text(self):
    pass

#-------------------------------
class Hotkey(object):
  #===============================
  def __init__(self):
    self.display = Xlib.display.Display()
    self.root = self.display.screen().root    
    
    #self.binds = [{
    #  'name': 'CLIPBOARD',
    #  'key': self.display.keysym_to_keycode(Xlib.XK.XK_C),
    #  'modifiers': Xlib.X.ControlMask | Xlib.X.Mod1Mask
    #}, {
    #  'name': 'URL',
    #  'key': self.display.keysym_to_keycode(Xlib.XK.XK_B),
    #  'modifiers': Xlib.X.ControlMask | Xlib.X.Mod1Mask
    #}]
    
    self.binds = []
      
    self.scroll_lock_mask = self.caps_lock_mask = self.num_lock_mask = 0
    self._get_apply_masks()
    
    self.shutdown = False
    
    self.event = Signal()
    
  #===============================
  def _get_apply_masks(self):
    KC_Scroll_Lock, KC_Caps_Lock, KC_Num_Lock = [self.display.keysym_to_keycode(keysym) for keysym in \
      [Xlib.XK.XK_Scroll_Lock, Xlib.XK.XK_Caps_Lock, Xlib.XK.XK_Num_Lock]]    
    
    for count,mask in enumerate(self.display.get_modifier_mapping()):      
      if mask[0] == KC_Scroll_Lock:
        self.scrolllock_mask = 1 << count
      elif mask[0] == KC_Caps_Lock:
        self.capslock_mask = 1 << count
      elif mask[0] == KC_Num_Lock:
        self.numlock_mask = 1 << count
    
    self.apply_masks = (0, self.scroll_lock_mask, self.caps_lock_mask, self.num_lock_mask, \
      self.caps_lock_mask | self.num_lock_mask, self.scroll_lock_mask | self.caps_lock_mask, \
      self.scroll_lock_mask | self.caps_lock_mask | self.num_lock_mask)
    
  #===============================
  def add_bind(self, name, string):
    keys = re.findall(r'(\w+)', string)
    
    modifiers = 0
    
    # Process the keys
    for modifier in keys[:-1]:
      if modifier == 'alt':
        modifier = 'mod1'
        
      mask_name = '{0}{1}Mask'.format(modifier[0].upper(), modifier[1:])
      mask = getattr(Xlib.X, mask_name)
      modifiers |= mask
      
    key = getattr(Xlib.XK, 'XK_{0}'.format(keys[-1]))
    key = self.display.keysym_to_keycode(key)
        
    self.binds.append({
      'name': name,
      'key': key,
      'modifiers': modifiers
    })
  
  #===============================
  def loop(self):
    owner = 1
    keyboard = pointer = Xlib.X.GrabModeAsync
    
    self.root.change_attributes(event_mask=Xlib.X.KeyPressMask)
    
    for bind in self.binds:
      for mask in self.apply_masks:
        self.root.grab_key(bind['key'], bind['modifiers'] | mask, owner, pointer, keyboard)		
    
    while not self.shutdown:
      while self.display.pending_events():
        event = self.display.next_event()
        if event.type == Xlib.X.KeyPress:
          #print("key pressed: %d" % event.detail)
          for bind in self.binds:
            if bind['key'] == event.detail:
              self.event.send(sender=self.__class__, name=bind['name'])
              break
    
      time.sleep(0.1)
   
    self.display.ungrab_keyboard(Xlib.X.CurrentTime)
    self.display.flush()
    self.display.screen().root.ungrab_key(Xlib.X.AnyKey, Xlib.X.AnyModifier)
  