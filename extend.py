# coding: utf-8
	
# Base class for extending the functionality of Python
# classes that cannot be subclassed (for example,
# most view classes in the ui module of Pythonista).
# 
# Constructor returns the extended instance instead of
# the extender, supporting chaining of extenders 
# around a single target instance


import types

class Extender(object):
	def __new__(extender_subclass, target_instance, *args, **kwargs):
		extender_instance = super(Extender, extender_subclass).__new__(extender_subclass)
		for key in dir(extender_instance):
			if key.startswith('__'): continue
			value = getattr(extender_instance, key)
			if callable(value):
				setattr(target_instance, key, types.MethodType(value.__func__, target_instance))
			else:
				setattr(target_instance, key, value)
		if isinstance(extender_subclass.__init__, types.MethodType):
			extender_subclass.__init__.__func__(target_instance, *args, **kwargs)
		return target_instance
		
# Extend the instance given as the first argument
# with the methods and properties of the instances
# given as the second and subsequent arguments

'''
def extend(target, *args):
	for (source_class, *source_args, **source_kwargs) in args:
		for key in dir(source):
			if key.startswith('__'): continue
			value = getattr(source, key)
			if callable(value):
				setattr(target, key, types.MethodType(value.__func__, target))
			else:
				setattr(target, key, value)
	return target
'''
		
if __name__ == '__main__':
		
	class Concrete(Extender):
		
		one = 'one'
		
		def __init__(self, location):
			self.two = 'two'
			self.three = location
			
		def four(self):
			return 'four'
			
	class MoreSpecific(Concrete):
		
		def __init__(self, five):
			Concrete.__init__.__func__(self, 'three')
			self.five = 'five'
			self.set_six()
			
		def set_six(self):
			self.six = 'six'
			
	class Target (object):
		def __init__(self, zero):
			self.zero = zero
		
	v = MoreSpecific(
		Target('zero'),
		'five'
	)
	print v
	print (v.zero, v.one, v.two, v.three, v.four(), v.five, v.six)
	
	# zero - target basic parameter passing not broken
	# one - superclass properties passed to target
	# two - right 'self' in init
	# three - can call overloaded method (note syntax)
	# four - superclass methods are passed to target
	# five - additional parameters passed to right init
	# six - can call methods on 'self' in init
		