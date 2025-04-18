import os
import sys
import pytest
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# デバッグ時のパス問題を解決するための設定
os.environ["PYTHONPATH"] = str(root_dir) 

# デバッグモードの設定
# 1. 環境変数から判定
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# 2. コマンドライン引数から判定
#if '--debug' in sys.argv:
#    DEBUG = True

# 3. VSCodeのデバッガーから判定
# VSCodeのデバッガーが実行されている場合、sys.gettrace()はNone以外を返す
#if sys.gettrace() is not None:
#    DEBUG = True