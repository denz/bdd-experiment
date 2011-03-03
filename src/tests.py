import unittest

from decorators import given, when, then, should, BDDDescriptor
from behaviour import Behaviour, Scenario, ScenarioPreconditionsNotMet

class TestBDDDescriptor(unittest.TestCase):
    def test_descriptor_call_should_do_actual_func_call(self):
        '''
        BDDDescriptor __call__ should do actual func call
        '''
        class Spec(object):
            @BDDDescriptor
            def testfn(self, arg, k=None):
                assert(arg == 1)
                assert(k == True)
                return True
        tt = Spec()
        self.assert_(tt.testfn(1, True))
    
    def test_descriptor_doc_should_be_preserved(self):
        '''
        BDDDescriptor  __doc__ should be preserved
        '''
        class Spec(object):
            @BDDDescriptor
            def testfn(self, arg, k=None):
                '''testdoc'''
                assert(arg == 1)
                assert(k == True)
                return True
            @BDDDescriptor
            def testfn1(self, arg, k=None):
                assert(arg == 1)
                assert(k == True)
                return True

        tt = Spec()
        self.assert_(tt.testfn.__doc__ == 'testdoc')        
        self.assert_(not tt.testfn1.__doc__)        
        

class TestBehaviorScenarios(unittest.TestCase):
    def test_behaviour_iter_memebers(self):
        '''
        Behaviour._iter_member_names() should return defs and assigns in correct order
        '''
        class TestB1(Behaviour):
            def a0(self):
                pass
            def b0(self):
                pass

            class TTT():
                pass 
            
            @given
            def a(self):
                pass
            
            def e(self):
                pass
            
            @when
            def b(self):
                pass
            
            h = 2
            class cc():
                pass
            
            @then
            def c(self):
                pass
            
            @should
            def d(self):
                pass

            for i in range(5):
                locals()['v%s'%i] = i
            @should
            def e(self):
                pass
            
        t = TestB1()
        print list(t._iter_member_names())
        self.assert_(list(t._iter_member_names()) == ['a0', 'b0', 'a', 'e', 'b', 'h', 'c', 'd', 'e'])
    

    def test_iter_descriptors(self):
        '''
        Behaviour._iter_bdd_descriptors should return only BDDDescriptor inherited objects
        '''
        class CustomShould(BDDDescriptor):
            a = 22
            pass
        class TestB2(Behaviour):
            def a0(self):
                pass
            def b0(self):
                pass

            class TTT():
                pass 
            
            @given
            def a(self):
                pass
            

            @when
            def b(self):
                pass
            
            h = 2
            class cc():
                pass
            
            @then
            def c(self):
                pass
            
            c22 = then(lambda self:None)
            @should
            def d(self):
                pass

            for i in range(5):
                locals()['v%s'%i] = i
            @CustomShould
            def e(self):
                pass
            
        t = TestB2()
        self.assert_(list(t._iter_bdd_descriptors()) == [t.a, t.b, t.c, t.c22, t.d, t.e])


    def test_behaviour_simple_iter_scenarios(self):
        '''
        Behaviour._iter_scenarios() should return Scenarios iterator
        '''
        class TestB3(Behaviour):
            @given
            def a(self):
                pass
            @when
            def b(self):
                pass
            @then
            def c(self):
                pass            
            @should
            def d(self):
                pass
 
        t = TestB3()
        self.assert_(list(t._iter_scenarios()) == [Scenario(t, t.a, t.b, t.c, t.d),])        
        
    
    def test_behaviour_iter_scenarios_with_omtted_stages(self):
        '''
         All stages, except 'should' can be omitted in scenario
        '''
        class TestB4(Behaviour):
            @given
            def a0(self):
                pass
            @when
            def b0(self):
                pass
            @then
            def c0(self):
                pass            
            @should
            def d0(self):
                pass
            
            @when
            def b1(self):
                pass
            @then
            def c1(self):
                pass            
            @should
            def d1(self):
                pass

            @then
            def c2(self):
                pass            
            @should
            def d2(self):
                pass

            @should
            def d3(self):
                pass
            
            @given
            def a4(self):
                pass
            @should
            def d4(self):
                pass


            @given
            def a5(self):
                pass
            @when
            def b5(self):
                pass
            @should
            def d5(self):
                pass

            @when
            def b6(self):
                pass            
            @should
            def d6(self):
                pass

            @given
            def a7(self):
                pass
            @then
            def c7(self):
                pass
            @should
            def d7(self):
                pass
            
            @should
            def d8(self):
                pass
            
            @should
            def d9(self):
                pass    
            
        t = TestB4()
        scenarios = list(t._iter_scenarios())
        self.assert_(scenarios[0] == Scenario(t, t.a0, t.b0, t.c0, t.d0))
        self.assert_(scenarios[1] == Scenario(t, None, t.b1, t.c1, t.d1))
        self.assert_(scenarios[2] == Scenario(t, None, None, t.c2, t.d2))
        self.assert_(scenarios[3] == Scenario(t, None, None, None, t.d3))
        self.assert_(scenarios[4] == Scenario(t, t.a4, None, None, t.d4))
        self.assert_(scenarios[5] == Scenario(t, t.a5, t.b5, None, t.d5))        
        self.assert_(scenarios[6] == Scenario(t, None, t.b6, None, t.d6))
        self.assert_(scenarios[7] == Scenario(t, t.a7, None, t.c7, t.d7))
        self.assert_(scenarios[8] == Scenario(t, None, None, None, t.d8))                
        self.assert_(scenarios[9] == Scenario(t, None, None, None, t.d9))


    def test_inconsistent_comment(self):
        '''
        Inconsistent comments in class definition should not raise IndentationError
        '''
        class TestB5(Behaviour):
   #
            @given
     #
            def a(self):
                pass
#
            @when
            def b(self):
                pass
            #
            @then#ddd
            def c(self):#asdas
                pass    #        
            @should
            def d(self):
                pass
            #    sometext
        t = TestB5()
        list(t._iter_scenarios())
        

    def test_multiple_methods_for_same_stage(self):
        '''
        Multiple methods with same stage in one scenario should raise AttributeError
        '''
        class TestB6(Behaviour):
            @given
            def a(self):
                pass
            @when
            def b(self):
                pass
            @when
            def c(self):
                pass            
            @should
            def d(self):
                pass
        t = TestB6()
        self.assertRaises(AttributeError, lambda:list(t._iter_scenarios()))
        
    def test_behavior_scenarios_inheritance(self):
        '''
        Behaviour scenarios inherited from parent
        '''
        
        class TestBBase(Behaviour):
            @given
            def a(self):
                return 1
            @should
            def d(self, v):
                return v == 1
        
        class TestBChild(TestBBase):
            @given
            def a1(self):
                return 2
            @should
            def d1(self, v):
                return v == 2
        b = TestBChild()
        import inspect
        print inspect.getsource(TestBChild)
        print list(b._iter_member_names())
        self.assert_(len(b.scenarios) == 2)
            
class TestScenario(unittest.TestCase):
    def test_should_started_with_init_args(self):
        '''
        Scenario __init__ args passed to single should 
        '''
        
        class TestB7(Behaviour):
            @should
            def d(self, a):
                return a == 'testarg'
        self.assert_(TestB7().scenarios[0]('testarg').passed)
    
    def test_should_returns_error(self):
        '''
        result contains error on @should exception
        '''
        class TestB7_5(Behaviour):
            @should
            def d(self, a):
                assert a == 'testarg1'
                return a == 'testarg1'
        result = TestB7_5().scenarios[0]('testarg')
        self.assert_(result.passed == False and type(result.
                                                     error) == AssertionError)
                     

    def test_then_started_with_init_args(self):
        '''
        Scenario __init__ args passed to then-should 
        '''
        class TestB8(Behaviour):
            @then
            def c(self, a):
                assert(a == 'testarg')
            @should
            def d(self, a):
                return a == 'testarg'
        self.assert_(TestB8().scenarios[0]('testarg').passed)
    
    def test_then_returns_error(self):
        '''
        result contains error on @then exception
        '''
        class TestB8_5(Behaviour):
            @then
            def c(self, a):
                assert a == 'testarg1'

            @should
            def d(self, a):
                return a == 'testarg'
        result = TestB8_5().scenarios[0]('testarg')
        self.assert_(result.passed == False and type(result.
                                                     error) == AssertionError)
    
    def test_given_started_with_init_args(self):
        '''
        Scenario __init__ args passed to given-should 
        '''
        class TestB9(Behaviour):
            @given
            def c(self, a):
                return a
            @should
            def d(self, a):
                return a == 'testarg'
        result = TestB9().scenarios[0]('testarg')
        self.assert_(result.passed)

    def test_given_returns_error(self):
        '''
        result contains error on @given exception
        '''
        class TestB9_5(Behaviour):
            @given
            def c(self, a):
                assert a == 'testarg1'
                return a

            @should
            def d(self, a):
                return a == 'testarg'
        result = TestB9_5().scenarios[0]('testarg')
        self.assert_(result.passed == False and type(result.
                                                     error) == AssertionError)


    def test_when_started_with_init_args(self):
        '''
        Scenario __init__ args passed to when-should
        '''
        class TestB10(Behaviour):
            @when
            def c(self, a):
                assert a == 'testarg'

            @should
            def d(self, a):
                return a == 'testarg'
        result = TestB10().scenarios[0]('testarg')
        self.assert_(result.passed)

    def test_when_returns_error(self):
        '''
        result contains error on @when exception
        '''
        class TestB10_5(Behaviour):
            @when
            def c(self, a):
                assert a == 'testarg1'

            @should
            def d(self, a):
                return a == 'testarg'
        result = TestB10_5().scenarios[0]('testarg')
        self.assert_(result.passed == False and type(result.
                                                     error) == AssertionError)
    def test_when_raises_conditions_not_met(self):
        '''
        Scenario skipped when ScenarioPreconditionsNotMet raised in @when
        '''
        rr = 1
        class TestB10_6(Behaviour):
            @when
            def c(self, a):
                assert a == 'testarg'
                raise ScenarioPreconditionsNotMet('test')

            @should
            def d(self, a):
                rr = 2
                return a == 'testarg'
        result = TestB10_6().scenarios[0]('testarg')
        self.assert_(result.passed == False and result.skipped == True)
        self.assert_(rr == 1)
    
    def test_when_returns_list_of_behaviours(self):
        '''
        Scenario @when list of behaviurs stored in result.subs list
        '''        
        class TestB11(Behaviour):
            @when
            def c(self, a, subs):
                assert a == 'testarg'
                return subs

            @should
            def d(self, a, subs):
                return a == 'testarg'
        subs = [TestB11(2), TestB11(3), TestB11(4)]
        result = TestB11().scenarios[0]('testarg', subs)
        self.assert_(result.passed)
        self.assert_(result.subs == subs)        
    
    def test_when_returns_incorrect_list_raises(self):
        '''
        Scenario raises error when non Behaviours list returned from @when
        '''
        class TestB12(Behaviour):
            @when
            def c(self, a):
                assert a == 'testarg'
                return [1,2,3]

            @should
            def d(self, a):

                return a == 'testarg' 
        self.assertRaises(ValueError, lambda:TestB12().scenarios[0]('testarg'))

    