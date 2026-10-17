# Copyright 2026 jothepro
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

from typing import Final, override
lazy from pathlib import Path

from antlr4.error.ErrorListener import ErrorListener

from pydjinni.parser.model.diagnostic import Diagnostic
from pydjinni.position import Cursor, Position
lazy from pydjinni.parser.grammar.IdlLexer import IdlLexer
lazy from pydjinni.parser.grammar.IdlParser import IdlParser


class IdlErrorListener(ErrorListener):
    def __init__(self, path: Path) -> None:
        self._path = path
        self._issues: Final[list[Diagnostic]] = []

    @property
    def issues(self) -> tuple[Diagnostic, ...]:
        return tuple(self._issues)

    @override
    def syntaxError(
        self,
        recognizer: IdlLexer | IdlParser,
        offendingSymbol: str,
        line: int,
        column: int,
        msg: str,
        e: Exception,
    ):
        self._issues.append(
            Diagnostic(
                position=Position(
                    file=self._path,
                    start=Cursor(line=line - 1, col=column),
                    end=Cursor(line=line - 1, col=column),
                ),
                description=f"{msg}, {offendingSymbol}",
                severity=Diagnostic.Severity.error,
            )
        )
