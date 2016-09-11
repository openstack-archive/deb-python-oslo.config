# Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import re
import unittest

from oslo_config import types


class ConfigTypeTests(unittest.TestCase):
    def test_none_concrete_class(self):
        class MyString(types.ConfigType):
            def __init__(self, type_name='mystring value'):
                super(MyString, self).__init__(type_name=type_name)

        self.assertRaises(TypeError, MyString)

    def test_concrete_class(self):
        class MyString(types.ConfigType):
            def __init__(self, type_name='mystring value'):
                super(MyString, self).__init__(type_name=type_name)

            def _formatter(self, value):
                return value

        MyString()


class TypeTestHelper(object):
    def setUp(self):
        super(TypeTestHelper, self).setUp()
        self.type_instance = self.type

    def assertConvertedValue(self, s, expected):
        self.assertEqual(expected, self.type_instance(s))

    def assertInvalid(self, value):
        self.assertRaises(ValueError, self.type_instance, value)


class StringTypeTests(TypeTestHelper, unittest.TestCase):
    type = types.String()

    def test_empty_string_passes(self):
        self.assertConvertedValue('', '')

    def test_should_return_same_string_if_valid(self):
        self.assertConvertedValue('foo bar', 'foo bar')

    def test_listed_value(self):
        self.type_instance = types.String(choices=['foo', 'bar'])
        self.assertConvertedValue('foo', 'foo')

    def test_unlisted_value(self):
        self.type_instance = types.String(choices=['foo', 'bar'])
        self.assertInvalid('baz')

    def test_with_no_values_returns_error(self):
        self.type_instance = types.String(choices=[])
        self.assertInvalid('foo')

    def test_string_with_non_closed_quote_is_invalid(self):
        self.type_instance = types.String(quotes=True)
        self.assertInvalid('"foo bar')
        self.assertInvalid("'bar baz")

    def test_quotes_are_stripped(self):
        self.type_instance = types.String(quotes=True)
        self.assertConvertedValue('"foo bar"', 'foo bar')

    def test_trailing_quote_is_ok(self):
        self.type_instance = types.String(quotes=True)
        self.assertConvertedValue('foo bar"', 'foo bar"')

    def test_repr(self):
        t = types.String()
        self.assertEqual('String', repr(t))

    def test_repr_with_choices(self):
        t = types.String(choices=['foo', 'bar'])
        self.assertEqual('String(choices=[\'foo\', \'bar\'])', repr(t))

    def test_equal(self):
        self.assertTrue(types.String() == types.String())

    def test_equal_with_same_choices(self):
        t1 = types.String(choices=['foo', 'bar'])
        t2 = types.String(choices=['foo', 'bar'])
        t3 = types.String(choices=('foo', 'bar'))
        t4 = types.String(choices=['bar', 'foo'])
        self.assertTrue(t1 == t2)
        self.assertTrue(t1 == t3)
        self.assertTrue(t1 == t4)

    def test_not_equal_with_different_choices(self):
        t1 = types.String(choices=['foo', 'bar'])
        t2 = types.String(choices=['foo', 'baz'])
        self.assertFalse(t1 == t2)

    def test_equal_with_equal_quote_falgs(self):
        t1 = types.String(quotes=True)
        t2 = types.String(quotes=True)
        self.assertTrue(t1 == t2)

    def test_not_equal_with_different_quote_falgs(self):
        t1 = types.String(quotes=False)
        t2 = types.String(quotes=True)
        self.assertFalse(t1 == t2)

    def test_not_equal_to_other_class(self):
        self.assertFalse(types.String() == types.Integer())

    def test_regex_matches(self):
        self.type_instance = types.String(regex=re.compile("^[A-Z]"))
        self.assertConvertedValue("Foo", "Foo")

    def test_regex_matches_uncompiled(self):
        self.type_instance = types.String(regex="^[A-Z]")
        self.assertConvertedValue("Foo", "Foo")

    def test_regex_fails(self):
        self.type_instance = types.String(regex=re.compile("^[A-Z]"))
        self.assertInvalid("foo")

    def test_regex_and_choices_raises(self):
        self.assertRaises(ValueError,
                          types.String,
                          regex=re.compile("^[A-Z]"),
                          choices=["Foo", "Bar", "baz"])

    def test_equal_with_same_regex(self):
        t1 = types.String(regex=re.compile("^[A-Z]"))
        t2 = types.String(regex=re.compile("^[A-Z]"))
        self.assertTrue(t1 == t2)

    def test_not_equal_with_different_regex(self):
        t1 = types.String(regex=re.compile("^[A-Z]"))
        t2 = types.String(regex=re.compile("^[a-z]"))
        self.assertFalse(t1 == t2)

    def test_ignore_case(self):
        self.type_instance = types.String(choices=['foo', 'bar'],
                                          ignore_case=True)
        self.assertConvertedValue('Foo', 'Foo')
        self.assertConvertedValue('bAr', 'bAr')

    def test_ignore_case_raises(self):
        self.type_instance = types.String(choices=['foo', 'bar'],
                                          ignore_case=False)
        self.assertRaises(ValueError, self.assertConvertedValue, 'Foo', 'Foo')

    def test_regex_and_ignore_case(self):
        self.type_instance = types.String(regex=re.compile("^[A-Z]"),
                                          ignore_case=True)
        self.assertConvertedValue("foo", "foo")

    def test_regex_and_ignore_case_str(self):
        self.type_instance = types.String(regex="^[A-Z]", ignore_case=True)
        self.assertConvertedValue("foo", "foo")

    def test_regex_preserve_flags(self):
        self.type_instance = types.String(regex=re.compile("^[A-Z]", re.I),
                                          ignore_case=False)
        self.assertConvertedValue("foo", "foo")

    def test_max_length(self):
        self.type_instance = types.String(max_length=5)
        self.assertInvalid('123456')
        self.assertConvertedValue('12345', '12345')


class BooleanTypeTests(TypeTestHelper, unittest.TestCase):
    type = types.Boolean()

    def test_True(self):
        self.assertConvertedValue('True', True)

    def test_yes(self):
        self.assertConvertedValue('yes', True)

    def test_on(self):
        self.assertConvertedValue('on', True)

    def test_1(self):
        self.assertConvertedValue('1', True)

    def test_False(self):
        self.assertConvertedValue('False', False)

    def test_no(self):
        self.assertConvertedValue('no', False)

    def test_off(self):
        self.assertConvertedValue('off', False)

    def test_0(self):
        self.assertConvertedValue('0', False)

    def test_other_values_produce_error(self):
        self.assertInvalid('foo')

    def test_repr(self):
        self.assertEqual('Boolean', repr(types.Boolean()))

    def test_equal(self):
        self.assertEqual(types.Boolean(), types.Boolean())

    def test_not_equal_to_other_class(self):
        self.assertFalse(types.Boolean() == types.String())


class IntegerTypeTests(TypeTestHelper, unittest.TestCase):
    type = types.Integer()

    def test_empty_string(self):
        self.assertConvertedValue('', None)

    def test_whitespace_string(self):
        self.assertConvertedValue("   \t\t\t\t", None)

    def test_positive_values_are_valid(self):
        self.assertConvertedValue('123', 123)

    def test_zero_is_valid(self):
        self.assertConvertedValue('0', 0)

    def test_negative_values_are_valid(self):
        self.assertConvertedValue('-123', -123)

    def test_leading_whitespace_is_ignored(self):
        self.assertConvertedValue('   5', 5)

    def test_trailing_whitespace_is_ignored(self):
        self.assertConvertedValue('7   ', 7)

    def test_non_digits_are_invalid(self):
        self.assertInvalid('12a45')

    def test_repr(self):
        t = types.Integer()
        self.assertEqual('Integer', repr(t))

    def test_repr_with_min(self):
        t = types.Integer(min=123)
        self.assertEqual('Integer(min=123)', repr(t))

    def test_repr_with_max(self):
        t = types.Integer(max=456)
        self.assertEqual('Integer(max=456)', repr(t))

    def test_repr_with_min_and_max(self):
        t = types.Integer(min=123, max=456)
        self.assertEqual('Integer(min=123, max=456)', repr(t))
        t = types.Integer(min=0, max=0)
        self.assertEqual('Integer(min=0, max=0)', repr(t))

    def test_repr_with_choices(self):
        t = types.Integer(choices=[80, 457])
        self.assertEqual('Integer(choices=[80, 457])', repr(t))

    def test_equal(self):
        self.assertTrue(types.Integer() == types.Integer())

    def test_equal_with_same_min_and_no_max(self):
        self.assertTrue(types.Integer(min=123) == types.Integer(min=123))

    def test_equal_with_same_max_and_no_min(self):
        self.assertTrue(types.Integer(max=123) == types.Integer(max=123))

    def test_equal_with_same_min_and_max(self):
        t1 = types.Integer(min=1, max=123)
        t2 = types.Integer(min=1, max=123)
        self.assertTrue(t1 == t2)

    def test_equal_with_same_choices(self):
        t1 = types.Integer(choices=[80, 457])
        t2 = types.Integer(choices=[457, 80])
        self.assertTrue(t1 == t2)

    def test_not_equal(self):
        self.assertFalse(types.Integer(min=123) == types.Integer(min=456))
        self.assertFalse(types.Integer(choices=[80, 457]) ==
                         types.Integer(choices=[80, 40]))
        self.assertFalse(types.Integer(choices=[80, 457]) ==
                         types.Integer())

    def test_not_equal_to_other_class(self):
        self.assertFalse(types.Integer() == types.String())

    def test_choices_with_min_max(self):
        self.assertRaises(ValueError,
                          types.Integer,
                          min=100,
                          choices=[50, 60])
        self.assertRaises(ValueError,
                          types.Integer,
                          max=10,
                          choices=[50, 60])
        types.Integer(min=10, max=100, choices=[50, 60])

    def test_min_greater_max(self):
        self.assertRaises(ValueError,
                          types.Integer,
                          min=100, max=50)
        self.assertRaises(ValueError,
                          types.Integer,
                          min=-50, max=-100)
        self.assertRaises(ValueError,
                          types.Integer,
                          min=0, max=-50)
        self.assertRaises(ValueError,
                          types.Integer,
                          min=50, max=0)

    def test_with_max_and_min(self):
        t = types.Integer(min=123, max=456)
        self.assertRaises(ValueError, t, 122)
        t(123)
        t(300)
        t(456)
        self.assertRaises(ValueError, t, 0)
        self.assertRaises(ValueError, t, 457)

    def test_with_min_zero(self):
        t = types.Integer(min=0, max=456)
        self.assertRaises(ValueError, t, -1)
        t(0)
        t(123)
        t(300)
        t(456)
        self.assertRaises(ValueError, t, -201)
        self.assertRaises(ValueError, t, 457)

    def test_with_max_zero(self):
        t = types.Integer(min=-456, max=0)
        self.assertRaises(ValueError, t, 1)
        t(0)
        t(-123)
        t(-300)
        t(-456)
        self.assertRaises(ValueError, t, 201)
        self.assertRaises(ValueError, t, -457)

    def test_with_choices_list(self):
        t = types.Integer(choices=[80, 457])
        self.assertRaises(ValueError, t, 1)
        self.assertRaises(ValueError, t, 200)
        self.assertRaises(ValueError, t, -457)
        t(80)
        t(457)

    def test_with_choices_tuple(self):
        t = types.Integer(choices=(80, 457))
        self.assertRaises(ValueError, t, 1)
        self.assertRaises(ValueError, t, 200)
        self.assertRaises(ValueError, t, -457)
        t(80)
        t(457)


class FloatTypeTests(TypeTestHelper, unittest.TestCase):
    type = types.Float()

    def test_decimal_format(self):
        v = self.type_instance('123.456')
        self.assertAlmostEqual(v, 123.456)

    def test_decimal_format_negative_float(self):
        v = self.type_instance('-123.456')
        self.assertAlmostEqual(v, -123.456)

    def test_exponential_format(self):
        v = self.type_instance('123e-2')
        self.assertAlmostEqual(v, 1.23)

    def test_non_float_is_invalid(self):
        self.assertInvalid('123,345')
        self.assertInvalid('foo')

    def test_repr(self):
        self.assertEqual('Float', repr(types.Float()))

    def test_repr_with_min(self):
        t = types.Float(min=1.1)
        self.assertEqual('Float(min=1.1)', repr(t))

    def test_repr_with_max(self):
        t = types.Float(max=2.2)
        self.assertEqual('Float(max=2.2)', repr(t))

    def test_repr_with_min_and_max(self):
        t = types.Float(min=1.1, max=2.2)
        self.assertEqual('Float(min=1.1, max=2.2)', repr(t))
        t = types.Float(min=1.0, max=2)
        self.assertEqual('Float(min=1, max=2)', repr(t))
        t = types.Float(min=0, max=0)
        self.assertEqual('Float(min=0, max=0)', repr(t))

    def test_equal(self):
        self.assertTrue(types.Float() == types.Float())

    def test_equal_with_same_min_and_no_max(self):
        self.assertTrue(types.Float(min=123.1) == types.Float(min=123.1))

    def test_equal_with_same_max_and_no_min(self):
        self.assertTrue(types.Float(max=123.1) == types.Float(max=123.1))

    def test_not_equal(self):
        self.assertFalse(types.Float(min=123.1) == types.Float(min=456.1))
        self.assertFalse(types.Float(max=123.1) == types.Float(max=456.1))
        self.assertFalse(types.Float(min=123.1) == types.Float(max=123.1))
        self.assertFalse(types.Float(min=123.1, max=456.1) ==
                         types.Float(min=123.1, max=456.2))

    def test_not_equal_to_other_class(self):
        self.assertFalse(types.Float() == types.Integer())

    def test_equal_with_same_min_and_max(self):
        t1 = types.Float(min=1.1, max=2.2)
        t2 = types.Float(min=1.1, max=2.2)
        self.assertTrue(t1 == t2)

    def test_min_greater_max(self):
        self.assertRaises(ValueError,
                          types.Float,
                          min=100.1, max=50)
        self.assertRaises(ValueError,
                          types.Float,
                          min=-50, max=-100.1)
        self.assertRaises(ValueError,
                          types.Float,
                          min=0.1, max=-50.0)
        self.assertRaises(ValueError,
                          types.Float,
                          min=50.0, max=0.0)

    def test_with_max_and_min(self):
        t = types.Float(min=123.45, max=678.9)
        self.assertRaises(ValueError, t, 123)
        self.assertRaises(ValueError, t, 123.1)
        t(124.1)
        t(300)
        t(456.0)
        self.assertRaises(ValueError, t, 0)
        self.assertRaises(ValueError, t, 800.5)

    def test_with_min_zero(self):
        t = types.Float(min=0, max=456.1)
        self.assertRaises(ValueError, t, -1)
        t(0.0)
        t(123.1)
        t(300.2)
        t(456.1)
        self.assertRaises(ValueError, t, -201.0)
        self.assertRaises(ValueError, t, 457.0)

    def test_with_max_zero(self):
        t = types.Float(min=-456.1, max=0)
        self.assertRaises(ValueError, t, 1)
        t(0.0)
        t(-123.0)
        t(-300.0)
        t(-456.0)
        self.assertRaises(ValueError, t, 201.0)
        self.assertRaises(ValueError, t, -457.0)


class ListTypeTests(TypeTestHelper, unittest.TestCase):
    type = types.List()

    def test_empty_value(self):
        self.assertConvertedValue('', [])

    def test_single_value(self):
        self.assertConvertedValue(' foo bar ',
                                  ['foo bar'])

    def test_list_of_values(self):
        self.assertConvertedValue(' foo bar, baz ',
                                  ['foo bar',
                                   'baz'])

    def test_list_of_values_containing_commas(self):
        self.type_instance = types.List(types.String(quotes=True))
        self.assertConvertedValue('foo,"bar, baz",bam',
                                  ['foo',
                                   'bar, baz',
                                   'bam'])

    def test_list_of_lists(self):
        self.type_instance = types.List(
            types.List(types.String(), bounds=True)
        )
        self.assertConvertedValue('[foo],[bar, baz],[bam]',
                                  [['foo'], ['bar', 'baz'], ['bam']])

    def test_list_of_custom_type(self):
        self.type_instance = types.List(types.Integer())
        self.assertConvertedValue('1,2,3,5',
                                  [1, 2, 3, 5])

    def test_bounds_parsing(self):
        self.type_instance = types.List(types.Integer(), bounds=True)
        self.assertConvertedValue('[1,2,3]', [1, 2, 3])

    def test_bounds_required(self):
        self.type_instance = types.List(types.Integer(), bounds=True)
        self.assertInvalid('1,2,3')
        self.assertInvalid('[1,2,3')
        self.assertInvalid('1,2,3]')

    def test_repr(self):
        t = types.List(types.Integer())
        self.assertEqual('List of Integer', repr(t))

    def test_equal(self):
        self.assertTrue(types.List() == types.List())

    def test_equal_with_equal_custom_item_types(self):
        it1 = types.Integer()
        it2 = types.Integer()
        self.assertTrue(types.List(it1) == types.List(it2))

    def test_not_equal_with_non_equal_custom_item_types(self):
        it1 = types.Integer()
        it2 = types.String()
        self.assertFalse(it1 == it2)
        self.assertFalse(types.List(it1) == types.List(it2))

    def test_not_equal_to_other_class(self):
        self.assertFalse(types.List() == types.Integer())


class DictTypeTests(TypeTestHelper, unittest.TestCase):
    type = types.Dict()

    def test_empty_value(self):
        self.assertConvertedValue('', {})

    def test_single_value(self):
        self.assertConvertedValue(' foo: bar ',
                                  {'foo': 'bar'})

    def test_dict_of_values(self):
        self.assertConvertedValue(' foo: bar, baz: 123 ',
                                  {'foo': 'bar',
                                   'baz': '123'})

    def test_custom_value_type(self):
        self.type_instance = types.Dict(types.Integer())
        self.assertConvertedValue('foo:123, bar: 456',
                                  {'foo': 123,
                                   'bar': 456})

    def test_dict_of_values_containing_commas(self):
        self.type_instance = types.Dict(types.String(quotes=True))
        self.assertConvertedValue('foo:"bar, baz",bam:quux',
                                  {'foo': 'bar, baz',
                                   'bam': 'quux'})

    def test_dict_of_dicts(self):
        self.type_instance = types.Dict(
            types.Dict(types.String(), bounds=True)
        )
        self.assertConvertedValue('k1:{k1:v1,k2:v2},k2:{k3:v3}',
                                  {'k1': {'k1': 'v1', 'k2': 'v2'},
                                   'k2': {'k3': 'v3'}})

    def test_bounds_parsing(self):
        self.type_instance = types.Dict(types.String(), bounds=True)
        self.assertConvertedValue('{foo:bar,baz:123}',
                                  {'foo': 'bar',
                                   'baz': '123'})

    def test_bounds_required(self):
        self.type_instance = types.Dict(types.String(), bounds=True)
        self.assertInvalid('foo:bar,baz:123')
        self.assertInvalid('{foo:bar,baz:123')
        self.assertInvalid('foo:bar,baz:123}')

    def test_no_mapping_produces_error(self):
        self.assertInvalid('foo,bar')

    def test_repr(self):
        t = types.Dict(types.Integer())
        self.assertEqual('Dict of Integer', repr(t))

    def test_equal(self):
        self.assertTrue(types.Dict() == types.Dict())

    def test_equal_with_equal_custom_item_types(self):
        it1 = types.Integer()
        it2 = types.Integer()
        self.assertTrue(types.Dict(it1) == types.Dict(it2))

    def test_not_equal_with_non_equal_custom_item_types(self):
        it1 = types.Integer()
        it2 = types.String()
        self.assertFalse(it1 == it2)
        self.assertFalse(types.Dict(it1) == types.Dict(it2))

    def test_not_equal_to_other_class(self):
        self.assertFalse(types.Dict() == types.Integer())


class IPAddressTypeTests(TypeTestHelper, unittest.TestCase):
    type = types.IPAddress()

    def test_ipv4_address(self):
        self.assertConvertedValue('192.168.0.1', '192.168.0.1')

    def test_ipv6_address(self):
        self.assertConvertedValue('abcd:ef::1', 'abcd:ef::1')

    def test_strings(self):
        self.assertInvalid('')
        self.assertInvalid('foo')

    def test_numbers(self):
        self.assertInvalid(1)
        self.assertInvalid(-1)
        self.assertInvalid(3.14)


class IPv4AddressTypeTests(IPAddressTypeTests):
    type = types.IPAddress(4)

    def test_ipv6_address(self):
        self.assertInvalid('abcd:ef::1')


class IPv6AddressTypeTests(IPAddressTypeTests):
    type = types.IPAddress(6)

    def test_ipv4_address(self):
        self.assertInvalid('192.168.0.1')


class HostnameTypeTests(TypeTestHelper, unittest.TestCase):
    type = types.Hostname()

    def assertConvertedEqual(self, value):
        self.assertConvertedValue(value, value)

    def test_empty_hostname_fails(self):
        self.assertInvalid('')

    def test_should_return_same_hostname_if_valid(self):
        self.assertConvertedEqual('foo.bar')

    def test_trailing_quote_is_invalid(self):
        self.assertInvalid('foo.bar"')

    def test_repr(self):
        self.assertEqual('Hostname', repr(types.Hostname()))

    def test_equal(self):
        self.assertEqual(types.Hostname(), types.Hostname())

    def test_not_equal_to_other_class(self):
        self.assertNotEqual(types.Hostname(), types.Integer())
        self.assertNotEqual(types.Hostname(), types.String())

    def test_invalid_characters(self):
        self.assertInvalid('"host"')
        self.assertInvalid("h'ost'")
        self.assertInvalid("h'ost")
        self.assertInvalid("h$ost")
        self.assertInvalid("h%ost")
        self.assertInvalid("host_01.co.uk")
        self.assertInvalid("host;name=99")
        self.assertInvalid('___site0.1001')
        self.assertInvalid('_site01001')
        self.assertInvalid("host..name")
        self.assertInvalid(".host.name.com")
        self.assertInvalid("no spaces")

    def test_no_start_end_hyphens(self):
        self.assertInvalid("-host.com")
        self.assertInvalid("-hostname.com-")
        self.assertInvalid("hostname.co.uk-")

    def test_strip_trailing_dot(self):
        self.assertConvertedValue('cell1.nova.site1.', 'cell1.nova.site1')
        self.assertConvertedValue('cell1.', 'cell1')

    def test_valid_hostname(self):
        self.assertConvertedEqual('cell1.nova.site1')
        self.assertConvertedEqual('site01001')
        self.assertConvertedEqual('home-site-here.org.com')
        self.assertConvertedEqual('192.168.0.1')
        self.assertConvertedEqual('1.1.1')
        self.assertConvertedEqual('localhost')

    def test_max_segment_size(self):
        self.assertConvertedEqual('host.%s.com' % ('x' * 63))
        self.assertInvalid('host.%s.com' % ('x' * 64))

    def test_max_hostname_size(self):
        test_str = '.'.join('x'*31 for x in range(8))
        self.assertEqual(255, len(test_str))
        self.assertInvalid(test_str)
        self.assertConvertedEqual(test_str[:-2])


class URITypeTests(TypeTestHelper, unittest.TestCase):
    type = types.URI()

    def test_uri(self):
        self.assertConvertedValue('http://example.com', 'http://example.com')
        self.assertInvalid('invalid')  # it doesn't include a scheme
        self.assertInvalid('http://')  # it doesn't include an authority

    def test_repr(self):
        self.assertEqual('URI', repr(types.URI()))

    def test_max_length(self):
        self.type_instance = types.String(max_length=30)
        self.assertInvalid('http://www.example.com/versions')
        self.assertConvertedValue('http://www.example.com',
                                  'http://www.example.com')


class PortTypeTests(TypeTestHelper, unittest.TestCase):
    type = types.Port()

    def test_port(self):
        self.assertInvalid(-1)
        self.assertInvalid(65536)
        self.assertConvertedValue('80', 80)
        self.assertConvertedValue('65535', 65535)

    def test_repr(self):
        self.assertEqual('Port(min=0, max=65535)', repr(types.Port()))

    def test_repr_with_min(self):
        t = types.Port(min=123)
        self.assertEqual('Port(min=123, max=65535)', repr(t))

    def test_repr_with_max(self):
        t = types.Port(max=456)
        self.assertEqual('Port(min=0, max=456)', repr(t))

    def test_repr_with_min_and_max(self):
        t = types.Port(min=123, max=456)
        self.assertEqual('Port(min=123, max=456)', repr(t))
        t = types.Port(min=0, max=0)
        self.assertEqual('Port(min=0, max=0)', repr(t))

    def test_repr_with_choices(self):
        t = types.Port(choices=[80, 457])
        self.assertEqual('Port(choices=[80, 457])', repr(t))

    def test_choices(self):
        t = types.Port(choices=[80, 457])
        self.assertRaises(ValueError, t, 1)
        self.assertRaises(ValueError, t, 200)
        t(80)
        t(457)

    def test_invalid_choices(self):
        self.assertRaises(ValueError, types.Port, choices=[-1, 457])
        self.assertRaises(ValueError, types.Port, choices=[1, 2, 3, 65536])

    def test_equal(self):
        self.assertTrue(types.Port() == types.Port())

    def test_equal_with_same_min_and_no_max(self):
        self.assertTrue(types.Port(min=123) == types.Port(min=123))

    def test_equal_with_same_max_and_no_min(self):
        self.assertTrue(types.Port(max=123) == types.Port(max=123))

    def test_equal_with_same_min_and_max(self):
        t1 = types.Port(min=1, max=123)
        t2 = types.Port(min=1, max=123)
        self.assertTrue(t1 == t2)

    def test_equal_with_same_choices(self):
        t1 = types.Port(choices=[80, 457])
        t2 = types.Port(choices=[457, 80])
        self.assertTrue(t1 == t2)

    def test_not_equal(self):
        self.assertFalse(types.Port(min=123) == types.Port(min=456))
        self.assertFalse(types.Port(choices=[80, 457]) ==
                         types.Port(choices=[80, 40]))
        self.assertFalse(types.Port(choices=[80, 457]) ==
                         types.Port())

    def test_not_equal_to_other_class(self):
        self.assertFalse(types.Port() == types.Integer())

    def test_choices_with_min_max(self):
        self.assertRaises(ValueError,
                          types.Port,
                          min=100,
                          choices=[50, 60])
        self.assertRaises(ValueError,
                          types.Port,
                          max=10,
                          choices=[50, 60])
        types.Port(min=10, max=100, choices=[50, 60])

    def test_min_greater_max(self):
        self.assertRaises(ValueError,
                          types.Port,
                          min=100, max=50)
        self.assertRaises(ValueError,
                          types.Port,
                          min=-50, max=-100)
        self.assertRaises(ValueError,
                          types.Port,
                          min=0, max=-50)
        self.assertRaises(ValueError,
                          types.Port,
                          min=50, max=0)

    def test_illegal_min(self):
        self.assertRaises(ValueError,
                          types.Port,
                          min=-1, max=50)
        self.assertRaises(ValueError,
                          types.Port,
                          min=-50)

    def test_illegal_max(self):
        self.assertRaises(ValueError,
                          types.Port,
                          min=100, max=65537)
        self.assertRaises(ValueError,
                          types.Port,
                          max=100000)

    def test_with_max_and_min(self):
        t = types.Port(min=123, max=456)
        self.assertRaises(ValueError, t, 122)
        t(123)
        t(300)
        t(456)
        self.assertRaises(ValueError, t, 0)
        self.assertRaises(ValueError, t, 457)

    def test_with_min_zero(self):
        t = types.Port(min=0, max=456)
        self.assertRaises(ValueError, t, -1)
        t(0)
        t(123)
        t(300)
        t(456)
        self.assertRaises(ValueError, t, -201)
        self.assertRaises(ValueError, t, 457)

    def test_with_max_zero(self):
        t = types.Port(max=0)
        self.assertRaises(ValueError, t, 1)
        t(0)

    def test_with_choices_list(self):
        t = types.Port(choices=[80, 457])
        self.assertRaises(ValueError, t, 1)
        self.assertRaises(ValueError, t, 200)
        self.assertRaises(ValueError, t, -457)
        t(80)
        t(457)

    def test_with_choices_tuple(self):
        t = types.Port(choices=(80, 457))
        self.assertRaises(ValueError, t, 1)
        self.assertRaises(ValueError, t, 200)
        self.assertRaises(ValueError, t, -457)
        t(80)
        t(457)
