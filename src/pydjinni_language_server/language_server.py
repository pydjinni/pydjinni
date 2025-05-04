# Copyright 2025 jothepro
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

from traceback import TracebackException

from lsprotocol.types import *
from pygls.server import LanguageServer, ServerErrors
from pydjinni_language_server.api import Workspace
from .text_document_path import TextDocumentPath


class PyDjinniLanguageServer(LanguageServer):

    def report_server_error(self, error: Exception, source: ServerErrors):
        self.show_message_log(TracebackException.from_exception(error).format(), msg_type=MessageType.Error)

    async def register_workspace_capabilites(self, workspace: Workspace):
        await self.register_capability_async(
            RegistrationParams(
                registrations=[
                    Registration(
                        id=str(workspace.uuid),
                        method=WORKSPACE_DID_CHANGE_WATCHED_FILES,
                        register_options=DidChangeWatchedFilesRegistrationOptions(
                            watchers=[
                                FileSystemWatcher(glob_pattern=RelativePattern(workspace.root_uri, "**/*.pydjinni")),
                                FileSystemWatcher(
                                    glob_pattern=RelativePattern(
                                        workspace.root_uri, workspace.configuration.config.as_posix()
                                    )
                                ),
                            ]
                        ),
                    ),
                ]
            )
        )

    async def unregister_workspace_capabilities(self, workspace: Workspace):
        await self.unregister_capability_async(
            UnregistrationParams([Unregistration(id=str(workspace.uuid), method=WORKSPACE_DID_CHANGE_WATCHED_FILES)])
        )

    async def update_workspace_capabilities(self, workspace: Workspace):
        await self.unregister_workspace_capabilities(workspace)
        await self.register_workspace_capabilites(workspace)

    def get_text_document_path(self, uri: str):
        return TextDocumentPath(self.workspace.get_text_document(uri))
