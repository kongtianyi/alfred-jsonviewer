# -*- encoding: utf-8 -*-

import sys
import pyperclip
import json
import re
from enum import Enum
from workflow import Workflow3

PYTHON_JSON_TYPE_MAP = {
    "dict": "object",
    "list": "array",
    "tuple": "array",
    "set": "array",
    "str": "string",
    "unicode": "string",
    "int": "number",
    "float": "number",
    "bool": "bool",
    "NoneType": "null"
}


class QueryType(Enum):
    SIMPLE = 0
    SEARCH = 1


has_item = False


def main(wf):
    query = str(wf.args[0])
    query_type, paths = parse_input(query)

    clipboard_text = pyperclip.paste().encode('utf-8')
    text = parse_text(clipboard_text.strip())

    json_dict = load_json(text)
    if json_dict is None:
        add_item(wf, title="can not read json from clipboard", valid=False)
        wf.send_feedback()
        return

    if query_type == QueryType.SIMPLE:
        add_item(wf, title=text, output=generate_output(load_json(text)), valid=True,
                 subtitle="following rows are key-value pairs of clipboard object")

    for i in range(len(paths)):
        json_dict = load_json(text)
        if not isinstance(json_dict, dict):
            break
        for k in sorted(json_dict.keys()):
            v = json_dict[k]
            if i != len(paths) - 1:
                # 中间的path都是整个的单词
                if k.lower() == paths[i].lower():
                    text = v
                    break
            else:
                # 最后一个path模糊搜索
                if k.lower().find(paths[i].lower()) == -1:
                    continue
                if k.lower() != paths[i].lower():
                    add_item(wf, title=k + get_type_name(v) + ": " + generate_output(v),
                             output=build_predict_output(k, paths),
                             autocomplete=build_autocomplete(k, paths),
                             subtitle="press enter/tab to fill in the search box")
                else:
                    text = v
                    add_item(wf,
                             title=k + get_type_name(v) + ": " + generate_output(v),
                             output=generate_output(v),
                             subtitle="press enter to show in web browser")

    if not has_item:
        add_item(wf, title="path error", valid=False)

    wf.send_feedback()


def get_type_name(item):
    type_str = str(type(item))
    pattern = re.compile("\'(.*?)\'")
    py_type_name = pattern.search(type_str).group()[1:-1]
    return '(' + PYTHON_JSON_TYPE_MAP.get(py_type_name, 'unknown') + ')'


def add_item(wf, title, output=None, subtitle=None, valid=True, autocomplete=None):
    global has_item
    has_item = True
    if subtitle is None:
        subtitle = ""
    wf.add_item(title=title, subtitle=subtitle, arg=output, valid=valid, autocomplete=autocomplete)


def parse_input(key):
    if key.strip() == "":
        return QueryType.SIMPLE, [""]
    return QueryType.SEARCH, key.strip().split('>')


def parse_text(text):
    if text.startswith('\"'):
        # like "{\"a\": 1}"
        return eval(text)
    elif text.startswith("{\\\""):
        # like {\"a\": 1}
        return eval("\"" + text + "\"")
    else:
        # like {"a": 1}
        return text


def load_json(input):
    if type(input) == dict:
        return input
    try:
        json_obj = json.loads(input)
    except Exception as e:
        wf.logger.error(e)
        return None
    return json_obj


def generate_output(param, intent=None):
    if check_if_escape_json_dict(param):
        param = load_json(param)
    if type(param) is not str:
        return json.dumps(param, ensure_ascii=False, indent=intent)
    return param


def check_if_escape_json_dict(data):
    if type(data) not in (str, unicode):
        return False
    if not data.startswith('{'):
        return False
    try:
        json.loads(data)
    except Exception:
        return False
    return True


def build_predict_output(k, paths):
    path = ">".join(paths[:-1])
    if path.strip() != "":
        path = path + ">"
    return "json " + path + k


def build_autocomplete(k, paths):
    path = ">".join(paths[:-1])
    if path.strip() != "":
        path = path + ">"
    return path + k


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
