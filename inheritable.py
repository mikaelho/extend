import ui
import inspect, gc, types, sys
from functools import partial

class ExtenderMeta(type):
  '''
  Metaclass changed to accept all other types as instances of the Extender class.
  This enables us to call superclass methods in the Extender inheritance chain.
  '''
  def __instancecheck__(self, other):
    return True


class Extender(object):
  '''
  Base class for extending the functionality of Python classes that cannot be subclassed (for example, most view classes in the ui module of Pythonista).
  Intended to be always subclassed.
  '''
  
  __metaclass__ = ExtenderMeta

  def __new__(extender_subclass, target_instance, *args, **kwargs):
    '''
    Custom constructor returns the extended instance instead of the extender. 
    '''
    extender_instance = super(Extender, extender_subclass).__new__(extender_subclass)
    for key in dir(extender_instance):
      if key.startswith('__'): continue
      value = getattr(extender_instance, key)
      if callable(value) and type(value) is not type:
        setattr(target_instance, key, types.MethodType(value.__func__, target_instance))
      else:
        setattr(target_instance, key, value)
    init_op = getattr(extender_subclass, '__init__', None)
    if callable(init_op):
      init_op(target_instance, *args, **kwargs)
    return target_instance


class PythonistaClass(Extender):

  def __new__(extender_subclass, *args, **kwargs):
    to_extend = extender_subclass._pythonista_class()
    to_extend = super().__new__(extender_subclass, to_extend, *args, **kwargs)
    return to_extend

  def super(self):
    return ExtenderSuper(self)
    

class ExtenderSuper():
  
  def __init__(self, target_self):
    self._target = target_self
  
  def __getattribute__(self, name):
    frame = inspect.currentframe()
    frame = frame.f_back
    if frame.f_code.co_name == 'super':
      frame = frame.f_back
    code = frame.f_code
    f = [obj for  obj in  gc.get_referrers(code) if isinstance(obj, types.FunctionType)][0]
    cls = getattr(inspect.getmodule(f), f.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
    supers = inspect.getmro(cls)
    for cls in supers[1:]:
      if '_pythonista_class' in cls.__dict__:
        cls = getattr(cls, '_pythonista_class')
      attr = getattr(cls, name, None)
      if attr:
        if callable(attr):
          return partial(attr, object.__getattribute__(self, '_target'))
        else:
          return attr
    raise AttributeError(f"'super' object has no attribute '{name}'")
    

# Generate classes for all ui view classes
for key in ui.__dict__:
  value = getattr(ui, key)
  if type(value) == type:
    globals()[key] = type(key, (PythonistaClass,), {'_pythonista_class': value})


if __name__ == '__main__':

  import random
  
  
  class ClickButton(Button):
    def __init__(self, **kwargs):
      self.super().__init__(**kwargs)
      self.action = self.click_action
      
    def click_action(self, sender):
      pass
      
      
  class TintButton(ClickButton):
    def __init__(self, random_tint=False, **kwargs):
      self.super().__init__(**kwargs)
      if random_tint:
        self.set_random_tint()

    def set_random_tint(self):
      self.tint_color = tuple([random.random() for i in range(3)])

    def click_action(self, sender):
      self.set_random_tint()
  
  
  class MarginView(View):
    
    margin = 20
    
    def __init__(self, margin=20):
      self.margin = margin
      
    def size_to_fit(self):
      self.super().size_to_fit()
      self.frame = self.frame.inset(-self.margin, -self.margin)
      

  class MultiButton(TintButton, MarginView):
    pass


  v = ui.View(background_color='grey')
  b = MultiButton(tint_color='red', background_color='white', font=('Arial Rounded MT Bold', 30), title='Test button', margin=50, extra='Test')
  v.present()
  v.add_subview(b)
  b.size_to_fit()
  b.center = v.center
  print(b.extra)