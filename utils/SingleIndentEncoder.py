import json


class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        # 第一层缩进
        first_level_indent = "  "
        # 嵌套结构紧凑
        if isinstance(obj, dict):
            items = [
                f'"{key}": {json.dumps(value, separators=(",", ":"), ensure_ascii=False)}'
                for key, value in obj.items()
            ]
            return "{\n" + first_level_indent + (",\n" + first_level_indent).join(items) + "\n}"
        return json.dumps(obj)