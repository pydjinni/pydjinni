var pyodideReadyPromise = pyodideReadyPromise || null
var demo_output = null
var demo_input = null
var demo_config = null

function configure_textfield(element) {
    element.addEventListener("keydown", function(e) {
        if (e.key == 'Tab') {
            e.preventDefault();
            var start = this.selectionStart;
            var end = this.selectionEnd;

            // set textarea value to: text before caret + tab + text after caret
            this.value = this.value.substring(0, start) +
              "    " + this.value.substring(end);

            // put caret at right position again
            this.selectionStart =
              this.selectionEnd = start + 4;
        }
    });
    var timeoutID;
    element.addEventListener("input", (e) => {
        clearTimeout(timeoutID);
        timeoutID = setTimeout(function() {
            generate(demo_input.value, demo_config.value);
            window.sessionStorage.setItem("idl_input", demo_input.value);
            window.sessionStorage.setItem("config_input", demo_config.value);
        }, 400);

    });
}

// init Pyodide
async function main() {
    try {
        demo_output.innerText = "⏱️ loading demo... This may take a while..."
        let pyodide = await loadPyodide();
        demo_output.innerText = "💬 installing packages..."
        await pyodide.loadPackage("micropip")
        const micropip = pyodide.pyimport("micropip");
        demo_output.innerText += "pygments, "
        await micropip.install("pygments==2.15");
        demo_output.innerText += "pydantic-core, "
        await micropip.install("https://github.com/pydantic/pydantic-core/releases/download/v0.23.1/pydantic_core-0.23.1-cp311-cp311-emscripten_3_1_32_wasm32.whl");
        demo_output.innerText += "pydjinni"
        await micropip.install("http://localhost:8001/pydjinni-0.1.2.dev27+gefd6587.d20230427-py3-none-any.whl")
        demo_output.innerText = "ready... start defining your IDL!"
        return pyodide;
    } catch (err) {
      demo_output.innerText = "❌ " + err;
    }
}

async function visualize_results(path, target_element_id) {
    let pyodide = await pyodideReadyPromise;
    target_element = document.getElementById(target_element_id);
    target_element.innerHTML = "";
    files = pyodide.FS.readdir(path)
    files.forEach((file) => {
        if(file != ".." && file != ".") {
            file_content = pyodide.FS.readFile(path + "/" + file, { encoding: 'utf8' })
            title = document.createElement("h4");
            title.innerText = file;
            target_element.appendChild(title);
            code = document.createElement("code");
            code.innerHTML = file_content;
            target_element.appendChild(code);
        }
    })
}

async function generate(idl_content, config_content) {
    let pyodide = await pyodideReadyPromise;
    pyodide.FS.writeFile("/input.idl", idl_content, { encoding: "utf8" });
    pyodide.FS.writeFile("/pydjinni.yaml", config_content, { encoding: "utf8" });
    try {
        demo_output.innerText = "parsing & generating..."
        result = pyodide.runPython(`
            import shutil
            from pydjinni import API
            from pathlib import Path
            from pydjinni.exceptions import ApplicationException
            from pygments import highlight
            from pygments.lexers import CppLexer, JavaLexer
            from pygments.formatters import HtmlFormatter

            result = ""

            cpp_header_path = Path("/out/cpp/header")
            cpp_html_path = Path("/out/cpp/html")
            java_source_path = Path("/out/java/source")
            java_html_path = Path("/out/java/html")
            try:
                api = API().configure("/pydjinni.yaml", options={
                    "generate": {
                        "cpp": {
                            "out": {
                                "header": cpp_header_path,
                                "source": "/out/cpp/source"
                            }
                        },
                        "java": {
                            "out": java_source_path
                        },
                        "jni": {
                            "out": {
                                "header": "/out/jni/header",
                                "source": "/out/jni/source"
                            }
                        }
                    }
                }).parse("/input.idl").generate("cpp", clean=True).generate("java", clean=True)
                
                def highlight_generated_files(source_path: Path, target_path: Path, lexer):
                    files = source_path.glob("*")
                    shutil.rmtree(target_path, ignore_errors=True)
                    target_path.mkdir(parents=True, exist_ok=True)
                    for file in files:
                        if file.is_file():
                            output_file = target_path / file.name
                            output_file.write_text(highlight(file.read_text(), lexer, HtmlFormatter()))

                highlight_generated_files(cpp_header_path, cpp_html_path, CppLexer())
                highlight_generated_files(java_source_path, java_html_path, JavaLexer())
                result = "✅ success"
            except ApplicationException as e:
                result = f"❌ {e}"
            result
        `);
        demo_output.innerText = result;
        if(result == "✅ success") {
            await visualize_results("/out/cpp/html", "generated_cpp_files");
            await visualize_results("/out/java/html", "generated_java_files");
        }

    } catch (err) {
      demo_output.innerText = err;
    }
}

function demo_init() {
    let edit_button = document.getElementsByClassName("md-content__button")[0]
    edit_button.innerHTML = ""
    demo_output = document.getElementById("demo_output");
    demo_input = document.getElementById("idl_input");
    demo_config = document.getElementById("config_input");

    configure_textfield(demo_input);
    configure_textfield(demo_config);
    idl_input = window.sessionStorage.getItem("idl_input");
    config_input = window.sessionStorage.getItem("config_input");

    pyodideReadyPromise = pyodideReadyPromise || main();

    if(idl_input || config_input) {
        demo_input.value = idl_input;
        demo_config.value = config_input;
        generate(demo_input.value, demo_config.value);
    }
}

demo_init();
