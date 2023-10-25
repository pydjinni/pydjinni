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

from pydjinni.generator.target import Target
from pydjinni.parser.ast import Record
from .objc.generator import ObjcGenerator
from .objcpp.generator import ObjcppGenerator


class ObjcTarget(Target):
    """
    Generate Objective-C interface and Objective-C++ gluecode.

    The output of this can also be used to interface with Swift, when the bridging-header generation is enabled.
    """
    key = "objc"
    generators = [ObjcGenerator, ObjcppGenerator]
    supported_deriving = {Record.Deriving.eq, Record.Deriving.ord, Record.Deriving.str}
