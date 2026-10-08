import copy
import unittest
from engine import DurationModel, seating_time, recommend, validate_options
from server import DEFAULT, ROOT


class FixedModel:
    def estimate(self, meal, party, elapsed=0, q=.5):
        return {"minutes": max(1, 20-elapsed), "support": 100, "fallback": False}


def venue(tables, queue=None):
    return {"id":"test", "name":"Test", "meal":"rice", "cleanup":2,
            "outbound_m":400, "return_m":400,"tables":tables,"queue":queue or []}


def table(capacity=2, party=0, elapsed=0):
    return {"id":"T", "capacity":capacity, "party":party,"elapsed":elapsed}


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.model = FixedModel()

    def test_free_table_has_zero_wait_after_travel(self):
        self.assertEqual(seating_time(venue([table()]),2,7,self.model,.5),7)

    def test_subtract_travel_from_remaining_wait(self):
        # 20 - 12 remaining + 2 cleanup = 10; arrive at 7 -> wait 3.
        self.assertEqual(seating_time(venue([table(party=2,elapsed=12)]),2,7,self.model,.5),10)

    def test_queue_uses_multiple_table_turnovers(self):
        self.assertEqual(seating_time(venue([table()], [2,2]),2,5,self.model,.5),44)

    def test_fifo_head_blocks_later_small_group(self):
        # Large group seats at t=22; user cannot bypass it at t=5.
        r=venue([table(),table(4,4,0)],[4])
        self.assertEqual(seating_time(r,2,5,self.model,.5),22)

    def test_best_fit_does_not_waste_large_table(self):
        r=venue([table(4),table(2)],[2])
        self.assertEqual(seating_time(r,4,5,self.model,.5),5)

    def test_party_larger_than_all_tables(self):
        self.assertIsNone(seating_time(venue([table()]),4,5,self.model,.5))


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.model=DurationModel(ROOT/'data'/'synthetic_meals.csv')

    def test_long_seated_party_does_not_have_negative_time(self):
        value=self.model.estimate('rice',2,180)
        self.assertTrue(value['fallback'])
        self.assertGreater(value['minutes'],0)

    def test_quantiles_are_ordered(self):
        for meal in ('rice','noodles','cafe'):
            for party in range(1,7):
                self.assertGreaterEqual(self.model.estimate(meal,party,q=.8)['minutes'],self.model.estimate(meal,party,q=.5)['minutes'])

    def test_recommendation_time_accounting_and_no_mutation(self):
        snapshot=copy.deepcopy(DEFAULT)
        options=validate_options(dict(party=2,buffer=5,now_min=720,class_min=780,out_mode='walk',back_mode='bike'))
        for r in snapshot:
            result=recommend(r,options,self.model)
            for s in result['scenarios'].values():
                self.assertAlmostEqual(s['total'],s['outbound']+s['wait']+s['dining']+s['inbound'])
                self.assertAlmostEqual(s['margin'],55-s['total'])
        self.assertEqual(snapshot,DEFAULT)

    def test_same_day_deadline_and_integer_validation(self):
        valid=dict(party=2,buffer=5,now_min=720,class_min=780,out_mode='walk',back_mode='walk')
        for bad in ({'class_min':700},{'party':True},{'party':7},{'buffer':-1},{'out_mode':'car'}):
            with self.assertRaises(ValueError): validate_options({**valid,**bad})


if __name__=='__main__': unittest.main()
