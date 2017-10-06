# coding: utf-8
import types
import sys
import warnings

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
    Custom constructor returns the extended instance instead of the extender, supporting chaining of extenders around a single target instance, and type checks that expect an instance of the extended class. 
    '''
    extender_instance = super(Extender, extender_subclass).__new__(extender_subclass)
    for key in dir(extender_instance):
      if key.startswith('__'): continue
      if hasattr(target_instance, key):
        warnings.warn('Target ' + str(type(target_instance)) + ' instance already has attribute ' + key)
      value = getattr(extender_instance, key)
      if callable(value):
        setattr(target_instance, key, types.MethodType(value.__func__, target_instance))
      else:
        setattr(target_instance, key, value)
    init_op = getattr(extender_subclass, '__init__', None)
    if callable(init_op):
      #if sys.version_info[0] < 3:
        #init_op.__func__(target_instance, *args, **kwargs)
      #else:
      init_op(target_instance, *args, **kwargs)
    return target_instance

def combine(target_instance, extender_instance):
    for key in dir(extender_instance):
      if key.startswith('__'): continue
      if hasattr(target_instance, key):
        continue
      value = getattr(extender_instance, key)
      if callable(value):
        def func(self, *args, extender_function_name=key, **kwargs):
          return_value = getattr(extender_instance, extender_function_name)(*args, **kwargs)
          return return_value
        setattr(target_instance, key, types.MethodType(func, target_instance))
    
    def get_func(self, key):
      print('get')
      return getattr(extender_instance, key)
                
    setattr(type(target_instance), '__getattr__', types.MethodType(get_func, target_instance))
    """
      else:
        def get_func(self, extender_attribute_name=key):
          print('get')
          return_value = getattr(extender_instance, extender_attribute_name)
          return return_value
        def set_func(self, value, extender_attribute_name=key):
          print('set')
          setattr(extender_instance, extender_attribute_name, value)
        setattr(type(target_instance), key, property(get_func, set_func))
    """

if __name__ == '__main__':

  class Target (object):
    def __init__(self, zero):
      self.zero = zero

  class AddOn(Extender):

    one = 'one'
    nine = 'nine'

    def __init__(self, location):
      self.two = 'two'
      self.three = location

    def four(self):
      return 'four'

  class OtherParent(Extender):

    nine = 'conflicting nine'
    
    def eight(self):
      return 'eight'

  class MoreSpecificAddOn(AddOn, OtherParent):

    def __init__(self, five):
      AddOn.__init__(self, 'three') # Cannot use super
      self.five = five
      self.set_six()

    def set_six(self):
      self.six = 'six'
      
  class AnotherAddOn(Extender):
    
    def __init__(self):
      self.seven = 'seven'

  v = AnotherAddOn(
    MoreSpecificAddOn(
      Target('zero'),
      'five'
    )
  )
  
  # Right type maintained through the chain
  assert type(v) == Target
  
  # Basic constructor parameters not impacted
  assert v.zero == 'zero'
  
  # Superclass properties passed to target
  assert v.one == 'one'
  
  # Extender subclass __init__ is called and has the right `self`
  assert v.two == 'two'
  
  # Can call superclass overloaded methods in the Extender hierarchy (note syntax)
  assert v.three == 'three'
  
  # Superclass methods are passed to target
  assert v.four() == 'four'
  
  # Parameters beyond the target instance to right init
  assert v.five == 'five'
  
  # Extender subclass init can call methods in the same class
  assert v.six == 'six'
  
  # Extenders are chainable
  assert v.seven == 'seven'
  
  # Multiple inheritance causes no problems
  assert v.eight() == 'eight'
  
  # Regular multiple inheritance conflict resolution applies
  assert v.nine == 'nine'
  
  print('All Extender tests passed')
  
  
  class Master(object):
    def __init__(self):
      self.one = 'one'
    
    def two(self):
      return 'two'
    
  class Supplementer(object):
    def __init__(self):
      self.three = 'three'
    
    def four(self):
      return 'four'
      
    def five(self):
      return self.five
      
  m = Master()
  s = Supplementer()
  
  combine(m, s)
  
  # Basics still work
  assert m.one == 'one'
  assert m.two() == 'two'
  
  # Proxied properties work
  print(m.three)
  
  # Proxied methods work
  assert(m.four() == 'four')

  print('All combine tests passed')
