"""One-off: extract assets and sample colours from the pre-theory-deck pptx.

Run from repo root: python3 presentation/build/extract_assets.py
"""
import io
import re
import shutil
import subprocess
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "presentation" / "assets"
TAG = "pre-theory-deck"


def slide_image(z, n, index=0):
    rels = z.read(f"ppt/slides/_rels/slide{n}.xml.rels").decode()
    targets = re.findall(r'Target="\.\./media/([^"]+)"', rels)
    return targets[index]


def main():
    data = subprocess.check_output(
        ["git", "show", f"{TAG}:presentation/speckit-workshop.pptx"], cwd=ROOT)
    z = zipfile.ZipFile(io.BytesIO(data))
    OUT.mkdir(parents=True, exist_ok=True)

    # slide 1 rels: rId2 is the full-slide background PNG (image1.png)
    bg = Path(slide_image(z, 1, 1)).name
    (OUT / "bg.png").write_bytes(z.read(f"ppt/media/{bg}"))
    # slide 22: rId3 (image220.png) is the blank dark code-card
    card = slide_image(z, 22, 1)
    (OUT / "code-card.png").write_bytes(z.read(f"ppt/media/{Path(card).name}"))
    # photos: same hardware images as docs/images
    for kind in ("ok", "warning"):
        shutil.copy(ROOT / "docs/images" / f"hardware-dht22-{kind}.jpg",
                    OUT / f"photo-{kind}.jpg")

    counts = Counter()
    for name in z.namelist():
        if re.match(r"ppt/slides/slide\d+\.xml$", name):
            counts.update(re.findall(r'srgbClr val="(\w+)"', z.read(name).decode()))
    print("srgbClr frequency:", counts.most_common(20))
    for label, img in (("bg.png", "bg.png"), ("code-card.png", "code-card.png")):
        im = Image.open(OUT / img).convert("RGB")
        print(label, "pixel(5,5)/center:", "%02X%02X%02X" % im.getpixel((5, 5)),
              "%02X%02X%02X" % im.getpixel((im.width // 2, im.height // 2)))
    card2 = Image.open(io.BytesIO(z.read("ppt/media/image227.png"))).convert("RGB")
    print("surface card (slide 23) pixel(5,300): %02X%02X%02X" % card2.getpixel((5, 300)))


if __name__ == "__main__":
    main()
