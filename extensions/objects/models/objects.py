# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Classes for interpreting typed objects in Oppia."""

__author__ = 'Sean Lip'

import base64
import copy
import os
import StringIO
import tarfile

import feconf
import schema_utils
import utils


class BaseObject(object):
    """Base object class.

    This is the superclass for typed object specifications in Oppia, such as
    SanitizedUrl and CoordTwoDim.

    Typed objects are initialized from a raw Python object which is expected to
    be derived from a JSON object. They are validated and normalized to basic
    Python objects (primitive types combined via lists and dicts; no sets or
    tuples).
    """

    # These values should be overridden in subclasses.
    description = ''
    edit_html_filename = None
    edit_js_filename = None

    @classmethod
    def normalize(cls, raw):
        """Validates and normalizes a raw Python object.

        Returns:
          a normalized Python object describing the Object specified by this
          class.

        Raises:
          TypeError: if the Python object cannot be normalized.
        """
        return schema_utils.normalize_against_schema(raw, cls.SCHEMA)

    @classmethod
    def has_editor_js_template(cls):
        return cls.edit_js_filename is not None

    @classmethod
    def get_editor_js_template(cls):
        if cls.edit_js_filename is None:
            raise Exception(
                'There is no editor template defined for objects of type %s' %
                cls.__name__)
        return utils.get_file_contents(os.path.join(
            os.getcwd(), feconf.OBJECT_TEMPLATES_DIR,
            '%s.js' % cls.edit_js_filename))

    @classmethod
    def get_editor_html_template(cls):
        if cls.edit_html_filename is None:
            raise Exception(
                'There is no editor template defined for objects of type %s' %
                cls.__name__)
        return utils.get_file_contents(os.path.join(
            os.getcwd(), feconf.OBJECT_TEMPLATES_DIR,
            '%s.html' % cls.edit_html_filename))


class Null(BaseObject):
    """Class for a null object."""

    description = 'A null object.'

    @classmethod
    def normalize(cls, raw):
        """Validates and normalizes a raw Python object."""
        return None


class Boolean(BaseObject):
    """Class for booleans."""

    description = 'A boolean.'
    edit_html_filename = 'boolean_editor'
    edit_js_filename = 'BooleanEditor'

    SCHEMA = {
        'type': 'bool'
    }

    @classmethod
    def normalize(cls, raw):
        """Validates and normalizes a raw Python object."""
        if raw is None or raw == '':
            raw = False

        return schema_utils.normalize_against_schema(raw, cls.SCHEMA)


class Real(BaseObject):
    """Real number class."""

    description = 'A real number.'
    edit_html_filename = 'real_editor'
    edit_js_filename = 'RealEditor'

    SCHEMA = {
        'type': 'float'
    }


class Int(BaseObject):
    """Integer class."""

    description = 'An integer.'
    edit_html_filename = 'int_editor'
    edit_js_filename = 'IntEditor'

    SCHEMA = {
        'type': 'int'
    }


class UnicodeString(BaseObject):
    """Unicode string class."""

    description = 'A unicode string.'
    edit_html_filename = 'unicode_string_editor'
    edit_js_filename = 'UnicodeStringEditor'

    SCHEMA = {
        'type': 'unicode',
    }


class Html(BaseObject):
    """HTML string class."""

    description = 'An HTML string.'
    edit_html_filename = 'html_editor'
    edit_js_filename = 'HtmlEditor'

    SCHEMA = {
        'type': 'html',
    }


class NonnegativeInt(BaseObject):
    """Nonnegative integer class."""

    description = 'A non-negative integer.'
    edit_html_filename = 'nonnegative_int_editor'
    edit_js_filename = 'NonnegativeIntEditor'

    SCHEMA = {
        'type': 'int',
        'validators': [{
            'id': 'is_at_least',
            'min_value': 0
        }]
    }


class CodeEvaluation(BaseObject):
    """Evaluation result of programming code."""

    description = 'Code and its evaluation results.'

    SCHEMA = {
        'type': 'dict',
        'properties': [{
            'name': 'code',
            'schema': UnicodeString.SCHEMA,
        }, {
            'name': 'output',
            'schema': UnicodeString.SCHEMA,
        }, {
            'name': 'evaluation',
            'schema': UnicodeString.SCHEMA,
        }, {
            'name': 'error',
            'schema': UnicodeString.SCHEMA,
        }]
    }


class CoordTwoDim(BaseObject):
    """2D coordinate class."""

    description = 'A two-dimensional coordinate (a pair of reals).'
    edit_html_filename = 'coord_two_dim_editor'
    edit_js_filename = 'CoordTwoDimEditor'

    SCHEMA = {
        'type': 'list',
        'len': 2,
        'items': Real.SCHEMA,
    }


class ListOfUnicodeString(BaseObject):
    """List class."""

    description = 'A list.'
    edit_html_filename = 'list_editor'
    edit_js_filename = 'ListOfUnicodeStringEditor'

    SCHEMA = {
        'type': 'list',
        'items': UnicodeString.SCHEMA
    }


class SetOfUnicodeString(BaseObject):
    """Class for sets of UnicodeStrings."""

    description = 'A set (a list with unique elements) of unicode strings.'
    edit_html_filename = 'list_editor'
    edit_js_filename = 'SetOfUnicodeStringEditor'

    SCHEMA = {
        'type': 'list',
        'items': UnicodeString.SCHEMA,
        'validators': [{
            'id': 'is_uniquified'
        }]
    }


class NormalizedString(BaseObject):
    """Unicode string with spaces collapsed."""

    description = 'A unicode string with adjacent whitespace collapsed.'
    edit_html_filename = 'unicode_string_editor'
    edit_js_filename = 'NormalizedStringEditor'

    SCHEMA = {
        'type': 'unicode',
        'post_normalizers': [{
            'id': 'normalize_spaces'
        }]
    }


class MathLatexString(BaseObject):
    """Math LaTeX string class"""

    description = 'A LaTeX string.'
    edit_html_filename = 'math_latex_string_editor'
    edit_js_filename = 'MathLatexStringEditor'

    SCHEMA = UnicodeString.SCHEMA


class SanitizedUrl(BaseObject):
    """HTTP or HTTPS url string class."""

    description = 'An HTTP or HTTPS url.'
    edit_html_filename = 'unicode_string_editor'
    edit_js_filename = 'SanitizedUrlEditor'

    SCHEMA = {
        'type': 'unicode',
        'post_normalizers': [{
            'id': 'sanitize_url'
        }]
    }


class MusicPhrase(BaseObject):
    """List of Objects that represent a musical phrase."""

    description = ('A musical phrase that contains zero or more notes, rests, '
                   'and time signature.')
    edit_html_filename = 'music_phrase_editor'
    edit_js_filename = 'MusicPhraseEditor'

    _FRACTION_PART_SCHEMA = {
        'type': 'int',
        'validators': [{
            'id': 'is_at_least',
            'min_value': 1
        }]
    }

    SCHEMA = {
        'type': 'list',
        'items': {
            'type': 'dict',
            'properties': [{
                'name': 'readableNoteName',
                'schema': {
                    'type': 'unicode',
                    'choices': [
                        'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5',
                        'D5', 'E5', 'F5', 'G5', 'A5'
                    ]
                }
            }, {
                'name': 'noteDuration',
                'schema': {
                    'type': 'dict',
                    'properties': [{
                        'name': 'num',
                        'schema': _FRACTION_PART_SCHEMA
                    }, {
                        'name': 'den',
                        'schema': _FRACTION_PART_SCHEMA
                    }]
                }
            }],
        }
    }


class Filepath(BaseObject):
    """A string representing a filepath.

    The path will be prefixed with '[exploration_id]/assets'.
    """

    description = 'A string that represents a filepath'
    edit_html_filename = 'filepath_editor'
    edit_js_filename = 'FilepathEditor'

    SCHEMA = UnicodeString.SCHEMA


class CheckedProof(BaseObject):
    """A proof attempt and any errors it makes."""

    description = 'A proof attempt and any errors it makes.'

    @classmethod
    def normalize(cls, raw):
        """Validates and normalizes a raw Python object."""
        try:
            assert isinstance(raw, dict)
            assert isinstance(raw['assumptions_string'], basestring)
            assert isinstance(raw['target_string'], basestring)
            assert isinstance(raw['proof_string'], basestring)
            assert raw['correct'] in [True, False]
            if not raw['correct']:
                assert isinstance(raw['error_category'], basestring)
                assert isinstance(raw['error_code'], basestring)
                assert isinstance(raw['error_message'], basestring)
                assert isinstance(raw['error_line_number'], int)
            return copy.deepcopy(raw)
        except Exception:
            raise TypeError('Cannot convert to checked proof %s' % raw)


class LogicQuestion(BaseObject):
    """A question giving a formula to prove"""

    description = 'A question giving a formula to prove.'
    edit_html_filename = 'logic_question_editor'
    edit_js_filename = 'LogicQuestionEditor'

    @classmethod
    def normalize(cls, raw):
        """Validates and normalizes a raw Python object."""

        def _validateExpression(expression):
            assert isinstance(expression, dict)
            assert isinstance(expression['top_kind_name'], basestring)
            assert isinstance(expression['top_operator_name'], basestring)
            _validateExpressionArray(expression['arguments'])
            _validateExpressionArray(expression['dummies'])

        def _validateExpressionArray(array):
            assert isinstance(array, list)
            for item in array:
                _validateExpression(item)

        try:
            assert isinstance(raw, dict)
            _validateExpressionArray(raw['assumptions'])
            _validateExpressionArray(raw['results'])
            assert isinstance(raw['default_proof_string'], basestring)

            return copy.deepcopy(raw)
        except Exception:
            raise TypeError('Cannot convert to a logic question %s' % raw)


class LogicErrorCategory(BaseObject):
    """A string from a list of possible categories"""

    description = 'One of the possible error categories of a logic proof.'
    edit_html_filename = 'logic_error_category_editor'
    edit_js_filename = 'LogicErrorCategoryEditor'

    SCHEMA = {
        'type': 'unicode',
        'choices': [
            'parsing', 'typing', 'line', 'layout', 'variables', 'logic',
            'target', 'mistake'
        ]
    }


class Graph(BaseObject):
    """A (mathematical) graph with edges and vertices"""

    description = 'A (mathematical) graph'
    edit_html_filename = 'graph_editor'
    edit_js_filename = 'GraphEditor'

    _schema = {
        'type': 'dict',
        'properties': {
           'vertices': {
               'type': 'list',
               'items': {
                   'type': 'dict',
                   'properties': {
                       'label': {
                           'type': 'unicode'
                       },
                       'x': {
                           'type': 'float'
                       },
                       'y': {
                           'type': 'float'
                       }
                   }
               }
           },
           'edges': {
               'type': 'list',
               'items': {
                   'type': 'dict',
                   'properties': {
                       'src': {
                           'type': 'int'
                       },
                       'dst': {
                           'type': 'int'
                       },
                       'weight': {
                           'type': 'int'
                       }
                   }
               }
           },
           'isDirected': {
               'type': 'bool'
           },
           'isWeighted': {
               'type': 'bool'
           },
           'isLabeled': {
               'type': 'bool'
           }
        }
     }

