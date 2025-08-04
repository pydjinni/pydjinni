/*#
Copyright 2023 -2024 jothepro

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
#*/
//> extends "base.jinja2"

//> block content
//> for property in type_def.properties
[[nodiscard]] {{ property.cpp.return_type_spec }} {{ type_def.cpp.name }}::{{ property.cpp.getter }}() const noexcept {
    return _{{ property.cpp.name }};
}
pydjinni::signals::connection {{ type_def.cpp.name }}::{{ property.cpp.notifier }}(const std::function<void({{ property.cpp.type_spec }})>& callback) noexcept {
    return _signal_{{ property.cpp.name }}_changed.connect(callback);
}

void {{ type_def.cpp.name }}::{{ property.cpp.setter }}({{ property.cpp.type_spec }} value) noexcept {
    _{{ property.cpp.name }} = value;
    _signal_{{ property.cpp.name }}_changed.notify(_{{ property.cpp.name }});
}

//> endfor
//> endblock
