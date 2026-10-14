"""Copy canonical assets and reject any changed source checksum."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

def main():
    shared = ROOT / "shared"
    for relative, expected in json.loads((shared / "manifest.json").read_text()).items():
        assert hashlib.sha256((shared / relative).read_bytes()).hexdigest() == expected, relative
    for destination in [ROOT / "apps/flutter/assets", ROOT / "apps/react-native/assets",
                        ROOT / "apps/compose/app/src/main/assets"]:
        shutil.copytree(shared / "images", destination / "images", dirs_exist_ok=True)
        shutil.copy2(shared / "products.json", destination / "products.json")
    images = sorted((shared / "images").glob("*.png"))
    text = "export const images: Record<string, number> = {\n"
    text += "".join(f"  '{p.stem}': require('../assets/images/{p.name}'),\n" for p in images)
    text += "};\n"
    (ROOT / "apps/react-native/src/images.ts").parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "apps/react-native/src/images.ts").write_text(text)

if __name__ == "__main__":
    main()
