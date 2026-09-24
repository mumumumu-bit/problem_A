# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Content-addressed, atomic evaluation persistence."""
import hashlib
import json
import os
from pathlib import Path
import tempfile


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class EvaluationCache:
    def __init__(self, directory):
        self.directory = Path(directory) if directory else None
        self.memory = {}

    def get(self, key):
        if key in self.memory:
            return self.memory[key]
        path = self.directory / (key+'.json') if self.directory else None
        if path and path.exists():
            try:
                value = json.loads(path.read_text(encoding='utf-8'))
                if value['key'] == key:
                    self.memory[key] = value['evaluation']
                    return value['evaluation']
            except (ValueError, KeyError):
                return None

    def put(self, key, value):
        self.memory[key] = value
        if self.directory:
            atomic_json(self.directory/(key+'.json'), dict(key=key, evaluation=value))

