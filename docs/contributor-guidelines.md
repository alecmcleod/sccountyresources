Contributor guidelines for developers
---
* Author headers at the beginning of each class file. For example,
```
"""
    Author: XXX XXX
    Created for SCCR, 2018
"""
```
* CamelCase variables only (e.g. `int randomFlag = False;`)
* Descriptive variable names **PLEASE**
* One class per file, and no functions left outside of a given class
* Block comments at the beginning of each class, describing its purpose
* Block comments/docstrings at the beginning of each function. For example,
```
"""
    The purpose of this function is to blah blah blah...
    :param num: The number that does this
    :param name: The name that does that
    :return variableName, an integer that serves some random purpose...
"""
func abc(self, num, name):
    [...]
    return variableName
```
* An interface class for each class file where appropriate, to hide the abstraction from other developers on the project.
* Comment *heavily* (preferrably every three lines)
* Make your code modular
* Unit tests with at least 80% code coverage at any given time!
* Use logging statements instead of print statements for debugging purposes
* No single method should be longer than a screen's length (simply put, your methods should be short and sweet)
* Convention for naming *all* Python files: `SCCR[...].py`. For example, `SCCRRESTfulAPI.py`, or `SCCRMessageQueue.py`. The name of the actual class should correspond with the name of the file itself. All Markdown, HTML, and CSS files are exempt from this naming convention.
* Any documents under the `docs/` directory should be Markdown or LaTeX only.
