class STAGES_TYPE(object):
    GIVEN = 0
    WHEN = 1
    THEN = 2
    SHOULD = 3

    def __iter__(cls):
        for i in xrange(4):
            yield i
            
STAGES = STAGES_TYPE()