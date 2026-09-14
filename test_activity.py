import unittest
import activity
import argparse
import json
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError
SAMPLE_EVENT = [
    {
        "id": "22249084947",
        "type": "WatchEvent",
        "actor": {
            "id": 583231,
            "login": "octocat",
        },
        "repo": {
            "id": 1296269,
            "name": "octocat/Hello-World",
            "url": "https://api.github.com/repos/octocat/Hello-World"
        }
    }]

class TestActivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # convert list of dicts into a json string and encode. This is the 
        # response we expect
        cls.events_bytes = json.dumps(SAMPLE_EVENT).encode('utf-8')

    # @patch("activity.urlopen")
    # @patch("activity.display_events")
    # def test_get_github_activity_success(self, mocked_display, mocked_urlopen):
    #     # a mock is a blank slate and you can methods and attributes to it
    #     # with urlopen returns a context manager
    #     manager_mock = MagicMock()
    #     #the enter function yields the response object
    #     response_mock = manager_mock.__enter__.return_value = MagicMock()
    #     response_mock.read.return_value = self.events_bytes
    #     mocked_urlopen.return_value = manager_mock
    #     args = argparse.Namespace(username="octocat")
    #     activity.get_github_activity(args)
    #     mocked_display.assert_called_once_with(SAMPLE_EVENT)


    # @patch("activity.urlopen")
    # @patch("activity.print")
    # def test_get_github_activity_404(self, mock_print, mocked_urlopen):
    #     # no manager or response mock here urelopen fails
    #     mocked_urlopen.side_effect = HTTPError(
    #         url="https://api.github.com/users/notarealusername/events",
    #         code=404,
    #         msg="Not Found",
    #         hdrs=None,
    #         fp=None,
    #     )
    #     args = argparse.Namespace(username="notarealusername")
    #     activity.get_github_activity(args)
    #     mock_print.assert_called_once_with(
    #         "Github username notarealusername was not found"
    #     )

    # NEW TESTS SINCE WE ADDED CACHING
    @patch("activity.r")
    @patch("activity.urlopen")
    def test_get_user_data_cache_miss(self, mocked_urlopen, mocked_redis):
        mocked_redis.get.return_value = None
        # we need to mock url open here. we do not want the test to make the direct call to github.
        # github can rate-limit us, the user activity can change, network may fail making our test nondeterministic and flaky
        manager_mock = MagicMock()
        response_mock = MagicMock()
        manager_mock.__enter__.return_value = response_mock
        response_mock.read.return_value = self.events_bytes
        mocked_urlopen.return_value = manager_mock

        result = activity.get_user_data("octat")
        self.assertEqual(result, self.events_bytes)

    @patch("activity.r")
    @patch("activity.urlopen")
    def test_get_user_data_cache_hit(self, mocked_urlopen, mocked_redis):
        mocked_redis.get.return_value = self.events_bytes

        result = activity.get_user_data("Octocat")

        self.assertEqual(result, self.events_bytes)
        mocked_redis.get.assert_called_once_with("user_activity:octocat")
        mocked_urlopen.assert_not_called()

    @patch("activity.r")
    @patch("activity.urlopen")
    @patch("activity.print")
    def test_get_user_data_404(self, mocked_print, mocked_urlopen, mocked_redis):
        mocked_redis.get.return_value = None

        mocked_urlopen.side_effect = HTTPError(
            url="https://api.github.com/users/notarealusername/events",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None,
        )

        result = activity.get_user_data("notarealusername")

        self.assertIsNone(result)
        mocked_print.assert_any_call(
            "Github username notarealusername was not found"
        )

    @patch("activity.get_user_data")
    @patch("activity.display_events")
    def test_get_github_activity_success(self, mocked_display, mocked_user_get_data):
        mocked_user_get_data.return_value = self.events_bytes
        args = argparse.Namespace(username="octocat")
        activity.get_github_activity(args)
        mocked_display.assert_called_once_with(SAMPLE_EVENT)

    def test_format_event_success(self):
        self.assertEqual(activity.format_event(SAMPLE_EVENT[0]),"octocat starred octocat/Hello-World" )

    @patch("activity.print")
    def test_display_events_success(self, mocked_print):
        activity.display_events(SAMPLE_EVENT)
        mocked_print.assert_called_once_with("octocat starred octocat/Hello-World")

if __name__ == "__main__":
    unittest.main(verbosity=2)