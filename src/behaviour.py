from traceback import format_exc
from itertools import *
import inspect
import itertools 
import ast
from textwrap import dedent


import decorators
from stages import STAGES, STAGES_TITLES

class ScenarioPreconditionsNotMet(Exception):
    pass

def makelist(arg):
    if arg is None:
        return ()
    elif isinstance(arg, (list, tuple)):
        return arg
    else:
        return (arg,)


DEFAULT_SCENARIO_FORMAT = 'text'


def unCamel(x): 
    return reduce(lambda a,b: a + ((b.upper() == b and \
                                    (len(a) and a[-1].upper() != a[-1])) and \
                                    (' ' + b) or b), x, '')


class BehaviourResult(list):
    def check_passed(self, result):
        if not result.passed:
            return result.passed
        else:
            for subres in result.subresults:
                if not self.check_passed(subres):
                    return False
            
            return True 
    
    @property
    def status(self):
        for res in self:
            if res.skipped:
                return None
            if not self.check_passed(res):
                return False
        return True
    
    def format_recursively(self, result, indent=0):
        yield result.format(indent=indent)
        for result in result.subresults:
            for formatted in self.format_recursively(result, indent=indent+1):
                yield formatted
    
    def format(self, type='text'):
        indent = 0
        for res in self:
            for formatted in self.format_recursively(res, indent=indent):
                yield formatted 
 
class ScenarioResult(object):
    def __init__(self, scenario):
        self.scenario = scenario
        self.skipped = False
        self.error = False
        self.passed = False
        self.traceback = None
        self.subs = []
        self.subresults = []
    
    def describe(self, stage, prefix=True):
        if stage.__doc__:
            return stage.__doc__
        else:
            words = []
            if prefix:
                words += '%s:'%STAGES_TITLES[stage._stage],
            #first split by underscore
            predescr = stage.__name__.split('_')
            #then split by camel-case
            for descr in predescr:
                if descr.lower() == descr:
                    words += descr,
                else:
                    words += unCamel(descr),
                    
            return ' '.join(words) 
                     
    @property
    def status(self):
        if not self.skipped:
            return '\n%s'%(self.passed and 'OK' or self.error and 'ERROR' or 'FAIL')
        else:
            return '\n:SKIPPED'
    
    def format_text(self, with_traceback, indent = 0):
        indent = '\t'*indent 
        text = ''
        for stage in [self.scenario.given, 
                           self.scenario.when, 
                           self.scenario.then, 
                           self.scenario.should]:
            if not stage:
                continue
            
            if not text:                
                if stage._stage == STAGES.GIVEN:
                    text += '%s%s'%(indent, self.describe(stage))
                else: 
                    text += '%sGiven:'%indent + ','.join([arg for arg in inspect.getargspec(stage.wrapped).args if not arg == 'self'])
                    text += '\n\t%s%s'%(indent, self.describe(stage))
            else:
                text += '\n\t%s%s'%(indent, self.describe(stage))
        text += self.status
        return text
            
    def format(self, 
               type=DEFAULT_SCENARIO_FORMAT, 
               with_traceback=False,
               indent=0):
        return getattr(self, 'format_%s'%type)(with_traceback, indent=indent)

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
    _omit_member_names = ('__call__',
                          '_omit_member_names', 
                          '__init__', 
                          '_class_member_names', 
                          '_obj_classes', 
                          '_unique_names', 
                          '_iter_member_names', 
                          '_iter_bdd_descriptors', 
                          'scenario_stages', 
                          '_stages_dict_to_args', 
                          '_iter_scenarios', 
                          'scenarios',
                          '__call_recursively__')

    def __init__(self, *args):
        self.args = args
    
    def _class_member_names(self, cls):       
            passed_bases += base,

        
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
    
    def __call_recursively__(self, subs):
        for sub in subs:
            for result in sub():
                result.subresults += list(self.__call_recursively__(result.subs))
            yield result
        
    def __call__(self, *args):
        if not args:
            args = self.args
        results = BehaviourResult()
        for scenario in self.scenarios:
            result = scenario(*args)
            result.subresults = list(self.__call_recursively__(result.subs))
            results += result,
        return results
            