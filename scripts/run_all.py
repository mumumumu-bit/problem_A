# 本程序及代码是在人工智能工具辅助下完成的。
# AI工具：
# 模型/版本：
# 开发机构：
# 版本发布日期：
"""Repository-local entry point; defaults to six development cases, never all 100."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from npu_scheduler.cli import main

if __name__=='__main__':
    main(['benchmark',*sys.argv[1:]])
