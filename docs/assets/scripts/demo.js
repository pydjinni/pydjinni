var pyodideReadyPromise = pyodideReadyPromise || null
/** @type {Element} */
var demoOutputElement;
/** @type {Element} */
var idlInputElement
/** @type {Element} */;
var configInputElement;

/**
 * Appends an error message to the output in the 'output console' element
 * @param {string} message
 */
function reportError(message) {
    demoOutputElement.innerHTML += "<br>❌ " + message;
}

/**
 * Prints a success status in the 'output console' element (used to report generation success).
 * @param {string} message
 */
function reportSuccess(message) {
    demoOutputElement.innerHTML = `✅ ${message}`
}

/**
 * Prints a status message in the 'output console' element
 * @param message
 */
function reportStatus(message) {
    demoOutputElement.innerHTML = `💬 ${message}`
}

/**
 * prints a list of all currently installed packages in the 'output console' element.
 * @param micropip
 * @returns {Promise<void>}
 */
async function reportInstalledPackages(micropip) {
    packages = await micropip.list();
    let rows = packages.toString().split("\n").slice(2);
    demoOutputElement.innerHTML = "💬 installing packages: "
    rows.forEach((row) => {
        demoOutputElement.innerHTML += `${row.split(" | ")[0].trim()},  `;
    })
    demoOutputElement.innerHTML += "..."
}



/**
 * Takes the value of a textarea and renders it with pygments in the specified language
 * @param {Element} element The textarea that serves as input
 * @param {Element} richElement The target element that will display the formatted code.
 * @param {string} language Language of the input
 * @returns {Promise<void>}
 */
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
            if content.startswith('\\n'):
                content = " " + content
            highlight(content, get_lexer_by_name("${language}"), HtmlFormatter())
        `)
    } catch (err) {
        reportError(err);
    }
}

/**
 * used for synchronizing the scroll position between the textarea and the rich-text rendering in the background.
 * @param {Element} element the textarea that has been scrolled.
 * @param {Element} richElement the background element that needs to by adjusted to have the same scroll position.
 */
function richEditSyncScroll(element, richElement) {
  // Get and set x and y
  richElement.scrollTop = element.scrollTop;
  richElement.scrollLeft = element.scrollLeft;
}

/**
 * Configures the textarea. Adds the following behavior:
 * * 'Tab'-keypresses will add 4 whitespaces instead of jumping to the next input.
 * * When the content changes, re-generation of the output files will be triggered after no changes occurred for 500ms.
 * * When the content changes, it will be formatted with Pygments and rendered in the `richElement` element.
 *
 * @see https://css-tricks.com/creating-an-editable-textarea-that-supports-syntax-highlighted-code/
 *
 * @param {Element} element The textarea element.
 * @param {Element} richElement The background element that renders the formatted input.
 * @param {string} language The language of the textarea
 * @returns {Promise<void>}
 */
async function configureTextarea(element, richElement, language) {
    await pyodideReadyPromise;
    element.addEventListener("keydown", (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = e.target.selectionStart;
            const end = e.target.selectionEnd;

            // set textarea value to: text before caret + tab + text after caret
            e.target.value = e.target.value.substring(0, start) +
              "    " + e.target.value.substring(end);

            // put caret at right position again
            e.target.selectionStart = e.target.selectionEnd = start + 4;
            highlight(element, richElement, language);
        }
    });
    let timeoutID;
    element.addEventListener("input", (e) => {
        clearTimeout(timeoutID);
        timeoutID = setTimeout(function() {
            generate(idlInputElement.value, configInputElement.value);
            window.sessionStorage.setItem("idl_input", idlInputElement.value);
            window.sessionStorage.setItem("config_input", configInputElement.value);
        }, 500);
        highlight(element, richElement, language);
        richEditSyncScroll(element, richElement);
    });
    element.addEventListener("scroll", (e) => {
        richEditSyncScroll(element, richElement);
    })
    await highlight(element, richElement, language);
    element.removeAttribute("disabled");
}

/**
 * Initializes the Pyodine environment. Installs all required dependencies.
 * @param {string} version       Version of Pydjinni that should be loaded from PyPi
 * @param {boolean} localFallback Fallback URL for local development.
 *                               Will load the given file from localhost:8001 if specified
 * @returns {Promise<*>}
 */
async function main(version, localFallback) {
    let intervalId;
    try {
        reportStatus("loading demo... This will take a while...");
        let pyodide = await loadPyodide();
        await pyodide.loadPackage("micropip")
        const micropip = await pyodide.pyimport("micropip");
        intervalId = window.setInterval(() => {
            reportInstalledPackages(micropip);
        }, 200);
        await micropip.install("pygments==2.19.1");
        if(localFallback) {
            await micropip.install(`http://localhost:8001/pydjinni-${version}-py3-none-any.whl`)
        } else {
            await micropip.install(`pydjinni==${version}`)
        }
        clearInterval(intervalId);
        reportStatus("ready...");
        return pyodide;
    } catch (err) {
        clearInterval(intervalId);
        reportError(err)
        return Promise.reject(err)
    }
}


/**
 * takes IDL content and parses it with PyDjinni. Generates output files in the target languages C++, Java, Objective-C,
 * and renders them to the DOM with syntax highlighting.
 * @param {string} idlContent
 * @param {string} configContent
 * @returns {Promise<void>}
 */
async function generate(idlContent, configContent) {
    let pyodide = await pyodideReadyPromise;
    reportStatus("parsing & generating...")
    pyodide.FS.writeFile("/input.djinni", idlContent, { encoding: "utf8" });
    pyodide.FS.writeFile("/pydjinni.yaml", configContent, { encoding: "utf8" });
    try {
        const result = pyodide.runPython(`
            import shutil
            import js
            from pydjinni import API
            from pathlib import Path
            from pydjinni.exceptions import ApplicationException, ConfigurationException
            from pydjinni.parser.parser import IdlParser
            from pygments import highlight
            from pygments.lexers import CppLexer, JavaLexer, YamlLexer
            from pygments.lexers.objective import ObjectiveCLexer
            from pygments.formatters import HtmlFormatter

            result = ""

            cpp_header_path = Path("/out/cpp/header")
            cpp_html_path = Path("/out/cpp/html")
            java_source_path = Path("/out/java/source")
            java_html_path = Path("/out/java/html")
            objc_source_path = Path("/out/objc/header")
            objc_html_path = Path("/out/objc/html")
            cppcli_source_path = Path("/out/cppcli/header")
            cppcli_html_path = Path("/out/cppcli/html")
            yaml_source_path = Path("/out/yaml")
            yaml_html_path = Path("/out/yaml/html")
            try:
                api = API().configure("/pydjinni.yaml", options={
                    "generate": {
                        "support_lib_sources": False,
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
                        },
                        "objc": {
                            "out": {
                                "header": "/out/objc/header",
                                "source": "/out/objc/source"
                            }
                        },
                        "objcpp": {
                            "out": {
                                "header": "/out/objcpp/header",
                                "source": "/out/objcpp/source"
                            }
                        },
                        "cppcli": {
                            "out": {
                                "header": "/out/cppcli/header",
                                "source": "/out/cppcli/source"
                            }
                        },
                        "yaml": {
                            "out": "/out/yaml"
                        }
                    }
                }).parse("/input.djinni").generate("cpp", clean=True).generate("java", clean=True).generate("objc", clean=True).generate("cppcli", clean=True).generate("yaml", clean=True)
                
                def render_generated_files(source_path: Path, target_path: Path, lexer, id: str):
                    files = source_path.rglob("*")
                    target_element = js.document.getElementById(id)
                    target_element.innerHTML = ""
                    for file in files:
                        if file.is_file():
                            relative_file = str(file.relative_to(source_path))
                            output_content = highlight(file.read_text(), lexer, HtmlFormatter())
                            container = js.document.createElement("div")
                            container.className = "output_container"
                            title = js.document.createElement("div")
                            title.className = "filename"
                            title.innerText = relative_file
                            code = js.document.createElement("code")
                            code.innerHTML = output_content;
                            container.appendChild(title)
                            container.appendChild(code)
                            target_element.appendChild(container)
                            

                render_generated_files(cpp_header_path, cpp_html_path, CppLexer(), id="generated_cpp_files")
                render_generated_files(java_source_path, java_html_path, JavaLexer(), id="generated_java_files")
                render_generated_files(objc_source_path, objc_html_path, ObjectiveCLexer(), id="generated_objc_files")
                render_generated_files(cppcli_source_path, cppcli_html_path, CppLexer(), id="generated_cppcli_files")
                render_generated_files(yaml_source_path, yaml_html_path, YamlLexer(), id="generated_yaml_files")
                result = (0, "success")
            except IdlParser.ParsingException as e:
                result = (1, f"{e}")
            except ConfigurationException as e:
                result = (2, f"{e}")
            except ApplicationException as e:
                result = (3, f"{e}")
            result
        `);
        const resultCode = result.get(0);
        const resultMessage = result.get(1);
        if(resultCode === 1) { // parsing error
            reportError(resultMessage);
            idlInputElement.className = "error"
        } else if(resultCode === 2) { //configuration error
            reportError(resultMessage);
            configInputElement.className = "error"
        } else if(resultCode === 3) { // other error
            reportError(resultMessage);
        } else {
            idlInputElement.className = ""
            configInputElement.className = ""
            reportSuccess(result.get(1));
        }
    } catch (err) {
        reportError(err)
    }
}

/**
 * Initializes the Demo.
 * - Downloads the required Pyodide library
 * - Queries for a list of commonly used elements
 * - Initializes the Pyodide environment
 * - reads the current IDL and config file from the `sessionStorage` if it exists.
 * - sets up the textarea elements
 * - triggers generation
 *
 * For loading the Pyodide library, a weird workaround has to be done: This function creates a script element that
 * then in turn will load the referenced script and reports once the loading is finished.
 * This is required because "instant loading" in "Material for MkDocs" loads the page a bit weird: It will just replace
 * the page content dynamically, which is why the `window.onload` trigger can not be used to determine if all resources
 * are loaded. It may not be triggered when the user navigates to the page.
 */
function demoInit() {
    const pyodideScript = document.createElement("script");
    // a simple way to set attributes according to me
    Object.assign(pyodideScript, {
        id: "pyodide",
        src: "https://cdn.jsdelivr.net/pyodide/dev/full/pyodide.js",
    });

    let edit_button = document.getElementsByClassName("md-content__button")[0]
    edit_button.innerHTML = ""
    demoOutputElement = document.getElementById("demo_output");
    idlInputElement = document.getElementById("idl_input");
    const richDemoInputElement = document.getElementById("rich_idl_input");
    configInputElement = document.getElementById("config_input");
    const richDemoConfigElement = document.getElementById("rich_config_input");

    // this will be called once the Pyodide library is downloaded.
    pyodideScript.addEventListener("load", () => {
        const version = document.getElementById("pydjinni_version").innerText
        const localFallback = location.hostname === "localhost" || location.hostname === "127.0.0.1"
        if(localFallback) {
            console.info("This demo has been detected to run on 'localhost'. To make it work:")
            console.info("-> Disable CORS restrictions in your browser!")
            console.info("-> run 'python -m build && python -m http.server --directory ./dist 8001' before loading the demo.")
        }

        pyodideReadyPromise = pyodideReadyPromise || main(version, localFallback);

        const idlInput = window.sessionStorage.getItem("idl_input");
        const configInput = window.sessionStorage.getItem("config_input");

        if(idlInput) {
            idlInputElement.value = idlInput;
        }
        if(configInput) {
            configInputElement.value = configInput;
        }
        configureTextarea(idlInputElement, richDemoInputElement, "djinni");
        configureTextarea(configInputElement, richDemoConfigElement, "yaml");
        generate(idlInputElement.value, configInputElement.value);
    });
    // adding the script block to the DOM, telling the browser to load the Pyodide library.
    document.body.appendChild(pyodideScript);
}

demoInit()





