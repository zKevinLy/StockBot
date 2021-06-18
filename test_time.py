from datetime import date, datetime, timedelta
import unittest
import pytime

class TestTime(unittest.TestCase):

    def test_getCurrentDate(self):
        time = pytime.Time()
        returned = time.getCurrentDate()
        expected = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(expected,returned)

    def test_timeMath(self):
        time = pytime.Time()
        today = time.getCurrentDate()
        returned = time.timeMath(today,1,0,0,0)
        expected = (datetime.strptime(today, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(expected,returned)

    def test_timeDiff(self):
        time = pytime.Time()
        today = time.getCurrentDate()
        tomorrow = time.timeMath(today,1,0,0,0)
        returned = time.timeDiff(today,tomorrow)
        expected = timedelta(days=1)
        self.assertEqual(expected,returned)

    def test_busDays(self):
        time = pytime.Time()
        today = time.getCurrentDate()
        oneYear = time.timeMath(today,365,0,0,0)
        returned = time.busDays(today,oneYear)
        expected = 261
        self.assertEqual(expected,returned)

if __name__ == '__main__':
    unittest.main()