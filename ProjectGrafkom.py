import sys, math
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QPen, QBrush, QPolygonF,
    QCursor, QImage, QFont, QKeySequence, QTransform, QShortcut
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QComboBox, QLabel, QSlider, QColorDialog,
    QGraphicsView, QGraphicsScene, QGraphicsPolygonItem, QGraphicsPathItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsRectItem,
    QFileDialog, QInputDialog, QStatusBar, QMainWindow, QToolButton,
    QFrame, QSpinBox, QDoubleSpinBox, QSizePolicy,
    QGraphicsItem, QLineEdit, QScrollArea, QGridLayout
)

# ──────────────────────────────────────────────
# Konstanta
# ──────────────────────────────────────────────
W, H = 780, 540
SHAPES = ["Persegi Panjang", "Persegi", "Lingkaran", "Oval", "Segitiga", "Trapesium"]

TOOL_CURSORS = {
    "select":  Qt.ArrowCursor,
    "pen":     Qt.CrossCursor,
    "line":    Qt.CrossCursor,
    "shape":   Qt.CrossCursor,
    "text":    Qt.IBeamCursor,
    "move":    Qt.OpenHandCursor,
    "scale":   Qt.SizeFDiagCursor,
    "rotate":  Qt.SizeAllCursor,
    "fill":    Qt.PointingHandCursor,
    "delete":  Qt.ForbiddenCursor,
}

# ──────────────────────────────────────────────
# Stylesheet – bersih, profesional, ringan
# ──────────────────────────────────────────────
APP_STYLE = """
QMainWindow, QWidget {
    background-color: #f0f0f0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12px;
    color: #1e1e1e;
}

/* ── Toolbar wrapper ── */
#toolbar_widget {
    background-color: #e8e8e8;
    border-bottom: 1px solid #c0c0c0;
    padding: 2px 4px;
}
/* ── Sidebar wrapper ── */
#sidebar_widget {
    background-color: #e8e8e8;
    border-left: 1px solid #c0c0c0;
}

/* ── GroupBox ── */
QGroupBox {
    border: 1px solid #c0c0c0;
    border-radius: 4px;
    margin-top: 6px;
    padding: 4px 6px 4px 6px;
    background-color: #f5f5f5;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 3px;
    color: #555555;
    font-size: 10px;
    font-weight: bold;
}

/* ── Tombol standar ── */
QPushButton, QToolButton {
    background-color: #ffffff;
    border: 1px solid #b0b0b0;
    border-radius: 4px;
    padding: 3px 8px;
    min-width: 0px;
    color: #1e1e1e;
}
QPushButton:hover, QToolButton:hover {
    background-color: #e2eaf5;
    border-color: #5b9bd5;
}
QPushButton:pressed, QToolButton:pressed {
    background-color: #c5d8f0;
}
QPushButton:checked, QToolButton:checked {
    background-color: #2d6db5;
    color: #ffffff;
    border-color: #1a4f8a;
}

/* ── Tombol aktif (tool yang sedang dipilih) ── */
QPushButton#active_tool {
    background-color: #2d6db5;
    color: #ffffff;
    border-color: #1a4f8a;
}

/* ── ComboBox ── */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #b0b0b0;
    border-radius: 4px;
    padding: 3px 6px;
    min-width: 120px;
}
QComboBox:hover { border-color: #5b9bd5; }
QComboBox::drop-down { border: none; width: 18px; }

/* ── Slider ── */
QSlider::groove:horizontal {
    height: 4px;
    background: #c0c0c0;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #2d6db5;
    width: 12px; height: 12px;
    border-radius: 6px;
    margin: -4px 0;
}
QSlider::sub-page:horizontal { background: #5b9bd5; border-radius: 2px; }

/* ── SpinBox ── */
QSpinBox, QDoubleSpinBox {
    background: #ffffff;
    border: 1px solid #b0b0b0;
    border-radius: 4px;
    padding: 2px 4px;
}
QSpinBox:hover, QDoubleSpinBox:hover { border-color: #5b9bd5; }

/* ── StatusBar ── */
QStatusBar {
    background-color: #e0e0e0;
    border-top: 1px solid #c0c0c0;
    color: #444444;
    font-size: 11px;
    padding: 2px 8px;
}
QStatusBar::item { border: none; }

/* ── Frame pemisah ── */
QFrame[frameShape="5"] {          /* VLine */
    color: #c0c0c0;
    max-width: 1px;
    margin: 2px 4px;
}

/* ── Color swatch button ── */
QPushButton#color_btn {
    border: 1px solid #888888;
    border-radius: 3px;
    min-width: 28px;
    max-width: 28px;
    min-height: 22px;
    max-height: 22px;
    padding: 0;
}

/* ── Label kecil ── */
QLabel#small_label {
    color: #555555;
    font-size: 11px;
}
"""

# ──────────────────────────────────────────────
# Helper – buat polygon dari jenis bentuk
# ──────────────────────────────────────────────
def make_polygon(shape, x1, y1, x2, y2):
    def oval_pts(circle=False):
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        if circle:
            r = min(abs(x2 - x1), abs(y2 - y1)) / 2
            rx = ry = r
        else:
            rx = abs(x2 - x1) / 2
            ry = abs(y2 - y1) / 2
        return [
            QPointF(cx + rx * math.cos(2 * math.pi * i / 72),
                    cy + ry * math.sin(2 * math.pi * i / 72))
            for i in range(72)
        ]

    if shape == "Persegi":
        s = max(abs(x2 - x1), abs(y2 - y1))
        x2 = x1 + s * (1 if x2 >= x1 else -1)
        y2 = y1 + s * (1 if y2 >= y1 else -1)

    pts_map = {
        "Persegi":          [QPointF(x1, y1), QPointF(x2, y1), QPointF(x2, y2), QPointF(x1, y2)],
        "Persegi Panjang":  [QPointF(x1, y1), QPointF(x2, y1), QPointF(x2, y2), QPointF(x1, y2)],
        "Segitiga":         [QPointF((x1 + x2) / 2, y1), QPointF(x2, y2), QPointF(x1, y2)],
        "Trapesium":        [
            QPointF(x1 + (x2 - x1) * .25, y1), QPointF(x1 + (x2 - x1) * .75, y1),
            QPointF(x2, y2), QPointF(x1, y2)
        ],
        "Oval":             oval_pts(False),
        "Lingkaran":        oval_pts(True),
    }
    return QPolygonF(pts_map[shape])


# ──────────────────────────────────────────────
# Bounding box item (overlay, tidak permanen)
# ──────────────────────────────────────────────
class BoundingBoxItem(QGraphicsRectItem):
    def __init__(self, parent_item):
        super().__init__()
        pen = QPen(QColor("#2d6db5"), 1.0, Qt.DashLine)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setBrush(QBrush(Qt.transparent))
        self.setZValue(9999)
        self._target = parent_item
        self.update_from(parent_item)

    def update_from(self, item):
        if item is None:
            return
        rect = item.mapToScene(item.boundingRect()).boundingRect()
        # Sedikit padding
        rect.adjust(-4, -4, 4, 4)
        self.setRect(rect)


# ──────────────────────────────────────────────
# Canvas View
# ──────────────────────────────────────────────
class CanvasView(QGraphicsView):
    def __init__(self, app_ref, scene):
        super().__init__(scene)
        self.app_ref = app_ref
        self.setRenderHint(QPainter.Antialiasing)
        self.setBackgroundBrush(QBrush(QColor("white")))
        self.setMouseTracking(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self._zoom = 1.0

    def mousePressEvent(self, e):
        self.app_ref.on_press(self.mapToScene(e.pos()))
        # Untuk tool move/scale/rotate, jangan teruskan ke Qt scene
        # agar sistem internal Qt tidak ikut memindahkan item secara ganda.
        if self.app_ref.tool not in ("move", "scale", "rotate"):
            super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        scene_pos = self.mapToScene(e.pos())
        # Hanya panggil on_drag jika mouse button benar-benar sedang ditekan
        if e.buttons() != Qt.NoButton:
            self.app_ref.on_drag(scene_pos)
        self.app_ref.update_status_pos(scene_pos)
        if self.app_ref.tool not in ("move", "scale", "rotate"):
            super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self.app_ref.on_release(self.mapToScene(e.pos()))
        if self.app_ref.tool not in ("move", "scale", "rotate"):
            super().mouseReleaseEvent(e)

    def wheelEvent(self, e):
        factor = 1.15 if e.angleDelta().y() > 0 else (1 / 1.15)
        self._zoom *= factor
        self._zoom = max(0.1, min(self._zoom, 10.0))
        self.setTransform(QTransform().scale(self._zoom, self._zoom))
        self.app_ref.update_status_zoom(self._zoom)

    def zoom_in(self):
        self._zoom = min(self._zoom * 1.25, 10.0)
        self.setTransform(QTransform().scale(self._zoom, self._zoom))
        self.app_ref.update_status_zoom(self._zoom)

    def zoom_out(self):
        self._zoom = max(self._zoom / 1.25, 0.1)
        self.setTransform(QTransform().scale(self._zoom, self._zoom))
        self.app_ref.update_status_zoom(self._zoom)

    def zoom_reset(self):
        self._zoom = 1.0
        self.setTransform(QTransform())
        self.app_ref.update_status_zoom(self._zoom)


# ──────────────────────────────────────────────
# Aplikasi Utama
# ──────────────────────────────────────────────
class VectorPaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Grafika Komputer")

        # ── State ──
        self.tool = "pen"
        self.stroke_color = QColor("#000000")
        self.fill_color = None
        self.press_pos = self.drag_pos = QPointF(0, 0)
        self.active_item = None
        self.preview_item = None
        self.active_path = None
        self.active_line_preview = None
        self.selected_item = None
        self.bbox_item = None
        # Nilai awal scale/rotate saat drag dimulai
        self._base_scale = 1.0
        self._base_rotation = 0.0
        # Offset antara titik klik mouse dan posisi item saat drag geser dimulai
        # (pola drag-and-drop yang benar: item.setPos(mouse_pos - offset))
        self._drag_offset = QPointF(0, 0)
        # Flag: apakah mouse sedang ditekan dan digeser (true drag)
        self._is_dragging = False

        # Undo/Redo stack – simpan snapshot daftar item (referensi)
        self._undo_stack = []   # list of sets of item references
        self._redo_stack = []

        # ── Scene & View ──
        self.scene = QGraphicsScene(0, 0, W, H)
        self.view = CanvasView(self, self.scene)
        self.view.setCursor(QCursor(TOOL_CURSORS["pen"]))

        # ── Bangun UI ──
        self._build_ui()
        self._setup_shortcuts()

        # ── Status awal ──
        self._update_tool_label()

    # ════════════════════════════════════════════
    # Build UI
    # ════════════════════════════════════════════
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ════════════════════════════════════════
        # TOOLBAR ATAS – hanya alat & edit ringkas
        # ════════════════════════════════════════
        toolbar_container = QWidget()
        toolbar_container.setObjectName("toolbar_widget")
        toolbar_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tc_layout = QHBoxLayout(toolbar_container)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.setSpacing(0)

        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(6, 4, 6, 4)
        toolbar_layout.setSpacing(4)

        self._tool_buttons = {}

        # 1. Alat Gambar
        g1 = QGroupBox("Alat"); gl1 = QHBoxLayout(g1); gl1.setSpacing(3)
        g1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        for label, t in [("Select","select"),("Pen","pen"),("Garis","line"),("Teks","text")]:
            b = QPushButton(label); b.setCheckable(True)
            b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            b.clicked.connect(lambda _, tt=t: self.set_tool(tt))
            self._tool_buttons[t] = b; gl1.addWidget(b)
        toolbar_layout.addWidget(g1)

        # 2. Bentuk
        g2 = QGroupBox("Bentuk"); gl2 = QHBoxLayout(g2); gl2.setSpacing(3)
        g2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.shape_combo = QComboBox(); self.shape_combo.addItems(SHAPES)
        self.shape_combo.setFixedWidth(130)
        self.shape_combo.currentIndexChanged.connect(lambda _: self.set_tool("shape"))
        gl2.addWidget(self.shape_combo)
        b_shape = QPushButton("Gambar"); b_shape.setCheckable(True)
        b_shape.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        b_shape.clicked.connect(lambda: self.set_tool("shape"))
        self._tool_buttons["shape"] = b_shape; gl2.addWidget(b_shape)
        toolbar_layout.addWidget(g2)

        # 3. Transformasi (tool selector saja, presisi di sidebar)
        g3 = QGroupBox("Transformasi"); gl3 = QHBoxLayout(g3); gl3.setSpacing(3)
        g3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        for label, t in [("Geser","move"),("Skala","scale"),("Rotasi","rotate")]:
            b = QPushButton(label); b.setCheckable(True)
            b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            b.clicked.connect(lambda _, tt=t: self.set_tool(tt))
            self._tool_buttons[t] = b; gl3.addWidget(b)
        toolbar_layout.addWidget(g3)

        # 4. Edit
        g4 = QGroupBox("Edit"); gl4 = QHBoxLayout(g4); gl4.setSpacing(3)
        g4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        btn_undo = QPushButton("↩"); btn_undo.setToolTip("Undo (Ctrl+Z)")
        btn_undo.setFixedWidth(32); btn_undo.clicked.connect(self.undo); gl4.addWidget(btn_undo)
        btn_redo = QPushButton("↪"); btn_redo.setToolTip("Redo (Ctrl+Y)")
        btn_redo.setFixedWidth(32); btn_redo.clicked.connect(self.redo); gl4.addWidget(btn_redo)
        btn_del = QPushButton("Hapus"); btn_del.setCheckable(True)
        btn_del.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_del.clicked.connect(lambda: self.set_tool("delete"))
        self._tool_buttons["delete"] = btn_del; gl4.addWidget(btn_del)
        btn_clr = QPushButton("Bersihkan")
        btn_clr.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_clr.clicked.connect(self._clear_canvas)
        gl4.addWidget(btn_clr)
        toolbar_layout.addWidget(g4)

        # 5. Zoom
        g5 = QGroupBox("Zoom"); gl5 = QHBoxLayout(g5); gl5.setSpacing(3)
        g5.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        for label, fn in [("＋", self.view.zoom_in),("－", self.view.zoom_out),("1:1", self.view.zoom_reset)]:
            b = QPushButton(label); b.setFixedWidth(36); b.clicked.connect(fn); gl5.addWidget(b)
        toolbar_layout.addWidget(g5)

        # 6. Pencerminan
        g6 = QGroupBox("Cermin"); gl6 = QHBoxLayout(g6); gl6.setSpacing(3)
        g6.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        btn_flip_h = QPushButton("⇔ H")
        btn_flip_h.setToolTip("Cermin Horizontal")
        btn_flip_h.setFixedWidth(48)
        btn_flip_h.clicked.connect(self._mirror_horizontal)
        gl6.addWidget(btn_flip_h)
        btn_flip_v = QPushButton("⇕ V")
        btn_flip_v.setToolTip("Cermin Vertikal")
        btn_flip_v.setFixedWidth(48)
        btn_flip_v.clicked.connect(self._mirror_vertical)
        gl6.addWidget(btn_flip_v)
        toolbar_layout.addWidget(g6)

        toolbar_layout.addStretch(1)
        tc_layout.addWidget(toolbar_widget)
        tc_layout.addStretch(1)
        root.addWidget(toolbar_container)

        # ════════════════════════════════════════
        # TENGAH: Canvas + Sidebar kanan
        # ════════════════════════════════════════
        mid = QWidget()
        mid_layout = QHBoxLayout(mid)
        mid_layout.setContentsMargins(0, 0, 0, 0)
        mid_layout.setSpacing(0)

        # Canvas
        mid_layout.addWidget(self.view, stretch=1)

        # ── SIDEBAR KANAN ──
        # Wrapper scroll area agar semua grup muat tanpa terpotong
        scroll_area = QScrollArea()
        scroll_area.setFixedWidth(250)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setObjectName("sidebar_widget")

        sidebar = QWidget(); sidebar.setObjectName("sidebar_widget")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(6, 8, 6, 8)
        sb_layout.setSpacing(8)

        # ─ Warna & Kuas ─
        g_color = QGroupBox("Warna & Kuas")
        gl_color = QVBoxLayout(g_color); gl_color.setSpacing(6)

        row_stroke = QHBoxLayout()
        row_stroke.addWidget(QLabel("Garis:"))
        self.btn_stroke = QPushButton()
        self.btn_stroke.setObjectName("color_btn")
        self.btn_stroke.setStyleSheet(f"background:{self.stroke_color.name()}; border:1px solid #888;")
        self.btn_stroke.clicked.connect(self._pick_stroke)
        row_stroke.addWidget(self.btn_stroke); row_stroke.addStretch()
        gl_color.addLayout(row_stroke)

        row_fill = QHBoxLayout()
        row_fill.addWidget(QLabel("Isi:"))
        self.btn_fill = QPushButton()
        self.btn_fill.setObjectName("color_btn")
        self.btn_fill.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #fff,stop:0.49 #fff,stop:0.5 #ddd,stop:1 #ddd);"
            "border:1px solid #888;")
        self.btn_fill.setToolTip("Klik untuk pilih warna isi")
        self.btn_fill.clicked.connect(self._pick_fill)
        row_fill.addWidget(self.btn_fill); row_fill.addStretch()
        gl_color.addLayout(row_fill)

        row_brush = QHBoxLayout()
        row_brush.addWidget(QLabel("Tebal:"))
        self.lbl_brush_val = QLabel("2px"); self.lbl_brush_val.setFixedWidth(30)
        row_brush.addWidget(self.lbl_brush_val)
        gl_color.addLayout(row_brush)
        self.brush_slider = QSlider(Qt.Horizontal)
        self.brush_slider.setRange(1, 20); self.brush_slider.setValue(2)
        self.brush_slider.valueChanged.connect(self._on_brush_changed)
        gl_color.addWidget(self.brush_slider)

        btn_fill_tool = QPushButton("🪣  Isi Warna Objek")
        btn_fill_tool.setCheckable(True)
        btn_fill_tool.clicked.connect(lambda: self.set_tool("fill"))
        self._tool_buttons["fill"] = btn_fill_tool
        gl_color.addWidget(btn_fill_tool)
        sb_layout.addWidget(g_color)

        # ─ Scale Presisi ─
        g_scale = QGroupBox("Scale Presisi")
        gl_scale = QVBoxLayout(g_scale); gl_scale.setSpacing(5)
        row_sc1 = QHBoxLayout()
        for label, val in [("0.5×",0.5),("1×",1.0),("2×",2.0),("3×",3.0)]:
            b = QPushButton(label); b.setFixedWidth(42)
            b.clicked.connect(lambda _, v=val: self._apply_scale(v))
            row_sc1.addWidget(b)
        gl_scale.addLayout(row_sc1)
        row_sc2 = QHBoxLayout()
        row_sc2.addWidget(QLabel("Kustom:"))
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.05, 20.0); self.scale_spin.setValue(1.0)
        self.scale_spin.setSingleStep(0.1)
        row_sc2.addWidget(self.scale_spin)
        gl_scale.addLayout(row_sc2)
        btn_apply_s = QPushButton("Terapkan Scale")
        btn_apply_s.clicked.connect(lambda: self._apply_scale(self.scale_spin.value()))
        gl_scale.addWidget(btn_apply_s)
        sb_layout.addWidget(g_scale)

        # ─ Rotasi Presisi ─
        g_rot = QGroupBox("Rotasi Presisi")
        gl_rot = QVBoxLayout(g_rot); gl_rot.setSpacing(5)
        row_r1 = QHBoxLayout()
        for label, deg in [("45°",45),("90°",90),("180°",180),("270°",270)]:
            b = QPushButton(label); b.setFixedWidth(42)
            b.clicked.connect(lambda _, d=deg: self._apply_rotate(d))
            row_r1.addWidget(b)
        gl_rot.addLayout(row_r1)
        row_r2 = QHBoxLayout()
        row_r2.addWidget(QLabel("Kustom°:"))
        self.rotate_spin = QDoubleSpinBox()
        self.rotate_spin.setRange(-3600, 3600); self.rotate_spin.setValue(0)
        self.rotate_spin.setSingleStep(1)
        row_r2.addWidget(self.rotate_spin)
        gl_rot.addLayout(row_r2)
        btn_apply_r = QPushButton("Terapkan Rotasi")
        btn_apply_r.clicked.connect(lambda: self._apply_rotate(self.rotate_spin.value()))
        gl_rot.addWidget(btn_apply_r)
        sb_layout.addWidget(g_rot)

        # ─ File ─
        g_file = QGroupBox("Simpan")
        gl_file = QVBoxLayout(g_file); gl_file.setSpacing(4)
        btn_jpg = QPushButton("💾  Simpan JPG")
        btn_jpg.clicked.connect(lambda: self.save_image("jpg")); gl_file.addWidget(btn_jpg)
        btn_png = QPushButton("💾  Simpan PNG")
        btn_png.clicked.connect(lambda: self.save_image("png")); gl_file.addWidget(btn_png)
        sb_layout.addWidget(g_file)

        # ─ Translasi Pixel ─
        g_trans = QGroupBox("Translasi Pixel")
        gl_trans = QVBoxLayout(g_trans); gl_trans.setSpacing(4)

        row_px = QHBoxLayout()
        row_px.addWidget(QLabel("Jarak pixel:"))
        self.trans_spin = QSpinBox()
        self.trans_spin.setRange(1, 500); self.trans_spin.setValue(1)
        self.trans_spin.setFixedWidth(60)
        row_px.addWidget(self.trans_spin); row_px.addStretch()
        gl_trans.addLayout(row_px)

        # Grid 3x3 tombol arah – ikon panah, tooltip nama arah
        _dirs = [
            ("↖", -1, -1, "Kiri Atas"),  ("↑", 0, -1, "Atas"),  ("↗", 1, -1, "Kanan Atas"),
            ("←", -1,  0, "Kiri"),        None,                   ("→", 1,  0, "Kanan"),
            ("↙", -1,  1, "Kiri Bawah"),  ("↓", 0,  1, "Bawah"), ("↘", 1,  1, "Kanan Bawah"),
        ]
        grid = QGridLayout(); grid.setSpacing(3)
        for c in range(3):
            grid.setColumnStretch(c, 1)
        for idx, entry in enumerate(_dirs):
            r, c = divmod(idx, 3)
            if entry is None:
                placeholder = QLabel()
                placeholder.setFixedHeight(28)
                grid.addWidget(placeholder, r, c)
            else:
                icon, dx, dy, tip = entry
                b = QPushButton(icon)
                b.setFixedHeight(28)
                b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                b.setToolTip(tip)
                b.clicked.connect(lambda _, x=dx, y=dy: self._translate_selected(x, y))
                grid.addWidget(b, r, c)
        gl_trans.addLayout(grid)
        sb_layout.addWidget(g_trans)

        sb_layout.addStretch(1)
        scroll_area.setWidget(sidebar)
        mid_layout.addWidget(scroll_area)
        root.addWidget(mid, stretch=1)

        # ════════════════════════════════════════
        # STATUS BAR
        # ════════════════════════════════════════
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._lbl_tool    = QLabel("Tool: Pen")
        self._lbl_pos     = QLabel("Posisi: (0, 0)")
        self._lbl_obj     = QLabel("Objek: –")
        self._lbl_zoom    = QLabel("Zoom: 100%")
        self._lbl_scale_r = QLabel("Scale: 1.00×")
        self._lbl_rot_r   = QLabel("Rotasi: 0°")
        for lbl in [self._lbl_tool, self._lbl_pos, self._lbl_obj,
                    self._lbl_zoom, self._lbl_scale_r, self._lbl_rot_r]:
            self.status_bar.addWidget(lbl)
            sep = QFrame(); sep.setFrameShape(QFrame.VLine); sep.setFixedWidth(1)
            self.status_bar.addWidget(sep)

        # Aktifkan tool awal
        self.set_tool("pen")

    # ════════════════════════════════════════════
    # Shortcuts
    # ════════════════════════════════════════════
    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.redo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self).activated.connect(self.redo)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self._delete_selected)
        QShortcut(QKeySequence("+"), self).activated.connect(self.view.zoom_in)
        QShortcut(QKeySequence("-"), self).activated.connect(self.view.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(self.view.zoom_reset)

    # ════════════════════════════════════════════
    # Tool management
    # ════════════════════════════════════════════
    def set_tool(self, tool):
        self.tool = tool
        self.view.setCursor(QCursor(TOOL_CURSORS.get(tool, Qt.CrossCursor)))
        # Update tombol aktif
        for t, btn in self._tool_buttons.items():
            btn.setChecked(t == tool)
        self._update_tool_label()
        # Bersihkan selection saat ganti tool (kecuali transform tools)
        if tool not in ("move", "scale", "rotate", "select", "fill", "delete"):
            self._clear_selection()

    def _update_tool_label(self):
        name_map = {
            "select": "Select", "pen": "Pen", "line": "Garis",
            "shape": f"Bentuk – {self.shape_combo.currentText()}",
            "text": "Teks", "move": "Geser", "scale": "Skala",
            "rotate": "Rotasi", "fill": "Isi Warna", "delete": "Hapus",
        }
        self._lbl_tool.setText(f"  Tool: {name_map.get(self.tool, self.tool)}  ")

    # ════════════════════════════════════════════
    # Pen / Brush helpers
    # ════════════════════════════════════════════
    def _pen(self, preview=False):
        p = QPen(self.stroke_color, self.brush_slider.value())
        p.setCapStyle(Qt.RoundCap); p.setJoinStyle(Qt.RoundJoin)
        if preview:
            p.setStyle(Qt.DashLine)
        return p

    def _brush(self):
        return QBrush(self.fill_color) if self.fill_color else QBrush(Qt.transparent)

    def _on_brush_changed(self, val):
        self.lbl_brush_val.setText(f"{val}px")

    # ════════════════════════════════════════════
    # Color pickers
    # ════════════════════════════════════════════
    def _pick_color(self, title, initial=None):
        c = QColorDialog.getColor(initial or QColor("#000000"), self, title)
        return c if c.isValid() else None

    def _pick_stroke(self):
        c = self._pick_color("Warna Garis", self.stroke_color)
        if c:
            self.stroke_color = c
            self.btn_stroke.setStyleSheet(f"background:{c.name()}; border:1px solid #888;")

    def _pick_fill(self):
        # Tambahkan opsi "tanpa isi"
        c = self._pick_color("Warna Isi", self.fill_color or QColor("#ffffff"))
        if c:
            self.fill_color = c
            self.btn_fill.setStyleSheet(f"background:{c.name()}; border:1px solid #888;")
            self.btn_fill.setToolTip(c.name())

    # ════════════════════════════════════════════
    # Selection & Bounding Box
    # ════════════════════════════════════════════
    def _select_item(self, item):
        self._clear_selection()
        if item is None:
            return
        self.selected_item = item
        self.active_item = item
        self.bbox_item = BoundingBoxItem(item)
        self.scene.addItem(self.bbox_item)
        # Update status
        type_map = {
            QGraphicsPolygonItem: "Shape",
            QGraphicsPathItem: "Freehand",
            QGraphicsLineItem: "Garis",
            QGraphicsTextItem: "Teks",
        }
        obj_name = type_map.get(type(item), "Objek")
        self._lbl_obj.setText(f"  Objek: {obj_name}  ")
        self._lbl_scale_r.setText(f"  Scale: {item.scale():.2f}×  ")
        self._lbl_rot_r.setText(f"  Rotasi: {item.rotation():.1f}°  ")

    def _clear_selection(self):
        if self.bbox_item and self.bbox_item.scene() is not None:
            self.scene.removeItem(self.bbox_item)
        self.bbox_item = None
        self.selected_item = None
        self.active_item = None
        self._lbl_obj.setText("  Objek: –  ")

    def _refresh_bbox(self):
        if self.bbox_item and self.selected_item:
            self.bbox_item.update_from(self.selected_item)
            self._lbl_scale_r.setText(f"  Scale: {self.selected_item.scale():.2f}×  ")
            self._lbl_rot_r.setText(f"  Rotasi: {self.selected_item.rotation():.1f}°  ")

    def _item_at(self, pos):
        # Abaikan bbox_item sendiri
        items = self.scene.items(pos)
        for it in items:
            if it is not self.bbox_item:
                return it
        return None

    # ════════════════════════════════════════════
    # Undo / Redo
    # ════════════════════════════════════════════
    def _snapshot(self):
        """Simpan daftar item yang ada (referensi) sebagai checkpoint."""
        items = [it for it in self.scene.items() if it is not self.bbox_item]
        self._undo_stack.append(set(items))
        self._redo_stack.clear()
        # Batasi stack
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)

    def undo(self):
        if not self._undo_stack:
            return
        # Simpan state sekarang ke redo
        current = set(it for it in self.scene.items() if it is not self.bbox_item)
        self._redo_stack.append(current)
        prev = self._undo_stack.pop()
        self._clear_selection()
        # Hapus item yang tidak ada di snapshot sebelumnya
        for it in list(self.scene.items()):
            if it is not self.bbox_item and it not in prev:
                self.scene.removeItem(it)
        # Re-add item yang hilang (sudah dihapus tapi ada di snapshot)
        for it in prev:
            if it.scene() is None:
                self.scene.addItem(it)

    def redo(self):
        if not self._redo_stack:
            return
        current = set(it for it in self.scene.items() if it is not self.bbox_item)
        self._undo_stack.append(current)
        nxt = self._redo_stack.pop()
        self._clear_selection()
        for it in list(self.scene.items()):
            if it is not self.bbox_item and it not in nxt:
                self.scene.removeItem(it)
        for it in nxt:
            if it.scene() is None:
                self.scene.addItem(it)

    # ════════════════════════════════════════════
    # Transform helpers (presisi)
    # ════════════════════════════════════════════
    def _set_transform_origin(self, item):
        if item:
            item.setTransformOriginPoint(item.boundingRect().center())

    def _apply_scale(self, factor):
        if self.selected_item:
            self._snapshot()
            self._set_transform_origin(self.selected_item)
            self.selected_item.setScale(factor)
            self._refresh_bbox()

    def _apply_rotate(self, degrees):
        if self.selected_item:
            self._snapshot()
            self._set_transform_origin(self.selected_item)
            self.selected_item.setRotation(self.selected_item.rotation() + degrees)
            self._refresh_bbox()

    def _apply_reflection(self, axis: str):
        """
        Refleksi objek terpilih menggunakan matriks transformasi homogen 3x3.

        Refleksi terhadap sumbu Y (horizontal flip) - x' = -x, y' = y:
            | -1  0  0 |
            |  0  1  0 |
            |  0  0  1 |

        Refleksi terhadap sumbu X (vertical flip) - x' = x, y' = -y:
            |  1  0  0 |
            |  0 -1  0 |
            |  0  0  1 |

        Agar objek tidak berpindah, refleksi dilakukan relatif terhadap
        titik tengah bounding box menggunakan pola:
            T(cx,cy) . M_refleksi . T(-cx,-cy)

        Di Qt (row-vector convention), QTransform.map(x,y) menghitung:
            x' = m11*x + m21*y + dx
            y' = m12*x + m22*y + dy
        Dan urutan perkalian A*B berarti "terapkan A dulu, lalu B".
        """
        if not self.selected_item:
            return
        self._snapshot()

        cx = self.selected_item.boundingRect().center().x()
        cy = self.selected_item.boundingRect().center().y()

        # Bangun matriks gabungan T(cx,cy) . M_refleksi . T(-cx,-cy) secara langsung.
        # Di Qt row-vector: QTransform(m11, m12, m21, m22, dx, dy)
        #
        # Untuk refleksi sumbu Y (x' = -x, y' = y):
        #   x_out = -1*(x - cx) + cx = -x + 2*cx
        #   y_out =  1*(y - cy) + cy =  y
        #   => m11=-1, m22=1, dx=2*cx, dy=0
        #
        # Untuk refleksi sumbu X (x' = x, y' = -y):
        #   x_out =  1*(x - cx) + cx =  x
        #   y_out = -1*(y - cy) + cy = -y + 2*cy
        #   => m11=1, m22=-1, dx=0, dy=2*cy

        if axis == "Y":   # Refleksi terhadap sumbu Y: x' = -x + 2cx,  y' = y
            m_ref = QTransform(-1, 0,  0, 1,  2 * cx, 0)
        else:             # Refleksi terhadap sumbu X: x' = x,  y' = -y + 2cy
            m_ref = QTransform( 1, 0,  0,-1,  0, 2 * cy)

        # Kalikan dengan transform yang sudah ada (scale/rotasi sebelumnya tetap terjaga)
        self.selected_item.setTransform(self.selected_item.transform() * m_ref)
        self._refresh_bbox()

    def _mirror_horizontal(self):
        """Cermin horizontal - refleksi terhadap sumbu Y (x' = -x, y' = y)."""
        self._apply_reflection("Y")

    def _mirror_vertical(self):
        """Cermin vertikal - refleksi terhadap sumbu X (x' = x, y' = -y)."""
        self._apply_reflection("X")

    def _translate_selected(self, dx, dy):
        if self.selected_item:
            self._snapshot()
            step = self.trans_spin.value()
            cur = self.selected_item.pos()
            self.selected_item.setPos(cur.x() + dx * step, cur.y() + dy * step)
            self._refresh_bbox()

    def _delete_selected(self):
        if self.selected_item:
            self._snapshot()
            self.scene.removeItem(self.selected_item)
            self._clear_selection()

    def _clear_canvas(self):
        self._snapshot()
        self._clear_selection()
        # Simpan dan hapus semua item kecuali bbox
        for it in list(self.scene.items()):
            self.scene.removeItem(it)

    # ════════════════════════════════════════════
    # Save Image
    # ════════════════════════════════════════════
    def save_image(self, fmt="jpg"):
        filter_str = "JPEG Image (*.jpg *.jpeg)" if fmt == "jpg" else "PNG Image (*.png)"
        file_path, _ = QFileDialog.getSaveFileName(self, "Simpan Gambar", "", filter_str)
        if file_path:
            # Sembunyikan bbox sementara
            if self.bbox_item:
                self.bbox_item.setVisible(False)
            rect = self.scene.sceneRect()
            image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.white)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            self.scene.render(painter)
            painter.end()
            image.save(file_path)
            if self.bbox_item:
                self.bbox_item.setVisible(True)

    # ════════════════════════════════════════════
    # Status bar update
    # ════════════════════════════════════════════
    def update_status_pos(self, pos):
        self._lbl_pos.setText(f"  Posisi: ({int(pos.x())}, {int(pos.y())})  ")

    def update_status_zoom(self, zoom):
        self._lbl_zoom.setText(f"  Zoom: {int(zoom * 100)}%  ")

    # ════════════════════════════════════════════
    # Mouse events
    # ════════════════════════════════════════════
    def on_press(self, pos):
        self.press_pos = self.drag_pos = pos

        if self.tool == "pen":
            self._snapshot()
            self.active_path = QPainterPath(pos)
            self.active_item = QGraphicsPathItem(self.active_path)
            self.active_item.setPen(self._pen())
            self.scene.addItem(self.active_item)

        elif self.tool == "line":
            # Preview garis
            self.active_line_preview = QGraphicsLineItem(
                QLineF(pos, pos)
            )
            self.active_line_preview.setPen(self._pen(True))
            self.scene.addItem(self.active_line_preview)

        elif self.tool == "shape":
            self.preview_item = QGraphicsPolygonItem()
            self.preview_item.setPen(self._pen(True))
            self.preview_item.setBrush(self._brush())
            self.scene.addItem(self.preview_item)

        elif self.tool == "text":
            text, ok = QInputDialog.getText(self, "Masukkan Teks", "Teks:")
            if ok and text:
                self._snapshot()
                item = QGraphicsTextItem(text)
                font = QFont("Segoe UI", 16)
                item.setFont(font)
                item.setDefaultTextColor(self.stroke_color)
                item.setPos(pos)
                item.setFlag(QGraphicsItem.ItemIsMovable)
                self.scene.addItem(item)
                self._select_item(item)

        elif self.tool == "select":
            item = self._item_at(pos)
            self._select_item(item)

        elif self.tool in ("move", "scale", "rotate"):
            hit = self._item_at(pos)
            # Kalau klik bbox sendiri, ambil objek yang sedang dipilih
            if hit is self.bbox_item:
                hit = self.selected_item
            if hit:
                # Catat offset SEBELUM _select_item() mengubah state apapun.
                # Gunakan scenePos() (bukan pos()) agar koordinat konsisten dengan
                # `pos` yang sudah dalam koordinat scene — penting kalau item punya
                # transformasi atau parent.
                if self.tool == "move":
                    self._drag_offset = pos - hit.scenePos()
                    self.view.setCursor(QCursor(Qt.ClosedHandCursor))
                self._select_item(hit)
                self._base_scale    = hit.scale()
                self._base_rotation = hit.rotation()
            # press_pos sudah di-set di awal on_press

        elif self.tool == "fill":
            item = self._item_at(pos)
            if item and hasattr(item, "setBrush"):
                self._snapshot()
                item.setBrush(self._brush())

        elif self.tool == "delete":
            item = self._item_at(pos)
            if item:
                self._snapshot()
                self.scene.removeItem(item)
                if item is self.selected_item:
                    self._clear_selection()

    def on_drag(self, pos):
        if self.tool == "pen" and self.active_item:
            self.active_path.lineTo(pos)
            self.active_item.setPath(self.active_path)

        elif self.tool == "line" and self.active_line_preview:
            self.active_line_preview.setLine(QLineF(self.press_pos, pos))

        elif self.tool == "shape" and self.preview_item:
            self.preview_item.setPolygon(
                make_polygon(self.shape_combo.currentText(),
                             self.press_pos.x(), self.press_pos.y(),
                             pos.x(), pos.y())
            )

        elif self.tool == "move" and self.active_item:
            # Pola drag-and-drop yang benar:
            #   new_pos = mouse_current - offset_saat_klik
            # Ini memastikan objek bergerak mengikuti kursor dengan posisi relatif
            # yang konsisten — tidak melompat, tidak menempel ke kursor secara aneh.
            new_pos = pos - self._drag_offset
            self.active_item.setPos(new_pos)
            self._refresh_bbox()

        # scale dan rotate: tidak melakukan apapun saat drag,
        # perubahan diterapkan sekali saat mouse dilepas (on_release)

        self.drag_pos = pos

    def on_release(self, pos):
        if self.tool == "line" and self.active_line_preview:
            self._snapshot()
            line = QLineF(self.press_pos, pos)
            item = QGraphicsLineItem(line)
            item.setPen(self._pen())
            self.scene.addItem(item)
            self.scene.removeItem(self.active_line_preview)
            self.active_line_preview = None

        elif self.tool == "shape" and self.preview_item:
            self._snapshot()
            poly = make_polygon(
                self.shape_combo.currentText(),
                self.press_pos.x(), self.press_pos.y(),
                pos.x(), pos.y()
            )
            item = QGraphicsPolygonItem(poly)
            item.setPen(self._pen())
            item.setBrush(self._brush())
            self.scene.addItem(item)
            self.scene.removeItem(self.preview_item)
            self.preview_item = None

        elif self.tool == "move" and self.active_item:
            # Snapshot setelah move selesai agar undo/redo bisa mengembalikan posisi
            self._snapshot()
            self._drag_offset = QPointF(0, 0)
            # Kembalikan kursor ke OpenHand (tidak sedang drag)
            self.view.setCursor(QCursor(Qt.OpenHandCursor))

        elif self.tool == "scale" and self.active_item:
            # Terapkan sekali saat lepas — geser kanan = besar, kiri = kecil
            delta_x = pos.x() - self.press_pos.x()
            new_scale = max(0.05, self._base_scale * (1.0 + delta_x * 0.01))
            self._set_transform_origin(self.active_item)
            self.active_item.setScale(new_scale)
            self._base_scale = new_scale
            self._refresh_bbox()
            self._snapshot()

        elif self.tool == "rotate" and self.active_item:
            # Terapkan sekali saat lepas — geser kanan = searah jarum jam
            delta_x = pos.x() - self.press_pos.x()
            new_rot = self._base_rotation + delta_x * 0.5
            self._set_transform_origin(self.active_item)
            self.active_item.setRotation(new_rot)
            self._base_rotation = new_rot
            self._refresh_bbox()
            self._snapshot()

        # Untuk move/scale/rotate, pertahankan selection
        if self.tool not in ("move", "scale", "rotate"):
            self.active_item = None
        self.active_path = None


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    w = VectorPaintApp()
    w.resize(W + 270, H + 100)   # canvas + sidebar(220) + margin
    w.show()
    sys.exit(app.exec())