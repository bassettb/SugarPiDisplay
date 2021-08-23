# import unittest.mock
# from mock import patch
# from datetime import datetime
# with patch('sugarpidisplay.datetime') as mock_datetime:
#      mock_datetime.now.return_value = datetime(2010, 10, 8)
#      mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

# def test__datetime():
#     assert sugarpidisplay.datetime.now is None

import datetime
from .testhelpers import MockDatetime
def test__mock_datetime():
    # with MockDatetime('test_testhelpers.datetime', datetime.datetime(2019, 4, 29, 9, 10, 23, 1234)):
    #     assert datetime.datetime.utcnow() == datetime.datetime(2019, 4, 29, 9, 10, 23, 1234)

    with MockDatetime('datetime', datetime.datetime(2016, 3, 23)):
        assert datetime.datetime.utcnow() == datetime.datetime(2016, 3, 23)


from ..utils import seconds_since

def test_get_stale_minutes():
    with MockDatetime('datetime', datetime.datetime(2020, 1, 1, 0 , 0, 5, 0)):
        assert seconds_since(datetime.datetime(2020, 1, 1, 0 , 0, 0, 0, tzinfo=datetime.timezone.utc)) == 5



# from datetime import date
# >>> with patch('mymodule.date') as mock_date:
#         mock_date.today.return_value = date(2010, 10, 8)
#         mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
#
#         assert mymodule.date.today() == date(2010, 10, 8)
#         assert mymodule.date(2009, 6, 8) == date(2009, 6, 8)