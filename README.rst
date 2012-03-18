Decorators based BDD testing
============================

Differs from mainstream BDD by extended stages set - given-when-then-should

@when 
 - may raise ScenarioPreconditionsNotMet to skip tests
 - may return list of Behaviour objects to start subtests
 
 Main purpose is to experiment with testing of tree structures (DOM for example)
 with tree of tests

An example::

    from bdd import Behaviour
    class TestSub(Behaviour):
        @given
        def number(self, n):
            return n
        @should
        def be_equal_to_5(self, n):
            return n==5
    
    class TestOfTest(Behaviour):
        @given
        def some_string(self, a):
            return a
        @when
        def string_is_testArg(self, a):
            assert a == 'testarg'

        @should
        def len_string_equal_to_7(self, a):
            return len(a) == 7

        @when
        def all_is_good(self, a):
            return TestSub(5), TestSub(6)    
        @should
        def be_equal_ToTestarg(self, a):
            return a == 'testarg'            
        
        @should
        def len_string_equal_to_7a(self, a):
            return len(a) == 7


====
TODO
====

1. Integrate with `unittest.TestCase` test run
2. Integrate with `TestCase` result formatter
3. Enable `TestCase` subclassing with `Behaviour`.

 Smth like::

    from bdd import TestCaseBehaviour
    from django.test import LiveServerTestCase
    class LivePageTestCase(TestCaseBehaviour(LiveServerTestCase)):
        pass