from os import environ

from django.test import TestCase

from ..settings import (
    get_setting,
    CAST_AS_INT,
    CAST_AS_BOOL
)


class SettingsTests(TestCase):

    def test_cast_as_bool(self):

        self.assertTrue(CAST_AS_BOOL(True))
        self.assertTrue(CAST_AS_BOOL("True"))
        self.assertTrue(CAST_AS_BOOL("true"))
        # special case: 1 == True
        self.assertTrue(CAST_AS_BOOL(1))
        self.assertFalse(CAST_AS_BOOL(False))
        self.assertFalse(CAST_AS_BOOL(None))
        self.assertFalse(CAST_AS_BOOL("1"))

    def test_get_settings(self):

        with self.settings(TEST_SETTING=True):
            self.assertTrue(get_setting('TEST_SETTING', False))
            self.assertTrue(get_setting('TEST_SETTING', True))

        with self.settings(TEST_SETTING="0"):
            self.assertEqual(get_setting('TEST_SETTING', False), "0")

        with self.settings(TEST_SETTING="0"):
            self.assertEqual(
                get_setting('TEST_SETTING', False, cast_func=CAST_AS_INT),
                0
            )

        with self.settings(TEST_SETTING="True"):
            self.assertEqual(
                get_setting('TEST_SETTING', False, cast_func=CAST_AS_BOOL),
                True
            )

        # confirm that env vars trump django.conf
        environ['TEST_SETTING'] = "True"
        with self.settings(TEST_SETTING=False):
            self.assertEqual(
                get_setting('TEST_SETTING', False, cast_func=CAST_AS_BOOL),
                True
            )
