import pytest
import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# デバッグ時のパス問題を解決するための設定
os.environ["PYTHONPATH"] = str(root_dir) 