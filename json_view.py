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
    UNFOLD = 2


def main(wf):
    query = str(wf.args[0])
    query_type, paths = parse_input(query)

    clipboard_text = str(pyperclip.paste())
    text = parse_text(clipboard_text.strip())

    json_dict = load_json(text)
    if json_dict is None:
        wf.add_item(title="Can not read json from clipboard", valid=False)
        wf.send_feedback()
        return

    if query_type == QueryType.SIMPLE:
        wf.add_item(title=text, arg=generate_output(load_json(text)), valid=True,
                    subtitle="Followed raw are key value of clipboard JSON")

    items = []
    for i in range(len(paths)):
        items = []
        for k in sorted(json_dict.keys()):
            v = json_dict[k]
            if i != len(paths) - 1:
                # 中间的path都是整个的单词
                if k.lower() == paths[i].lower():
                    text = v
                    break
            else:
                if query_type == QueryType.SEARCH or query_type == QueryType.SIMPLE:
                    # 最后一个path模糊搜索
                    if k.lower().find(paths[i].lower()) == -1:
                        continue
                    items.append((k, v))
                elif query_type == QueryType.UNFOLD:
                    # 最后一个path展开
                    if k.lower() == paths[i]:
                        if type(v) is dict:
                            for sk in sorted(v.keys()):
                                items.append((sk, v[sk]))
                        elif check_if_escape_json_dict(v):
                            unfold_json_dict = load_json(v)
                            for sk in sorted(unfold_json_dict.keys()):
                                items.append((sk, unfold_json_dict[sk]))
                        else:
                            items.append((k, v))

    if len(items) == 0:
        add_item(wf, "error", "path error")

    for item in items:
        paths = query.split('>')[:-1]
        paths.append(str(item[0]))
        auto = ">".join(paths)
        add_item(wf, item[0] + get_type_name(item[1]), generate_output(item[1]), generate_output(item[1], 4), auto)

    wf.send_feedback()


def get_type_name(item):
    type_str = str(type(item))
    pattern = re.compile("\'(.*?)\'")
    py_type_name = pattern.search(type_str).group()[1:-1]
    return '(' + PYTHON_JSON_TYPE_MAP.get(py_type_name, 'unknown') + ')'


def add_item(wf, prefix, result, output=None, auto=None):
    title = '{}: {}'.format(prefix, result)
    wf.add_item(title=title, arg=output, valid=True, autocomplete=auto)


def parse_input(key):
    if key.strip() == "":
        return QueryType.SIMPLE, [""]
    if key.endswith('>'):
        return QueryType.UNFOLD, key.strip().split('>')[:-1]
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


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
