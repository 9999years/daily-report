import textwrap
import string
import tokenize

# local
from prefdicts import prefs, keys
import misc

class ExtendedFormatParser():
    """
    parses extended format-literals from, uh, non-literal strings

    tl;dr: arbitrary nesting is in, format and conversion specs (ending a
    replacement field with `!x:yyy`) is out (direct function calls to str(),
    repr(), hex(), or format() are better)

    [1]: https://docs.python.org/3/library/string.html#string.Formatter.parse
    """
    def __init__(self):
        self.code = ''

    def linebytes(self):
        for line in self.code.splitlines():
            yield line.encode('utf-8')

    def feed(self, code):
        self.code = code
        for tok in tokenize.tokenize(self.linebytes().__next__):
            print(tok.string, end='')

class ReportFormatter(string.Formatter):
    def __init__(self, **kwargs):
        # generic parts
        self.env       = kwargs
        self.saved_env = kwargs
        self.cache     = {}

    def save_env(self):
        self.saved_env = self.env.copy()

    def restore_env(self):
        self.env = self.saved_env

    def invalidate_cache(self):
        self.cache = {}

    def convert_field(self, field, spec):
        # look, the builtin modes
        # [r]epr
        # [s]tr
        # and [a]scii
        # are very uninteresting, so im cutting them out
        conversion_mapping = {
            'c': misc.center,
            'r': misc.right,
            'f': misc.fill,
            'l': lambda x: x.lower(),
            'u': lambda x: x.upper(),
            't': string.capwords, # for [t]itlecase
        }

        for c in conversion_mapping:
            if c in spec:
                field = conversion_mapping[c](field)

        return field

    def parse_field(self, field):
        # field is a tuple of
        # (literal text, replacement text, conversion, format spec)
        # 'locals are {locals()!r:s}' => ('locals are', 'locals()', 'r', 's')
        # parse(' ')    => (' ', None, None, None)
        # parse('{}')   => ('', '', '', None)
        # parse('{! }') => ('', '', '', ' ')
        # moral: check for None and len() > 0 on every field (except
        # literal_txt, which is guarenteed to be an empty string at worst)

        # tuple indicies
        literal_txt = 0
        repl_txt    = 1
        format_spec = 2
        conv_spec   = 3

        field_txt = ''

        if field[repl_txt] is not None:
            try:
                field_txt = eval(field[repl_txt],
                    {}, # globals
                    self.env # locals
                )
            except NameError as e:
                raise NameError(' '.join(e.args) + '\nEnvironment: \n' +
                    repr(self.env.keys())) from None

        if field[conv_spec] is not None and len(field[conv_spec]) > 0:
            field_txt = self.convert_field(field_txt, field[conv_spec])

        if field[format_spec] is not None and len(field[format_spec]) > 0:
            field_txt = self.format_field(
                field_txt, field[format_spec])
        else:
            field_txt = str(field_txt)

        return field[literal_txt] + field_txt


    def format(self, msg, **kwargs):
        """no you cant pass `msg` as a kwarg stop asking"""
        # narrator: nobody ever asked

        self.save_env()
        self.extend_env(kwargs)

        orig_msg = '\n'.join(msg) if isinstance(msg, list) else msg
        msg = ''

        # p = ExtendedFormatParser()
        # p.feed(orig_msg)

        for field in self.parse(orig_msg):
            msg += self.parse_field(field)

        msg = misc.deduplicate_rules(msg)

        self.restore_env()

        return msg

    def extend_env(self, vars={}, **kwargs):
        self.env.update(vars)
        self.env.update(kwargs)

formatter = ReportFormatter()
