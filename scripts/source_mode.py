"""Remove inspection-only source blocks for functional and size builds."""

import fcntl
import re
from contextlib import contextmanager
from pathlib import Path
from build_record import source_state

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "apps/react-native/App.tsx",
    "apps/flutter/lib/main.dart",
    "apps/compose/app/src/main/java/dev/devaxes/catalogue/MainActivity.kt",
]


def stripped(text):
    result = []
    inside = False
    for line in text.splitlines(keepends=True):
        if "CAPTURE_BEGIN" in line:
            assert not inside
            inside = True
        elif "CAPTURE_END" in line:
            assert inside
            inside = False
        elif not inside:
            result.append(line)
    assert not inside
    return "".join(result)


def cut(text, start, end, replacement=""):
    left = text.index(start)
    right = text.index(end, left)
    return text[:left] + replacement + text[right:]


def balanced_end(text, position, opening="(", closing=")"):
    depth, quote, escaped = 0, None, False
    for index in range(position, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in "\"'`":
            quote = char
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError("Unbalanced source region")


def remove_call(text, marker):
    start = text.index(marker)
    end = balanced_end(text, text.index("(", start))
    return text[:start] + text[end:]


def swift_capture_stripped(text):
    result, inside = [], False
    for line in text.splitlines(keepends=True):
        if line.strip() == "#if CAPTURE":
            inside = True
        elif inside and line.strip() == "#endif":
            inside = False
        elif not inside:
            result.append(line)
    assert not inside
    return "".join(result)


def projected(text, stack, variant, capture=False):
    if capture:
        if variant != "A":
            raise ValueError("Only A has an inspection timeline")
        return text
    text = swift_capture_stripped(text) if stack == "swift" else stripped(text)
    if variant != "S":
        return text
    if stack == "react-native":
        text = re.sub(r"^type Rect =.*\n", "", text, flags=re.M)
        text = cut(text, "  const [source, setSource]", "  const [width")
        text = cut(text, "  const origin =", "  const write =")
        text = text.replace("let [progress, time] = useProgress", "useProgress")
        # Retain navigation completion and input guards, without source geometry.
        text = cut(
            text,
            "    imageRefs.current[product.id]?.measureInWindow",
            "  const data =",
            "    setSelected(product);\n    setTarget(1);\n  };\n",
        )
        text = cut(text, "  const sourceExists =", "  const star =")
        text = text.replace("        ref={root}\n", "")
        text = cut(text, "          root.current?.measureInWindow", "        }}")
        text = re.sub(r"\s+ref=\{v => \{\s+imageRefs.current\[p.id\] = v;\s+\}\}", "", text)
        text = cut(
            text,
            "              style={{\n                position: 'absolute',",
            "            />",
            "              style={{position: 'absolute', left: 0, top: 52, width, height: 280, borderRadius: 0}}\n",
        )
        text = text.replace("opacity: progress", "opacity: 1")
        text = text.replace("Math.max(0, (time - 0.35) / 0.65)", "1")
        assert "measureInWindow" not in text and "sourceExists" not in text
    elif stack == "flutter":
        text = text.replace("\n    with SingleTickerProviderStateMixin", "")
        for line in [
            "  final rootKey = GlobalKey();\n",
            "  final imageKeys = <String, GlobalKey>{};\n",
            "  Rect source = Rect.zero;\n",
        ]:
            text = text.replace(line, "")
        text = text.replace("Progress(vsync: this)", "Progress()")
        text = cut(text, "    final image =", "    setState(() {")
        text = re.sub(r"^\s*var visual(?:Progress|Time) =.*\n", "", text, flags=re.M)
        text = re.sub(r"^\s*final exists =.*\n", "", text, flags=re.M)
        text = cut(text, "              final destination =", "              return Stack(")
        text = text.replace("                key: rootKey,\n", "")
        text = re.sub(r"\s*final key = imageKeys.putIfAbsent\([\s\S]*?\);", "", text)
        text = re.sub(r"^\s*key: key,\n", "", text, flags=re.M)
        start = text.index("                    Positioned.fromRect(")
        end = balanced_end(text, text.index("(", start))
        text = (
            text[:start]
            + "                    Positioned(left: 0, top: 52, width: constraints.maxWidth, height: 280, child: photo(p, radius: 0))"
            + text[end:]
        )
        text = text.replace("Colors.white.withValues(alpha: visualProgress)", "Colors.white")
        text = text.replace("((visualTime - 0.35) / 0.65).clamp(0, 1)", "1")
        assert (
            "Rect.lerp" not in text
            and "RenderBox" not in text
            and "SingleTickerProvider" not in text
        )
    elif stack == "compose":
        for name in ["source", "origin", "density", "positions"]:
            text = re.sub(r"^\s*(?:var|val) " + name + r"\b[^\n]*\n", "", text, flags=re.M)
        for name in ["Rect", "Offset", "LocalDensity", "boundsInRoot", "onGloballyPositioned"]:
            text = re.sub(r"^import .*\." + name + r"\n", "", text, flags=re.M)
        text = text.replace("var (progress, time) =\n                navProgress", "navProgress")
        text = re.sub(r"\.onGloballyPositioned\s*\{[^}]*\}", "", text)
        text = re.sub(r"^\s*source = positions[^\n]*\n", "", text, flags=re.M)
        text = cut(
            text,
            "                        val exists =",
            "                        Column(Modifier.fillMaxWidth()",
            "                        Box(Modifier.fillMaxSize().background(Color.White).clickable {})\n                        Photo(item, 0f, Modifier.offset(0.dp, 52.dp).size(width, 280.dp))\n",
        )
        text = text.replace(".alpha(((time - 0.35f) / 0.65f).coerceIn(0f, 1f))", "")
        assert "boundsInRoot" not in text and "fun mix" not in text
    elif stack == "swift":
        if "private struct ImagePositions" in text:
            start = text.index("private struct ImagePositions")
            end = balanced_end(text, text.index("{", start), "{", "}")
            text = text[:start] + text[end:]
        if "private func imageRect" in text:
            start = text.index("    private func imageRect")
            end = balanced_end(text, text.index("{", start), "{", "}")
            text = text[:start] + text[end:]
            start = text.index("GeometryReader { cell in")
            opening = text.index("{", start)
            end = balanced_end(text, opening, "{", "}")
            body = text[start + len("GeometryReader { cell in") : end - 1]
            text = text[:start] + body + text[end:]
            text = re.sub(r"open\(p,\s*rect: imageRect\(cell,\s*width\)\)", "open(p)", text)
            text = text.replace(
                "private func open(_ p: Product, rect: CGRect)", "private func open(_ p: Product)"
            )
        text = re.sub(
            r"^\s*@State private var (?:source|positions)\b[^\n]*\n", "", text, flags=re.M
        )
        text = text.replace(
            "guard !busy, selected == nil, let rect = positions[p.id] else",
            "guard !busy, selected == nil else",
        )
        text = text.replace("        source = rect\n", "")
        text = cut(text, "    private var visualProgress:", "    var body: some View")
        marker = ".background(\n                                        GeometryReader { image"
        if marker in text:
            text = remove_call(text, marker)
        text = cut(
            text,
            "                    let exists =",
            "                    VStack(alignment: .leading, spacing: 0)",
            "                    Color.white.ignoresSafeArea()\n                    photo(p, width: geometry.size.width, height: 280, radius: 0).offset(x: 0, y: 52)\n",
        )
        text = text.replace(".opacity(max(0, (visualTime - 0.35) / 0.65))", "")
        text = text.replace('.coordinateSpace(name: "catalogue")', "")
        if ".onPreferenceChange(ImagePositions.self)" in text:
            start = text.index(".onPreferenceChange(ImagePositions.self)")
            end = balanced_end(text, text.index("{", start), "{", "}")
            text = text[:start] + text[end:]
        assert "ImagePositions" not in text and "source.minX" not in text
    else:
        raise ValueError(stack)
    return text


@contextmanager
def sources(capture=False, variant="A"):
    (ROOT / ".work").mkdir(exist_ok=True)
    lock = (ROOT / ".work/source.lock").open("w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    originals = {ROOT / name: (ROOT / name).read_text() for name in FILES if (ROOT / name).exists()}
    state = source_state()
    try:
        for path, text in originals.items():
            stack = (
                "react-native"
                if path.name == "App.tsx"
                else "flutter"
                if path.suffix == ".dart"
                else "compose"
            )
            path.write_text(projected(text, stack, variant, capture))
        yield state
    finally:
        for path, text in originals.items():
            path.write_text(text)
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
