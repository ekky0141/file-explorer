"""
File Explorer with Preview - Built with Flet
ติดตั้ง: pip install flet
รัน: python file_explorer.py
"""
 
import flet as ft
import os
import mimetypes
import base64
from pathlib import Path
from datetime import datetime
 
 
# ---- Helpers ----
 
def get_file_icon(filename: str) -> tuple[str, str]:
    """Return (icon, color) based on file extension."""
    ext = Path(filename).suffix.lower()
    mapping = {
        # Images
        ".jpg": (ft.Icons.IMAGE, "#4CAF50"),
        ".jpeg": (ft.Icons.IMAGE, "#4CAF50"),
        ".png": (ft.Icons.IMAGE, "#4CAF50"),
        ".gif": (ft.Icons.IMAGE, "#4CAF50"),
        ".webp": (ft.Icons.IMAGE, "#4CAF50"),
        ".bmp": (ft.Icons.IMAGE, "#4CAF50"),
        ".svg": (ft.Icons.IMAGE, "#66BB6A"),
        # Documents
        ".pdf": (ft.Icons.PICTURE_AS_PDF, "#F44336"),
        ".doc": (ft.Icons.DESCRIPTION, "#2196F3"),
        ".docx": (ft.Icons.DESCRIPTION, "#2196F3"),
        ".xls": (ft.Icons.TABLE_CHART, "#4CAF50"),
        ".xlsx": (ft.Icons.TABLE_CHART, "#4CAF50"),
        ".ppt": (ft.Icons.SLIDESHOW, "#FF5722"),
        ".pptx": (ft.Icons.SLIDESHOW, "#FF5722"),
        # Text / Code
        ".txt": (ft.Icons.TEXT_SNIPPET, "#9E9E9E"),
        ".md": (ft.Icons.TEXT_SNIPPET, "#607D8B"),
        ".py": (ft.Icons.CODE, "#FFEB3B"),
        ".js": (ft.Icons.CODE, "#FFC107"),
        ".ts": (ft.Icons.CODE, "#2196F3"),
        ".html": (ft.Icons.CODE, "#FF5722"),
        ".css": (ft.Icons.CODE, "#2196F3"),
        ".json": (ft.Icons.DATA_OBJECT, "#FF9800"),
        ".xml": (ft.Icons.CODE, "#9C27B0"),
        ".yaml": (ft.Icons.CODE, "#00BCD4"),
        ".yml": (ft.Icons.CODE, "#00BCD4"),
        # Audio
        ".mp3": (ft.Icons.AUDIO_FILE, "#9C27B0"),
        ".wav": (ft.Icons.AUDIO_FILE, "#9C27B0"),
        ".flac": (ft.Icons.AUDIO_FILE, "#9C27B0"),
        # Video
        ".mp4": (ft.Icons.VIDEO_FILE, "#E91E63"),
        ".mkv": (ft.Icons.VIDEO_FILE, "#E91E63"),
        ".avi": (ft.Icons.VIDEO_FILE, "#E91E63"),
        # Archives
        ".zip": (ft.Icons.FOLDER_ZIP, "#795548"),
        ".rar": (ft.Icons.FOLDER_ZIP, "#795548"),
        ".tar": (ft.Icons.FOLDER_ZIP, "#795548"),
        ".gz": (ft.Icons.FOLDER_ZIP, "#795548"),
        # Executables
        ".exe": (ft.Icons.TERMINAL, "#F44336"),
        ".sh": (ft.Icons.TERMINAL, "#4CAF50"),
        ".bat": (ft.Icons.TERMINAL, "#FF9800"),
    }
    return mapping.get(ext, (ft.Icons.INSERT_DRIVE_FILE, "#BDBDBD"))
 
 
def format_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"
 
 
def format_date(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
 
 
def is_text_file(path: str) -> bool:
    mime, _ = mimetypes.guess_type(path)
    if mime:
        return mime.startswith("text/") or mime in (
            "application/json", "application/xml",
            "application/javascript", "application/x-yaml"
        )
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
        chunk.decode("utf-8")
        return True
    except Exception:
        return False
 
 
def is_image_file(path: str) -> bool:
    mime, _ = mimetypes.guess_type(path)
    return mime is not None and mime.startswith("image/")
 
 
def read_text_preview(path: str, max_chars: int = 3000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_chars)
    except Exception as e:
        return f"[ไม่สามารถอ่านไฟล์ได้: {e}]"
 
 
def read_image_base64(path: str) -> str | None:
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        mime, _ = mimetypes.guess_type(path)
        return f"data:{mime};base64,{data}"
    except Exception:
        return None
 
 
# ---- Main App ----
 
def main(page: ft.Page):
    page.title = "File Explorer"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F1117"
    page.padding = 0
    page.fonts = {"mono": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}
 
    # ── State ──
    current_path = [str(Path.home())]
    history: list[str] = []
 
    # ── Theme Colors ──
    C_BG       = "#0F1117"
    C_PANEL    = "#161B22"
    C_CARD     = "#1C2333"
    C_BORDER   = "#30363D"
    C_ACCENT   = "#58A6FF"
    C_ACCENT2  = "#3FB950"
    C_TEXT     = "#E6EDF3"
    C_MUTED    = "#7D8590"
    C_HOVER    = "#21262D"
 
    # ── Breadcrumb ──
    breadcrumb_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=4)
 
    def update_breadcrumb():
        parts = Path(current_path[0]).parts
        breadcrumb_row.controls.clear()
        for i, part in enumerate(parts):
            sub_path = str(Path(*parts[: i + 1]))
            label = part if part != "/" else "/"
            idx = i
 
            def make_click(p):
                def click(_):
                    navigate_to(p)
                return click
 
            breadcrumb_row.controls.append(
                ft.TextButton(
                    label,
                    on_click=make_click(sub_path),
                    style=ft.ButtonStyle(
                        color=C_ACCENT if idx == len(parts) - 1 else C_MUTED,
                        padding=ft.padding.symmetric(horizontal=4, vertical=0),
                        overlay_color=ft.Colors.with_opacity(0.05, C_ACCENT),
                    ),
                )
            )
            if idx < len(parts) - 1:
                breadcrumb_row.controls.append(
                    ft.Text("/", color=C_BORDER, size=14)
                )
 
    # ── Preview panel ──
    preview_title   = ft.Text("เลือกไฟล์เพื่อดูตัวอย่าง", size=13, color=C_MUTED, italic=True)
    preview_content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
    preview_meta    = ft.Column(spacing=4)
 
    def show_preview(path: str):
        preview_content.controls.clear()
        preview_meta.controls.clear()
 
        try:
            stat = os.stat(path)
            name = Path(path).name
            size_str = format_size(stat.st_size)
            date_str = format_date(stat.st_mtime)
            ext = Path(path).suffix.lower()
        except Exception as e:
            preview_title.value = "ข้อผิดพลาด"
            preview_content.controls.append(ft.Text(str(e), color="#F44336", size=12))
            page.update()
            return
 
        preview_title.value = name
 
        # Meta info
        for label, value in [("ขนาด", size_str), ("แก้ไขล่าสุด", date_str), ("ประเภท", ext or "ไม่ทราบ")]:
            preview_meta.controls.append(
                ft.Row([
                    ft.Text(label + ":", size=11, color=C_MUTED, width=90),
                    ft.Text(value, size=11, color=C_TEXT),
                ], spacing=4)
            )
 
        # Content preview
        if is_image_file(path):
            src = read_image_base64(path)
            if src:
                preview_content.controls.append(
                    ft.Image(src=src, fit=ft.ImageFit.CONTAIN, border_radius=8,
                             width=320, height=260)
                )
            else:
                preview_content.controls.append(ft.Text("[ไม่สามารถโหลดรูปได้]", color=C_MUTED))
 
        elif is_text_file(path):
            text = read_text_preview(path)
            preview_content.controls.append(
                ft.Container(
                    content=ft.Text(
                        text,
                        size=11,
                        font_family="mono",
                        color=C_TEXT,
                        selectable=True,
                        no_wrap=False,
                    ),
                    bgcolor="#0D1117",
                    border_radius=8,
                    padding=12,
                    border=ft.border.all(1, C_BORDER),
                )
            )
        else:
            icon, color = get_file_icon(name)
            preview_content.controls.append(
                ft.Column([
                    ft.Icon(icon, size=64, color=color),
                    ft.Text("ไม่รองรับการแสดงตัวอย่างไฟล์นี้", color=C_MUTED, size=12),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
            )
 
        page.update()
 
    # ── File list ──
    file_list = ft.ListView(expand=True, spacing=2, padding=ft.padding.symmetric(horizontal=8, vertical=8))
 
    def navigate_to(path: str):
        if not os.path.isdir(path):
            return
        if current_path[0] != path:
            history.append(current_path[0])
        current_path[0] = path
        load_directory()
 
    def go_back(_):
        if history:
            current_path[0] = history.pop()
            load_directory()
 
    def go_up(_):
        parent = str(Path(current_path[0]).parent)
        if parent != current_path[0]:
            navigate_to(parent)
 
    def load_directory():
        file_list.controls.clear()
        update_breadcrumb()
        preview_title.value = "เลือกไฟล์เพื่อดูตัวอย่าง"
        preview_content.controls.clear()
        preview_meta.controls.clear()
 
        try:
            entries = list(os.scandir(current_path[0]))
        except PermissionError:
            file_list.controls.append(
                ft.Text("  ไม่มีสิทธิ์เข้าถึงโฟลเดอร์นี้", color="#F44336", size=13)
            )
            page.update()
            return
 
        dirs  = sorted([e for e in entries if e.is_dir()],  key=lambda e: e.name.lower())
        files = sorted([e for e in entries if e.is_file()], key=lambda e: e.name.lower())
 
        for entry in dirs + files:
            is_dir = entry.is_dir()
            icon_val = ft.Icons.FOLDER if is_dir else get_file_icon(entry.name)[0]
            icon_col = "#FFB74D" if is_dir else get_file_icon(entry.name)[1]
 
            try:
                stat = entry.stat()
                meta_text = format_date(stat.st_mtime) if is_dir else f"{format_size(stat.st_size)}  ·  {format_date(stat.st_mtime)}"
            except Exception:
                meta_text = ""
 
            def make_tap(e=entry, d=is_dir):
                def tap(_):
                    if d:
                        navigate_to(e.path)
                    else:
                        show_preview(e.path)
                        # Highlight selected
                        for ctrl in file_list.controls:
                            if hasattr(ctrl, "bgcolor"):
                                ctrl.bgcolor = C_HOVER if ctrl.data == e.path else "transparent"
                        page.update()
                return tap
 
            tile = ft.Container(
                data=entry.path,
                content=ft.Row([
                    ft.Icon(icon_val, size=18, color=icon_col),
                    ft.Column([
                        ft.Text(entry.name, size=13, color=C_TEXT, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(meta_text, size=10, color=C_MUTED),
                    ], spacing=1, expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=14, color=C_BORDER) if is_dir else ft.Container(width=14),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(horizontal=12, vertical=7),
                border_radius=6,
                bgcolor="transparent",
                on_click=make_tap(),
                on_hover=lambda e, path=entry.path: (
                    setattr(e.control, "bgcolor", C_HOVER if e.data else "transparent"),
                    page.update()
                ),
            )
            file_list.controls.append(tile)
 
        page.update()
 
    # ── Search ──
    search_field = ft.TextField(
        hint_text="ค้นหาไฟล์...",
        hint_style=ft.TextStyle(color=C_MUTED),
        border_color=C_BORDER,
        focused_border_color=C_ACCENT,
        color=C_TEXT,
        bgcolor=C_CARD,
        border_radius=8,
        height=38,
        text_size=13,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=4),
        prefix_icon=ft.Icons.SEARCH,
    )
 
    def on_search(e):
        query = search_field.value.strip().lower()
        if not query:
            load_directory()
            return
        file_list.controls.clear()
        try:
            entries = list(os.scandir(current_path[0]))
        except Exception:
            return
        matched = [en for en in entries if query in en.name.lower()]
        for entry in sorted(matched, key=lambda x: x.name.lower()):
            is_dir = entry.is_dir()
            icon_val = ft.Icons.FOLDER if is_dir else get_file_icon(entry.name)[0]
            icon_col = "#FFB74D" if is_dir else get_file_icon(entry.name)[1]
 
            def make_tap(e=entry, d=is_dir):
                def tap(_):
                    if d:
                        navigate_to(e.path)
                    else:
                        show_preview(e.path)
                return tap
 
            tile = ft.Container(
                content=ft.Row([
                    ft.Icon(icon_val, size=18, color=icon_col),
                    ft.Text(entry.name, size=13, color=C_TEXT, expand=True, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                ], spacing=10),
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                border_radius=6,
                bgcolor="transparent",
                on_click=make_tap(),
            )
            file_list.controls.append(tile)
        page.update()
 
    search_field.on_change = on_search
 
    # ── Folder picker ──
    def pick_folder_result(e: ft.FilePickerResultEvent):
        if e.path:
            navigate_to(e.path)
 
    folder_picker = ft.FilePicker(on_result=pick_folder_result)
    page.overlay.append(folder_picker)
 
    # ── Top bar ──
    top_bar = ft.Container(
        content=ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK, icon_color=C_MUTED, on_click=go_back,
                          tooltip="ย้อนกลับ", icon_size=18),
            ft.IconButton(ft.Icons.ARROW_UPWARD, icon_color=C_MUTED, on_click=go_up,
                          tooltip="โฟลเดอร์บน", icon_size=18),
            ft.IconButton(ft.Icons.REFRESH, icon_color=C_MUTED, on_click=lambda _: load_directory(),
                          tooltip="รีเฟรช", icon_size=18),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.FOLDER_OPEN, color=C_ACCENT, size=14),
                    breadcrumb_row,
                ], spacing=4),
                expand=True,
                bgcolor=C_CARD,
                border=ft.border.all(1, C_BORDER),
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
            ),
            ft.ElevatedButton(
                "เปิดโฟลเดอร์",
                icon=ft.Icons.FOLDER,
                on_click=lambda _: folder_picker.get_directory_path(),
                bgcolor=C_ACCENT,
                color="#0F1117",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                height=36,
            ),
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=C_PANEL,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border=ft.border.only(bottom=ft.BorderSide(1, C_BORDER)),
    )
 
    # ── Left panel: file list ──
    left_panel = ft.Container(
        content=ft.Column([
            ft.Container(
                content=search_field,
                padding=ft.padding.symmetric(horizontal=8, vertical=8),
            ),
            ft.Divider(height=1, color=C_BORDER),
            file_list,
        ], spacing=0, expand=True),
        expand=2,
        bgcolor=C_PANEL,
        border=ft.border.only(right=ft.BorderSide(1, C_BORDER)),
    )
 
    # ── Right panel: preview ──
    right_panel = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PREVIEW, size=16, color=C_ACCENT),
                    ft.Text("ตัวอย่างไฟล์", size=13, weight=ft.FontWeight.BOLD, color=C_TEXT),
                ], spacing=8),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                border=ft.border.only(bottom=ft.BorderSide(1, C_BORDER)),
            ),
            ft.Container(
                content=preview_title,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            ),
            ft.Container(
                content=preview_meta,
                padding=ft.padding.symmetric(horizontal=16, vertical=0),
            ),
            ft.Container(height=8),
            ft.Container(
                content=preview_content,
                padding=ft.padding.symmetric(horizontal=12, vertical=0),
                expand=True,
            ),
        ], spacing=0, expand=True),
        expand=3,
        bgcolor=C_PANEL,
    )
 
    # ── Layout ──
    page.add(
        ft.Column([
            top_bar,
            ft.Row([left_panel, right_panel], expand=True, spacing=0),
        ], spacing=0, expand=True)
    )
 
    load_directory()
ft.app(target=main)