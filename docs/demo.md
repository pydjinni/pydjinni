---
template: demo.html
hide:
  - navigation
  - toc
---

<div id="demo" markdown>


<div class="demo-left" markdown>

=== "IDL"

    <span class=rich_editor>
        <code id="rich_idl_input" class="rich_text"></code>
        <textarea disabled id="idl_input" name="idl_input" placeholder="Define your PyDjinni interface here..." spellcheck="false">
    foo = enum {
        bar;
        baz;
    }
    </textarea>
    </span>
=== "Config"

    <span class=rich_editor>
        <code id="rich_config_input" class="rich_text"></code>
        <textarea disabled id="config_input" name="config_input" spellcheck="false">
    generate:
        cpp:
            namespace: foo::bar
        java:
            package: foo.bar
        jni:
            namespace: foo::bar::jni
        objc:
            type_prefix: FB
            swift_bridging_header: bridging_header.h
        cppcli:
            namespace: foo::bar::cppcli
    </textarea>
    </span>

</div>

<div class="demo-right" markdown>

=== "C++"

    <span id="generated_cpp_files" class="generated_listing" markdown>
        <span class="teaser">:material-file-code:<br>Generated C++ interfaces will be displayed here.</span>
    </span>

=== "Java"

    <span id="generated_java_files" class="generated_listing" markdown>
        <span class="teaser">:material-file-code:<br>Generated Java code will be displayed here.</span>
    </span>

=== "Objective-C"

    <span id="generated_objc_files" class="generated_listing" markdown>
        <span class="teaser">:material-file-code:<br>Generated Objective-C interfaces will be displayed here.</span>
    </span>

=== "C++/CLI"

    <span id="generated_cppcli_files" class="generated_listing" markdown>
        <span class="teaser">:material-file-code:<br>Generated C++/CLI (.NET) interfaces will be displayed here.</span>
    </span>

=== "YAML"

    <span id="generated_yaml_files" class="generated_listing" markdown>
        <span class="teaser">:material-file-code:<br>Generated export YAML will be displayed here.</span>
    </span>

</div>

</div>

<div id="demo_output">
    This demo uses Pyodide to execute Python code in the Browser. It requires Javascript and a good portion of luck to work!
</div>

<small>This demo runs on PyDjinni v<span id="pydjinni_version">{{ pydjinni_version() }}</span>. It uses the amazing [Pyodide](https://pyodide.org/){ target=_blank } project to execute Python code in the browser.
    No data is sent to a server!</small>
