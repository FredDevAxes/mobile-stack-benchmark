"""Validate dataset invariants independently of each implementation."""

from pathlib import Path
import json
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AssetsTest(unittest.TestCase):
    def test_fixed_catalogue(self):
        data = json.loads((ROOT / "shared/products.json").read_text())
        self.assertEqual(len(data), 200)
        self.assertEqual([p["id"] for p in data], [f"p{i:03}" for i in range(1, 201)])
        self.assertEqual(len({p["imageKey"] for p in data}), 20)
        for p in data:
            self.assertGreater(p["priceCents"], 0)
            image = (ROOT / f"shared/images/{p['imageKey']}.png").read_bytes()
            self.assertEqual(struct.unpack("!II", image[16:24]), (640, 400))

    def test_source_checksums(self):
        from assets import main

        main()


if __name__ == "__main__":
    unittest.main()
