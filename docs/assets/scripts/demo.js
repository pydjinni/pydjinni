var pyodideReadyPromise = pyodideReadyPromise || null
var demo_output;
var demo_input;
var demo_config;

function reportError(message) {
    demo_output.innerHTML += "<br>❌ " + message;
}

function reportSuccess(message) {
    demo_output.innerHTML = `✅ ${message}`
}

async function reportInstalledPackages(micropip) {
    packages = await micropip.list();
    let rows = packages.toString().split("\n").slice(2);
    demo_output.innerHTML = "💬 installing packages: "
    rows.forEach((row) => {
        demo_output.innerHTML += `${row.split(" | ")[0].trim()},  `;
    })
    demo_output.innerHTML += "..."
}

function reportStatus(message) {
    demo_output.innerHTML = `💬 ${message}`
}

async function highlight(element, richElement, language) {
    let pyodide = await pyodideReadyPromise;
    try {
        pyodide.FS.writeFile(`/tmp/${element.name}`, element.value, { encoding: "utf8" });
        richElement.innerHTML = pyodide.runPython(`
            from pygments import highlight
            from pygments.lexers import get_lexer_by_name
            from pygments.formatters import HtmlFormatter
            
            input_file = Path("/tmp/${element.name}")
            content = input_file.read_text()
            if content.endswith('\\n'):
                content += " "
            highlight(content, get_lexer_by_name("${language}"), HtmlFormatter())
        `)
    } catch (err) {
        reportError(err);
    }
}

function rich_edit_sync_scroll(element, richElement) {
  // Get and set x and y
  richElement.scrollTop = element.scrollTop;
  richElement.scrollLeft = element.scrollLeft;
}

async function configure_textfield(element, richElement, language) {
    await pyodideReadyPromise;
    element.addEventListener("keydown", function(e) {
        if (e.key == 'Tab') {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;

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
        }, 500);
        highlight(element, richElement, language);
        rich_edit_sync_scroll(element, richElement);
    });
    element.addEventListener("scroll", (e) => {
        rich_edit_sync_scroll(element, richElement);
    })
    await highlight(element, richElement, language);
    element.removeAttribute("disabled");
}

// init Pyodide
async function main() {
    let intervalId;
    try {
        reportStatus("loading demo... This may take a while...");
        let pyodide = await loadPyodide();
        await pyodide.loadPackage("micropip")
        const micropip = await pyodide.pyimport("micropip");
        intervalId = window.setInterval(() => {
            reportInstalledPackages(micropip);
        }, 200);
        await micropip.install("pygments==2.15");
        await micropip.install("https://github.com/pydantic/pydantic-core/releases/download/v0.23.1/pydantic_core-0.23.1-cp311-cp311-emscripten_3_1_32_wasm32.whl");
        await micropip.install("http://localhost:8001/pydjinni-0.1.2.dev27+gefd6587.d20230427-py3-none-any.whl")
        clearInterval(intervalId);
        reportStatus("ready... start defining your IDL!");
        return pyodide;
    } catch (err) {
        clearInterval(intervalId);
        reportError(err)
        return Promise.reject(err)
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
            const container = document.createElement("div");
            container.className = "output_container"
            const title = document.createElement("div");
            title.className = "filename";
            title.innerText = file;
            container.appendChild(title);
            const code = document.createElement("code");
            code.innerHTML = file_content;
            container.appendChild(code)
            target_element.appendChild(container);
        }
    })
}

async function generate(idl_content, config_content) {
    let pyodide = await pyodideReadyPromise;
    reportStatus("parsing & generating...")
    pyodide.FS.writeFile("/input.idl", idl_content, { encoding: "utf8" });
    pyodide.FS.writeFile("/pydjinni.yaml", config_content, { encoding: "utf8" });
    try {
        result = pyodide.runPython(`
            import shutil
            from pydjinni import API
            from pathlib import Path
            from pydjinni.exceptions import ApplicationException, ConfigurationException
            from pydjinni.parser.parser import IdlParser
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
                result = (0, "success")
            except IdlParser.ParsingException as e:
                result = (1, f"{e}")
            except ConfigurationException as e:
                result = (2, f"{e}")
            except ApplicationException as e:
                result = (3, f"{e}")
            result
        `);
        result_code = result.get(0);
        result_message = result.get(1);
        if(result_code === 1) { // parsing error
            reportError(result_message);
            demo_input.className = "error"
        } else if(result_code === 2) { //configuration error
            reportError(result_message);
            demo_config.className = "error"
        } else if(result_code === 3) { // other error
            reportError(result_message);
        } else {
            demo_input.className = ""
            demo_config.className = ""
            reportSuccess(result.get(1));
            await visualize_results("/out/cpp/html", "generated_cpp_files");
            await visualize_results("/out/java/html", "generated_java_files");
        }
    } catch (err) {
        reportError(err)
    }
}

function demo_init() {
    let edit_button = document.getElementsByClassName("md-content__button")[0]
    edit_button.innerHTML = ""
    demo_output = document.getElementById("demo_output");
    demo_input = document.getElementById("idl_input");
    rich_demo_input = document.getElementById("rich_idl_input");
    demo_config = document.getElementById("config_input");
    rich_demo_config = document.getElementById("rich_config_input");

    pyodideReadyPromise = pyodideReadyPromise || main();

    idl_input = window.sessionStorage.getItem("idl_input");
    config_input = window.sessionStorage.getItem("config_input");

    if(idl_input || config_input) {
        demo_input.value = idl_input;
        demo_config.value = config_input;
        generate(demo_input.value, demo_config.value);
    }
    configure_textfield(demo_input, rich_demo_input, "djinni");
    configure_textfield(demo_config, rich_demo_config, "yaml");
}

demo_init();
