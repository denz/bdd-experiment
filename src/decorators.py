from functools import wraps, update_wrapper

from stages import STAGES

class BDDDescriptor(object):
    '''
    base for @given, @when, @then, @should, and other stages of testing
    '''
    def __init__(self, wrapped):
        self.wrapped = wrapped
        if getattr(self, '_behavior_new_seq', False):
            pass
        
    def __get__(self, instance, owner):
        if not instance:
            return self.__class__
        self.instance = instance
        self.owner = owner        
        update_wrapper(self, self.wrapped)
        return self
                
    def __call__(self, *args, **kwargs):
        return self.wrapped.__get__(self.instance, self.owner)(*args, **kwargs)
    
    def __eq__(self, other):
        return self.__class__ == other.__class__ and\
               self.wrapped == other.wrapped
    

class given(BDDDescriptor):
    '''
    returns  *args, passed to all next stages.
    accepts *args provided on __call__ or __init__  of Behaviour 
    (__call__ overrides __init__) 
    '''
    _stage = STAGES.GIVEN


class when(BDDDescriptor):
    '''
    test that all conditions met before actual start of testing.
    can raise ScenarioPreconditionsNotMet to prevent further testing of current bdd scenario
    returns list of subs - Behaviour objects      
    '''
    _stage = STAGES.WHEN


class then(BDDDescriptor):
    ''' do additional actions before actual testing
    '''
    _stage = STAGES.THEN 


class should(BDDDescriptor):
    
    '''
    must return True in case of success
    '''
    _stage = STAGES.SHOULD