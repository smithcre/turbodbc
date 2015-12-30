from unittest import TestCase

from query_fixture import query_fixture

import pydbc
import json
import datetime


class SelectBaseTestCase(object):
    """
    Children are expected to provide the following attributes:
    
    self.dsn
    self.supports_row_count
    self.fixture_file_name
    """

    @classmethod
    def setUpClass(cls):
        with open(cls.fixture_file_name, 'r') as f:
            cls.fixtures = json.load(f)

    def setUp(self):
        self.connection = pydbc.connect(self.dsn)
        self.cursor = self.connection.cursor()

    def tearDown(self):
        self.cursor.close()
        self.connection.close()

    def _test_single_row_result_set(self, query, expected_row):
        self.cursor.execute(query)

        if self.supports_row_count:
            self.assertEqual(self.cursor.rowcount, 1)
        else:
            self.assertEqual(self.cursor.rowcount, -1)

        row = self.cursor.fetchone()
        self.assertItemsEqual(row, expected_row)

        row = self.cursor.fetchone()
        self.assertIsNone(row)

    def test_single_row_NULL_result(self):
        self._test_single_row_result_set("SELECT NULL", [None])

    def test_single_row_integer_result(self):
        self._test_single_row_result_set("SELECT 42", [42])

    def test_single_row_bool_result(self):
        self._test_single_row_result_set("SELECT True", [True])
        self._test_single_row_result_set("SELECT False", [False])

    def test_single_row_string_result(self):
        self._test_single_row_result_set("SELECT 'value'", ["value"])

    def test_single_row_unicode_result(self):
        self._test_single_row_result_set(u"SELECT 'value \u2665'", [u"value \u2665"])

    def test_single_row_double_result(self):
        with query_fixture(self.cursor, self.fixtures, 'SELECT DOUBLE') as query:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            self.assertItemsEqual(row, [3.14])

    def test_single_row_date_result(self):
        self._test_single_row_result_set("SELECT CAST('2015-12-31' AS DATE) AS a",
                                         [datetime.date(2015, 12, 31)])

    def test_single_row_timestamp_result(self):
        with query_fixture(self.cursor, self.fixtures, 'SELECT TIMESTAMP') as query:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            self.assertItemsEqual(row, [datetime.datetime(2015, 12, 31, 1, 2, 3)])

    def test_single_row_large_numeric_result_as_string(self):
        self._test_single_row_result_set("SELECT -1234567890123.123456789", ['-1234567890123.123456789'])

    def test_single_row_multiple_columns(self):
        self._test_single_row_result_set("SELECT 40, 41, 42, 43", [40, 41, 42, 43])

    def test_multiple_rows(self):
        with query_fixture(self.cursor, self.fixtures, 'SELECT MULTIPLE INTEGERS') as query:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            self.assertItemsEqual(row, [42])
            row = self.cursor.fetchone()
            self.assertItemsEqual(row, [43])
            row = self.cursor.fetchone()
            self.assertItemsEqual(row, [44])

            row = self.cursor.fetchone()
            self.assertIsNone(row)


# Actual test cases

class TestSelectExasol(SelectBaseTestCase, TestCase):
    dsn = "Exasol R&D test database"
    supports_row_count = True
    fixture_file_name = 'query_fixtures_exasol.json'


class TestSelectPostgreSQL(SelectBaseTestCase, TestCase):
    dsn = "PostgreSQL R&D test database"
    supports_row_count = False
    fixture_file_name = 'query_fixtures_postgresql.json'


class TestSelectMySQL(SelectBaseTestCase, TestCase):
    dsn = "MySQL R&D test database"
    supports_row_count = True
    fixture_file_name = 'query_fixtures_mysql.json'
