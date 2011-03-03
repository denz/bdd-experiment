from traceback import format_exc
from itertools import *
import inspect
import itertools 
import ast
from textwrap import dedent


import decorators
from stages import STAGES

class ScenarioPreconditionsNotMet(Exception):
    pass

def makelist(arg):
    if arg is None:
        return ()
    elif isinstance(arg, (list, tuple)):
        return arg
    else:
        return (arg,)
def process_exception(result, e):
    return result


class ScenarioResult(object):
    def __init__(self, scenario):
        self.skipped = False
        self.error = False
        self.passed = False
        self.traceback = None
        self.subs = [] 

class Scenario(object):
    '''
    scenario is a group of given-when-then-should members of Behaviour 
    '''
    def __init__(self, behaviour, given, when, then, should):
        if not should or not callable(should): 
            raise AttributeError('@should is mandatory for scenario')

        self.behaviour = behaviour
        self.given = given
        self.when = when
        self.then = then
        self.should = should


    def __call__(self, *args, **kwargs):
        result = ScenarioResult(self)
        
        try:
            if self.given:
                given = makelist(self.given(*args, **kwargs))
            else:
                given = args

            try:
                if self.when:
                    result.subs = makelist(self.when(*given))
            except ScenarioPreconditionsNotMet:
                result.skipped = True
                return result       
            if self.then:
                self.then(*given)
            
            result.passed = bool(self.should(*given))        
        
        except Exception, e:            
            result.error = e
            result.traceback = format_exc()            
        for sub in result.subs:
            if not isinstance(sub, Behaviour):
                raise ValueError('@when returned list with wrong items types \
                (must be Behaviour objects). List is %s'%result.subs)
        return result

    def __eq__(self, other):
        return other.behaviour == self.behaviour and\
               other.given == self.given and\
               other.when == self.when and\
               other.then == self.then and\
               other.should == self.should


    def __repr__(self):
        return ('%s'+4*'\n\t%s'+'\n')%(self.behaviour, self.given, self.when, self.then, self.should) 


class Behaviour(object):
    _omit_member_names = ('_omit_member_names', '__init__', '_class_member_names', '_obj_classes', '_unique_names', '_iter_member_names', '_iter_bdd_descriptors', 'scenario_stages', '_stages_dict_to_args', '_iter_scenarios', 'scenarios',)
    def __init__(self, *args):
        self.args = args
    
    def _class_member_names(self, cls):

                    
            passed_bases += base,
        
    def _obj_classes(self):
        '''
        iter base classes starting from Behaviour and finishing current class
        '''


    def _unique_names(self, bases, names):
        removed_names = []
        for base in bases:
            for name in names:
                if name in bases and not name in removed_names:
                    removed_names += name,
                    
        for name in names:
            if not name in removed_names:
                yield name
        
    def _iter_member_names(self):
        '''
        iterate over assign and def member names, including class bases
        preserves order (bases members goes first)
        '''
        all_bases_names = set(itertools.chain(*[dir(base) for base in self.__class__.__mro__]))
        for base in reversed(self.__class__.__mro__):
            if base.__name__ == 'object':
                continue
            
            class_src = '\n'.join(l for l in inspect.getsource(base).
                                  split('\n') if not l.lstrip().startswith('#'))
            classnodes = ast.iter_child_nodes(ast.parse(dedent(class_src)))
            names = []
            for classnode in classnodes:
                for node in ast.iter_child_nodes(classnode):
                    if isinstance(node, ast.FunctionDef):
                        if node.name in Behaviour._omit_member_names:
                            continue

                        names += node.name,
                        if node.name in all_bases_names:
                            all_bases_names.remove(node.name)
        
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if target.id in Behaviour._omit_member_names:
                                continue
                            names += target.id,
                            if target.id in all_bases_names:
                                all_bases_names.remove(target.id)
            
            for name in names:
                if not name in all_bases_names:
                    yield name

    
    
    def _iter_bdd_descriptors(self):
        '''
        iterate over BDDDescriptors preserving member definition order  
        '''
        for mname in self._iter_member_names():
            member = getattr(self, mname, None)
            if isinstance(member, decorators.BDDDescriptor):
                yield member
        
    scenario_stages = {STAGES.GIVEN:None,
                       STAGES.WHEN:None,
                       STAGES.THEN:None,
                               #SHOULD is mandatory
                               }
    
    def _stages_dict_to_args(self, stages_dict):
        for STAGE in STAGES:
            if STAGE in stages_dict:
                yield stages_dict[STAGE]
            elif STAGE in self.scenario_stages:
                yield self.scenario_stages[STAGE]
                
    def _iter_scenarios(self):
        '''
        iterate over scenarios 
        '''
        descriptors = self._iter_bdd_descriptors()
        stage = True

        while stage:
            stages = {}
            stage  = next(descriptors, None)
            while stage and not stage._stage == STAGES.SHOULD:
                if stage._stage in stages:
                    raise AttributeError(
                        '%s of stage %s alredy defined for current \
scenario'%(stage,stage._stage))                
                stages[stage._stage] = stage
                stage  = next(descriptors, None)
            if stage:    
                yield Scenario(*([self,] + list(self._stages_dict_to_args(stages)) +
                                 [stage,]))            
            
                
    @property
    def scenarios(self):
        '''
        get a list of prebuilt scenarios
        '''
        if not hasattr(self, '_scenarios'):
            self._scenarios = list(self._iter_scenarios())
        return self._scenarios