import sys
import warnings

if sys.version_info < (3, 11):
    raise RuntimeError("ARL requires Python 3.11 or newer")

# 关闭高权限使用celery警告
warnings.filterwarnings("ignore", category=UserWarning,
                        message="You're running the worker with superuser privileges")
