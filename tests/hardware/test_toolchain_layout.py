import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"hardware/pruebas"))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"hardware/pruebas/t06"))
from toolchain import select_runtime_root

class LayoutTests(unittest.TestCase):
    def test_split_runtime_and_host_rejection(self):
        with tempfile.TemporaryDirectory() as d:
            host=Path(d)/"usr"
            ti=host/"share/ti/cgt-pru"
            for root in (host,ti):
                for item in ("include/stdint.h","lib/libc.a"):
                    p=root/item
                    p.parent.mkdir(parents=True,exist_ok=True)
                    p.write_text("")
            self.assertIsNone(select_runtime_root([host,ti]))
            (ti/"lib/rtspruv3_le.lib").write_text("")
            self.assertEqual(select_runtime_root([host,ti]),ti)
            (ti/"include/stdint.h").unlink()
            self.assertIsNone(select_runtime_root([host,ti]))

    def test_standard_layout(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for item in ("include/stdint.h","lib/libc.a","lib/rtspruv3_le.lib"):
                p=root/item
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text("")
            self.assertEqual(select_runtime_root([root]),root)

if __name__=="__main__": unittest.main()
