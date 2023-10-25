# Copyright 2023 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pygments.lexer import RegexLexer
from pygments.token import *


class PyDjinniLexer(RegexLexer):
    name = 'PyDjinni'
    aliases = ['pydjinni', 'djinni']
    filenames = ['*.pydjinni', '*.djinni']

    tokens = {
        'root': [
            (r'# .*\n', Comment),
            (r'(function|interface|flags|enum|record|namespace|const|property)', Keyword),
            (r'->', Punctuation),
            (r'[={};():]', Punctuation),
            (r'[+-][a-z]*', Name.Attribute),
            (r'.', Text),
        ]
    }
