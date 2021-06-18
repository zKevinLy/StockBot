from datetime import date, datetime, timedelta
import numpy as np

class Time:
    # gets today's date
    def getCurrentDate(self):
        datetimeObj = datetime.now()
        ret = datetimeObj.strftime("%Y-%m-%d %H:%M:%S")
        return ret

    # gets dates math (addition and subtraction)
    def timeMath(self,a, days, hours = 0, minutes = 0, seconds = 0):
        adjusted = datetime.strptime(a, "%Y-%m-%d %H:%M:%S") + timedelta(days=days, hours = hours, minutes = minutes, seconds = seconds) 
        return adjusted.strftime("%Y-%m-%d %H:%M:%S")

    # gets time difference between 2 dates
    def timeDiff(self, d1, d2):
        d1 = datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
        d2 = datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
        return (d2 - d1)

    # gets number of business days in a year
    def busDays(self,d1,d2):
        d1, _ = d1.split(" ")
        y1,m1,d1 = d1.split("-")

        d2, _ = d2.split(" ")
        y2,m2,d2 = d2.split("-")

        start = date( int(y1), int(m1), int(d1))
        end = date( int(y2), int(m2), int(d2))

        days = np.busday_count( start, end )
        return days


if __name__ == '__main__':
    pass
    # t = Time()
    # today = t.getCurrentDate()
    # yesterday = t.timeMath(today, 1, 0, 0 ,0)
    # print(yesterday)
    # dif = t.timeDiff(today,yesterday)
    # print(dif)