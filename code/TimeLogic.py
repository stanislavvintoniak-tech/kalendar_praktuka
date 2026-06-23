

import datetime as dt
from typing import Union

class DateCalc:
  

    def __init__(self) -> None:
        """A Basic Date Calculator"""

    @staticmethod
    def day_calculator(start_date, end_date) -> int:

        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")

        if end_date < start_date:
            raise ValueError("End date was found to be less than start date")
        else:
            return (end_date - start_date).days

    @staticmethod
    def second_calculator(start_date, end_date) -> float:

        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")

        return (start_date - end_date).total_seconds()

    @staticmethod
    def date_increment(date, increment: int, increment_unit: str) -> dt.date:
        
        if increment_unit == 'week(s)':
            increment *= 7
        elif increment_unit == 'month(s)':
            increment *= 30
        elif increment_unit == 'year(s)':
            increment *= 365

        date = dt.datetime.strptime(date, "%Y-%m-%d")
        date += dt.timedelta(days=increment)
        return date


class TimeConvert:

    def __init__(self, integer: int, unit: str, out_unit: str):

        self.num = integer
        self.in_unit = unit
        self.out_unit = out_unit

        self.second = self._to_sec()

    def _to_sec(self) -> int:

        conversion: dict = {
            'min': 60,
            'hour': 60 * 60,
            'day(s)': 24 * 60 * 60,
            'week(s)': 7 * 24 * 60 * 60,
            'year(s)': 365 * 24 * 60 * 60,
        }
        return self.num * conversion[self.in_unit]

    def _to_min(self) -> float:
        return self.second / 60

    def _to_hour(self) -> float:
        return self._to_min() / 60

    def _to_days(self) -> float:
        return round(self._to_hour() / 24, 3)

    def _to_weeks(self) -> float:
        return round(self._to_days() / 7, 3)

    def _to_year(self) -> float:
        return round(self._to_days() / 365, 3)

    def output(self):
        conversion_func = {
            'sec': self._to_sec,
            'min': self._to_min,
            'hour': self._to_hour,
            'day(s)': self._to_days,
            'week(s)': self._to_weeks,
            'year(s)': self._to_year
        }
        return conversion_func[self.out_unit]()


class TimeCalc:

    def __init__(self) -> None:
        """A basic Time calculator"""

    @staticmethod
    def str_to_seconds(time_string: str) -> int:

        multipliers = [3600, 60, 1]
        return sum([a * b for a, b in zip(multipliers, map(int, time_string.split(':')))])

    def time_gap(self, start_time: str, end_time: str) -> Union[int, ValueError]:

        if dt.time.fromisoformat(start_time) > dt.time.fromisoformat(end_time):
            raise ValueError("Start time can't be bigger than end time")
        else:
            return self.str_to_seconds(end_time) - self.str_to_seconds(start_time)

    @staticmethod
    def time_increment(time: str, increment: int, increment_unit: str) -> str:

        if increment_unit == 'hrs':
            increment *= 3600
        elif increment_unit == 'min':
            increment *= 60

        time: list = time.split(':')
        time = [int(time[i].lstrip('0')) for i in range(3)]
        hours, minutes, seconds = time

        total_seconds = dt.timedelta(
            hours=hours, minutes=minutes, seconds=seconds) + dt.timedelta(seconds=increment)

        return str(total_seconds)
