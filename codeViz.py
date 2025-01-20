from pyflowchart import Flowchart

with open("historyTool_Con.py") as f:
    code = f.read()

fc = Flowchart.from_code(code)
print(fc.flowchart())