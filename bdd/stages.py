from collections import namedtuple
STAGES = namedtuple('STAGES', 'GIVEN WHEN THEN SHOULD')._make(range(4))
stages_dict = STAGES._asdict()
STAGES_TITLES = dict(zip(stages_dict.values(), 
                        [v.capitalize() for v in stages_dict.keys()]))  