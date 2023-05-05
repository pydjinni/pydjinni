from junitparser import JUnitXml



xml = JUnitXml.fromfile("pytest-report.xml")
output = ""
type = "pytest"

for suite in xml:
    output += f"# {suite.name}\n\n"
    output += "| Errors | Failure | Skipped | Tests | Time |\n" \
              "|--------|---------|---------|-------|------|\n" \
              f"| {suite.errors} | {suite.failures} | {suite.skipped} | {suite.tests} | {suite.time}s |\n\n"
    classname = ""
    matrix_name = ""
    for case in suite:
        if type == "pytest":
            icon = "✅" if case.is_passed else "❌"
            if classname != case.classname:
                classname = case.classname
                output += f"\n## {classname}\n\n"
            if case.name.endswith("]"):
                split = case.name.split("[")
                new_matrix_name = split[0]
                matrix_param = split[1][:-1]
                if matrix_name != new_matrix_name:
                    matrix_name = new_matrix_name
                    output += f"- {matrix_name}\n"
                output += f"    - {icon} {matrix_param} ({case.time}s)\n"
            else:
                output += f"- {icon} {case.name} ({case.time}s)\n"
            if not case.is_passed:
                for entry in case.result:
                    output += "      ```\n"
                    output += entry.text
                    output += "      ```\n"

print(output)
