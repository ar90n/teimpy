import sys
from pathlib import Path

src_root_path = (Path(__file__).parent.parent / "src").absolute()
sys.path.append(str(src_root_path))
