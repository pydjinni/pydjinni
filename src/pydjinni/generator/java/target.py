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
from .java.generator import JavaGenerator
from .jni.generator import JniGenerator


class JavaTarget(Target):
    """
    Generate Java interface and JNI gluecode.

    This target generates a public Java interface as well as the required JNI gluecode to interact with the C++ interface.
    """
    key = "java"
    generators = [JavaGenerator, JniGenerator]
    supported_deriving = {Record.Deriving.eq, Record.Deriving.ord, Record.Deriving.str, Record.Deriving.parcelable}
