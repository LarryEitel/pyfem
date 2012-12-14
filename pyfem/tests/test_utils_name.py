# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

from core import BaseTestCase

from utils.name import slug, abbreviate

# https://gist.github.com/1428479
class TestSlug(BaseTestCase):
    def test_should_always_return_lowercase_words(self):
        self.assertEquals(slug('ALVAROJUSTEN'), 'alvarojusten')

    def test_should_replace_space_with_dash(self):
        self.assertEquals(slug('Alvaro Justen'), 'alvaro-justen')

    def test_should_ignore_unecessary_spaces(self):
        self.assertEquals(slug('  alvaro   justen  '), 'alvaro-justen')

    def test_should_replace_nonascii_chars_with_corresponding_ascii_chars(self):
        self.assertEquals(slug('áÁàÀãÃâÂäÄ'.decode('utf8')), 'aaaaaaaaaa')
        self.assertEquals(slug('éÉèÈẽẼêÊëË'.decode('utf8')), 'eeeeeeeeee')
        self.assertEquals(slug('íÍìÌĩĨîÎïÏ'.decode('utf8')), 'iiiiiiiiii')
        self.assertEquals(slug('óÓòÒõÕôÔöÖ'.decode('utf8')), 'oooooooooo')
        self.assertEquals(slug('úÚùÙũŨûÛüÜ'.decode('utf8')), 'uuuuuuuuuu')
        self.assertEquals(slug('ćĆĉĈçÇ'.decode('utf8')), 'cccccc')

    def test_should_accept_unicode_text(self):
        self.assertEquals(slug(u'Álvaro Justen'), 'alvaro-justen')

    def test_should_accept_other_input_encodings(self):
        slugged_text = slug(u'Álvaro Justen'.encode('utf16'), 'utf16')
        self.assertEquals(slugged_text, 'alvaro-justen')

    def test_should_accept_only_ascii_letters_and_numbers(self):
        slugged_text = slug('''qwerty123456"'@#$%*()_+\|<>,.;:/?]~[`{}^ ''')
        self.assertEquals(slugged_text, 'qwerty123456')

    def test_should_accept_only_chars_in_permitted_chars_parameter(self):
        slugged_text = slug('''0987654321gfdsazxcvb''',
                            permitted_chars='abc123')
        self.assertEquals(slugged_text, '321acb')

class TestAbbreviate(unittest.TestCase):
    def test_name_and_last_name_should_return_equal(self):
        name = 'Álvaro Justen'
        expected = 'Álvaro Justen'
        self.assertEquals(abbreviate(name), expected)

    def test_name_with_two_surnames_should_abbreviate_the_middle_one(self):
        name = 'Álvaro Fernandes Justen'
        expected = 'Álvaro F. Justen'
        self.assertEquals(abbreviate(name), expected)

    def test_three_surnames_should_abbreviate_the_two_in_the_middle(self):
        name = 'Álvaro Fernandes Abreu Justen'
        expected = 'Álvaro F. A. Justen'
        self.assertEquals(abbreviate(name), expected)

    def test_should_not_abbreviate_tiny_words(self):
        name = 'Álvaro Fernandes de Abreu Justen'
        expected = 'Álvaro F. de A. Justen'
        self.assertEquals(abbreviate(name), expected)
        name = 'Fulano da Costa e Silva'
        expected = 'Fulano da C. e Silva'
        self.assertEquals(abbreviate(name), expected)
        name = 'Fulano dos Santos'
        expected = 'Fulano dos Santos'
        self.assertEquals(abbreviate(name), expected)

    def test_should_not_abbreviate_next_surname_if_pretty_is_True(self):
        name = 'Álvaro Fernandes de Abreu Justen'
        expected = 'Álvaro F. de Abreu Justen'
        self.assertEquals(abbreviate(name, pretty=True), expected)
        name = 'Rafael da Costa Rodrigues Silva'
        expected = 'Rafael da Costa R. Silva'
        self.assertEquals(abbreviate(name, pretty=True), expected)













if __name__ == "__main__":
    unittest.main()