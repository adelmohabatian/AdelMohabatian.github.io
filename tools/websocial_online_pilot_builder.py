#!/usr/bin/env python3
"""WebSocial online-editor pilot builder.

Reads the published ZIP as an immutable baseline, overlays *public-safe* carpet
metadata from Pages CMS, validates links, and emits a preview ZIP. It never
connects to GitHub and never publishes without the established deploy workflow.

In production, omit --include-drafts. A GitHub PR/merge approval is an additional
necessary editorial gate; status labels are not authorization controls.
"""
import argparse
import html
import io
import json
import re
import sys
import zipfile
from pathlib import Path

MAX_ENTRIES = 500
MAX_EXTRACTED_BYTES = 150 * 1024 * 1024
MAX_FILE_BYTES = 30 * 1024 * 1024
MAX_ZIP_BYTES = 24_000_000
ALLOWED_STATUS = {"draft", "review", "published"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,69}$")
MEDIA_PREFIX = "/assets/pilot/carpet/"
GRAPH_ANCHOR = "\n  ],\n  edges: ["


def reject(message):
    raise ValueError(message)


def safe_name(name):
    if not name or name.startswith("/") or "\\" in name or "\x00" in name:
        reject(f"Unsafe archive path: {name!r}")
    parts = name.split("/")
    if any(p in ("", ".", "..") for p in parts):
        reject(f"Unsafe archive path: {name!r}")
    return name


def validate_id(value, field):
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        reject(f"{field}: use lowercase Latin letters, numbers and hyphens (2-70 characters)")
    return value


def validate_status(entry):
    status = entry.get("status", "draft")
    if status not in ALLOWED_STATUS:
        reject(f"Unknown editorial status: {status!r}")
    return status


def valid_public_path(value):
    if not isinstance(value, str) or not value.startswith("/assets/"):
        reject(f"Photo path must start with /assets/: {value!r}")
    name = value.lstrip("/")
    safe_name(name)
    if Path(name).suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        reject(f"Unsupported image extension: {value!r}")
    return name


def load_base(path):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            reject("The baseline ZIP is corrupt")
        files = {}
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            name = safe_name(entry.filename)
            if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                reject(f"Refusing symlink: {name}")
            if name in files:
                reject(f"Duplicate ZIP member: {name}")
            files[name] = archive.read(entry)
    if "index.html" not in files or "assets/data/photo-carpet-v51.json" not in files or "explore/graph-data-v01.js" not in files:
        reject("Baseline does not include the expected WebSocial v6.0 files")
    return files


def materialize_images(files, media_dir, needed_refs):
    """Public-safe upload media is converted to compact WebP, no raw source saved."""
    if not media_dir.exists():
        return {}
    try:
        from PIL import Image, ImageOps, UnidentifiedImageError
    except ImportError:
        reject("Install Pillow to optimize uploaded photos: python -m pip install Pillow")
    result = {}
    for ref in sorted(needed_refs):
        if not ref.startswith(MEDIA_PREFIX):
            reject(f"Unrecognized CMS media URL: {ref}")
        filename = ref.removeprefix(MEDIA_PREFIX)
        if "/" in filename or filename.startswith(".") or not filename:
            reject(f"Invalid CMS media filename: {filename}")
        path = media_dir / filename
        if not path.is_file():
            reject(f"CMS media file missing from repository: {filename}")
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            reject(f"Unsupported upload (only images): {path.name}")
        if path.stat().st_size > 12 * 1024 * 1024:
            reject(f"Uploaded photo is larger than 12MB: {path.name}")
        try:
            with Image.open(path) as im:
                im = ImageOps.exif_transpose(im)
                if im.width * im.height > 35_000_000:
                    reject(f"Too many pixels in: {path.name}")
                if im.mode not in ("RGB", "RGBA"):
                    im = im.convert("RGB")
                im.thumbnail((1500, 1500), Image.Resampling.LANCZOS)
                if im.mode == "RGBA":
                    bg = Image.new("RGB", im.size, (246, 246, 244))
                    bg.paste(im, mask=im.getchannel("A"))
                    im = bg
                buf = io.BytesIO()
                im.save(buf, format="WEBP", quality=72, method=5)
        except Exception as exc:
            reject(f"Invalid image {path.name}: {exc}")
        # Resolve original CMS reference to optimized public WebP path.
        out_name = f"assets/pilot/carpet/{path.stem}.webp"
        if out_name in files:
            reject(f"Output media collides with existing file: {out_name}")
        files[out_name] = buf.getvalue()
        result[ref] = "/" + out_name
    return result


def resolve_image(src, original_files, replacements):
    if not src:
        return ""
    name = valid_public_path(src)
    if src in replacements:
        return replacements[src]
    if src.startswith(MEDIA_PREFIX):
        # Pages CMS can send an already-optimized WebP URL.
        candidate = MEDIA_PREFIX + Path(src).stem + ".webp"
        if candidate.lstrip("/") in original_files:
            return candidate
        reject(f"Uploaded media missing from content/pilot/media: {src}")
    if name not in original_files:
        reject(f"Photo URL does not exist in baseline: {src}")
    return src


def bilingual(text, lang):
    return html.escape(str(text or ""), quote=True)


def make_note_page(note, image_url, preview):
    title_fa = bilingual(note["title_fa"], "fa")
    title_en = bilingual(note["title_en"], "en")
    summary_fa = bilingual(note["summary_fa"], "fa").replace("\n", "<br>")
    summary_en = bilingual(note["summary_en"], "en").replace("\n", "<br>")
    pic = f'<figure><img loading="lazy" src="{html.escape(image_url,quote=True)}" alt=""/></figure>' if image_url else ""
    badge = '<p class="watermark">PREVIEW ONLY · پیش‌نمایش انتشارنشده</p>' if preview else ""
    return f'''<!doctype html><html lang="en" dir="ltr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title data-title-fa="{title_fa} | عادل محبتیان" data-title-en="{title_en} | Adel Mohabatian">{title_en} | Adel Mohabatian</title>
<link rel="stylesheet" href="/assets/css/pages.css"><link rel="stylesheet" href="/assets/css/ws-typography-v56.css">
<style>body{{background:#f1f5f5;color:#24353d;margin:0;font:17px/1.85 system-ui,sans-serif}}header,footer{{border-bottom:1px solid #d3dfe1;padding:18px 6vw}}main{{max-width:950px;margin:50px auto;padding:0 26px 80px}}h1{{font-size:clamp(28px,4vw,43px);line-height:1.35}}.lead{{font-size:18px;line-height:1.9;max-width:780px}}figure{{margin:26px 0}}figure img{{width:100%;max-height:540px;object-fit:contain;border-radius:8px}}.back{{color:#406477;text-underline-offset:4px}}.watermark{{font-weight:800;color:#a34f30;background:#fff0e5;padding:10px}}[dir=rtl]{{text-align:right}}</style>
</head><body><header><a href="/">ADEL MOHABATIAN</a> · <a href="/research/carpet/" data-fa="پژوهش فرش تبریز" data-en="Tabriz carpet research">Tabriz carpet research</a></header>
<main>{badge}<small data-fa="یادداشت مرتبط با پژوهش" data-en="Research-related note">Research-related note</small>
<h1 data-fa="{title_fa}" data-en="{title_en}">{title_en}</h1>{pic}
<p class="lead" data-fa="{summary_fa}" data-en="{summary_en}">{summary_en}</p>
<a class="back" href="/explore/?focus=carpet" data-fa="مشاهده ارتباطات در گراف" data-en="Explore relationships in graph">Explore relationships in graph</a></main>
<footer>© Adel Mohabatian · WebSocial</footer>
<script defer src="/assets/js/language.js"></script></body></html>'''.encode("utf-8")


def update_carpet_page(files, notes, preview):
    if not notes:
        return
    name = "research/carpet/index.html"
    source = files[name].decode("utf-8")
    start = '<section id="ws-editorial-pilot" class="section" aria-label="Field notes from the online studio"><h2><span data-fa="یادداشت‌های مرتبط" data-en="Related field notes">Related field notes</span></h2>'
    for note in notes:
        nid = html.escape(note["id"], quote=True)
        ftitle = html.escape(note["title_fa"], quote=True)
        etitle = html.escape(note["title_en"], quote=True)
        start += f'<p><a href="/research/carpet/notes/{nid}/"><span data-fa="{ftitle}" data-en="{etitle}">{etitle}</span></a></p>'
    start += "</section>"
    if "</main>" not in source:
        reject("Could not locate the insertion point in research/carpet/index.html")
    source = source.replace("</main>", start + "</main>", 1)
    files[name] = source.encode("utf-8")


def update_graph(files, notes, preview):
    if not notes:
        return
    name = "explore/graph-data-v01.js"
    graph = files[name].decode("utf-8")
    marker = GRAPH_ANCHOR
    if marker not in graph or "\n  ]\n};" not in graph:
        reject("Unexpected graph-data JS structure")
    known_ids = set(re.findall(r"\bid:'([^']+)'", graph))
    added_nodes = []
    added_edges = []
    for note in notes:
        uid = "carpet-note-" + note["id"]
        if uid in known_ids:
            reject(f"Duplicate graph node ID: {uid}")
        known_ids.add(uid)
        fa = note["title_fa"] + (" (پیش‌نمایش)" if preview else "")
        en = note["title_en"] + (" (Preview)" if preview else "")
        obj = {"id": uid, "type": "story", "title": {"fa": fa, "en": en}, "description": {"fa": note["summary_fa"], "en": note["summary_en"]}, "url": "/research/carpet/notes/" + note["id"] + "/"}
        added_nodes.append("    " + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/"))
        added_edges.append("    " + json.dumps({"source": "carpet", "target": uid}, ensure_ascii=False))
        related = note.get("related_node", "")
        if related and related != "carpet":
            if related not in {"carpetphotos"}:
                reject(f"Unauthorized link target: {related!r}")
            added_edges.append("    " + json.dumps({"source": uid, "target": related}, ensure_ascii=False))
    graph = graph.replace(marker, ",\n" + ",\n".join(added_nodes) + marker, 1)
    end = "\n  ]\n};"
    graph = graph.replace(end, ",\n" + ",\n".join(added_edges) + end, 1)
    files[name] = graph.encode("utf-8")


def write_zip(files, path):
    if len(files) > MAX_ENTRIES:
        reject(f"Too many entries: {len(files)} (max {MAX_ENTRIES})")
    uncompressed = sum(len(v) for v in files.values())
    if uncompressed > MAX_EXTRACTED_BYTES:
        reject(f"Too much uncompressed content: {uncompressed}")
    for name, data in files.items():
        safe_name(name)
        if len(data) > MAX_FILE_BYTES:
            reject(f"File exceeds 30 MB limit: {name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
        for name, data in sorted(files.items()):
            archive.writestr(name, data)
    if path.stat().st_size > MAX_ZIP_BYTES:
        path.unlink(missing_ok=True)
        reject("Output is over 24MB. Optimize/remove public pilot uploads before retrying.")
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            reject("Invalid final ZIP")
    return path.stat().st_size, uncompressed


def build(args):
    data = json.loads(args.data.read_text(encoding="utf-8"))
    if data.get("project_id") != "carpet":
        reject("Pilot is restricted to project_id=carpet")
    files = load_base(args.base_zip)
    # Critical: only images actually used in the selected output may be copied.
    # This prevents unpublished/draft uploads leaking into a public ZIP.
    needed_refs = set()
    for kind in ("photos", "notes"):
        for item in data.get(kind, []):
            status = validate_status(item)
            if status != "published" and not args.include_drafts:
                continue
            ref = (item.get("image") or (item.get("src") if kind == "photos" else "")) or ""
            if ref.startswith(MEDIA_PREFIX):
                needed_refs.add(ref)
    new_media = materialize_images(files, args.media_dir, needed_refs)
    gallery = json.loads(files["assets/data/photo-carpet-v51.json"].decode("utf-8"))
    by_src = {item["src"]: item for item in gallery}
    chosen = []
    seen_ids = set()
    for photo in data.get("photos", []):
        pid = validate_id(photo.get("id"), "photo.id")
        if pid in seen_ids:
            reject(f"Duplicate photo id: {pid}")
        seen_ids.add(pid)
        status = validate_status(photo)
        if status != "published" and not args.include_drafts:
            continue
        src = resolve_image(photo.get("image") or photo.get("src"), files, new_media)
        if not src:
            reject(f"Photo {pid} has no source")
        if not photo.get("title_fa") or not photo.get("title_en"):
            reject(f"Photo {pid} is missing titles")
        record = {
            "src": src,
            "fa": str(photo["title_fa"]),
            "en": str(photo["title_en"]),
            "description_fa": str(photo.get("description_fa", "")),
            "description_en": str(photo.get("description_en", "")),
            "alt_fa": str(photo.get("alt_fa") or photo["title_fa"]),
            "alt_en": str(photo.get("alt_en") or photo["title_en"]),
        }
        if src in by_src:
            by_src[src].update(record)
        else:
            gallery.append(record)
            by_src[src] = record
        chosen.append(pid)
    files["assets/data/photo-carpet-v51.json"] = json.dumps(gallery, ensure_ascii=False, indent=2).encode("utf-8")
    notes = []
    seen_note_ids = set()
    for note in data.get("notes", []):
        nid = validate_id(note.get("id"), "note.id")
        if nid in seen_note_ids:
            reject(f"Duplicate note id: {nid}")
        seen_note_ids.add(nid)
        status = validate_status(note)
        if status != "published" and not args.include_drafts:
            continue
        for key in ["title_fa", "title_en", "summary_fa", "summary_en"]:
            if not isinstance(note.get(key), str) or not note[key].strip():
                reject(f"Note {nid} requires {key}")
        image_url = resolve_image(note.get("image", ""), files, new_media)
        url = f"research/carpet/notes/{nid}/index.html"
        if url in files:
            reject(f"Refusing to overwrite pre-existing note page {url}")
        files[url] = make_note_page(note, image_url, args.include_drafts)
        notes.append(note)
    update_carpet_page(files, notes, args.include_drafts)
    update_graph(files, notes, args.include_drafts)
    size, uncompressed = write_zip(files, args.output)
    print(json.dumps({"output": str(args.output), "zip_bytes": size, "uncompressed_bytes": uncompressed, "entries": len(files), "gallery_count": len(gallery), "edited_photo_ids": chosen, "note_count": len(notes), "preview_includes_drafts": args.include_drafts}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-zip", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--media-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--include-drafts", action="store_true", help="REVIEW ARTIFACT ONLY, never public")
    args = parser.parse_args()
    try:
        build(args)
    except (ValueError, KeyError, zipfile.BadZipFile, OSError, json.JSONDecodeError) as exc:
        print("WebSocial pilot build failed:", exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
