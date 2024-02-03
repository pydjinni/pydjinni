# Copyright 2024 jothepro
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

from pydjinni.generator.target import Target
from pydjinni.parser.ast import Record
from .cppcli.generator import CppCliGenerator


class CppCliTarget(Target):
    """
    Generate C++/CLI interfaces.
    """
    key = "cppcli"
    generators = [CppCliGenerator]
    supported_deriving = {Record.Deriving.eq, Record.Deriving.ord, Record.Deriving.str}
