import unittest.mock as mock
import datetime
import inspect

class MockDatetime(object):

    def __init__(self, target, new_now):
        self.new_now = new_now
        self.target = target

    def __enter__(self):
        calling_module = inspect.getmodule(inspect.stack()[1][0])
        target_from_here = calling_module.__name__ + '.' + self.target
        self.patcher = mock.patch(target_from_here)
        mock_dt = self.patcher.start()
        mock_dt.datetime.now.return_value = self.new_now
        mock_dt.datetime.side_effect = lambda *args, **kw: datetime.datetime(*args, **kw)
        return mock_dt

    def __exit__(self, *args, **kwargs):
        self.patcher.stop()
