"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          SISTEMA DE INVENTARIO                         
║                            By Jusep Pimienta  @2026    
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import csv
import hashlib
import os
import platform
import sqlite3
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from PyQt6.QtCore import Qt, QTimer, QDateTime, QLocale
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter, QPen, QBrush, QLinearGradient
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QFormLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QFileDialog,
    QMessageBox, QGraphicsDropShadowEffect
)

class Config:
    APP_NAME = "Joyería"
    APP_VERSION = "1.0"
    DEFAULT_ADMIN_USER = "admin"
    DEFAULT_ADMIN_PASS = "admin1357"
    LOGIN_WIDTH = 420
    LOGIN_HEIGHT = 520
    MAIN_WINDOW_MIN_WIDTH = 1200
    MAIN_WINDOW_MIN_HEIGHT = 750
    
    CATEGORIAS = [
        "Anillos", "Collares", "Pulseras", "Aretes", 
        "Relojes", "Cadenas", "Dijes", "Tobilleras", "Otros"
    ]
    
    MATERIALES = [
        "Oro 18K", "Oro 14K", "Oro 10K", "Plata 925", 
        "Platino", "Acero Inoxidable", "Oro Blanco", 
        "Oro Rosa", "Titanio", "Rodio", "Otro"
    ]
    
    STOCK_BAJO = 5
    STOCK_CRITICO = 0

class Colores:
    FONDO_PRINCIPAL = "#000000"
    FONDO_TARJETA = "#1a1a1a"
    FONDO_INPUT = "#2d2d2d"
    FONDO_HOVER = "#3a3a3a"
    BORDE_NORMAL = "#404040"
    BORDE_FOCO = "#ffffff"
    TEXTO_PRINCIPAL = "#ffffff"
    TEXTO_SECUNDARIO = "#b0b0b0"
    TEXTO_DESHABILITADO = "#555555"

    AZUL_PRIMARIO = "#0073a8"
    AZUL_HOVER = "#005f8b"
    AZUL_FONDO = "#003d5c"
    
    VERDE_EXITO = "#00b894"
    VERDE_FONDO = "#003d33"
    
    ROJO_ERROR = "#ff7675"
    ROJO_FONDO = "#4a1a1a"
    
    AMARILLO_ADVERTENCIA = "#fdcb6e"
    AMARILLO_FONDO = "#4a4000"
    
    PURPURA = "#a29bfe"
    PURPURA_FONDO = "#2d2060"

class Estilos:
    @staticmethod
    def obtener_stylesheet_general() -> str:
        return f"""
        QWidget {{
            background-color: {Colores.FONDO_PRINCIPAL};
            color: {Colores.TEXTO_PRINCIPAL};
            font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
            font-size: 13px;
        }}
        QDialog {{
            background-color: {Colores.FONDO_TARJETA};
        }}
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
            background-color: {Colores.FONDO_INPUT};
            border: 2px solid {Colores.BORDE_NORMAL};
            border-radius: 8px;
            padding: 10px 14px;
            color: {Colores.TEXTO_PRINCIPAL};
            min-height: 20px;
            selection-background-color: {Colores.AZUL_PRIMARIO};
        }}
        QLineEdit:focus, QComboBox:focus, 
        QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
            border: 2px solid {Colores.AZUL_PRIMARIO};
            background-color: #222222;
        }}
        QLineEdit:hover, QComboBox:hover,
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {Colores.TEXTO_SECUNDARIO};
        }}
        QLineEdit::placeholder {{
            color: {Colores.TEXTO_SECUNDARIO};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {Colores.TEXTO_SECUNDARIO};
            margin-right: 10px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {Colores.FONDO_TARJETA};
            border: 2px solid {Colores.BORDE_NORMAL};
            border-radius: 8px;
            selection-background-color: {Colores.AZUL_PRIMARIO};
            outline: none;
        }}
        QPushButton {{
            background-color: {Colores.FONDO_HOVER};
            color: {Colores.TEXTO_PRINCIPAL};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: #4d4d4d;
        }}
        QPushButton:pressed {{
            background-color: {Colores.FONDO_INPUT};
        }}
        QPushButton:disabled {{
            background-color: {Colores.FONDO_TARJETA};
            color: {Colores.TEXTO_DESHABILITADO};
        }}
        QTableWidget {{
            background-color: {Colores.FONDO_TARJETA};
            alternate-background-color: {Colores.FONDO_TARJETA};
            gridline-color: {Colores.BORDE_NORMAL};
            border-radius: 10px;
            border: 2px solid {Colores.BORDE_NORMAL};
            selection-background-color: {Colores.AZUL_FONDO};
            selection-color: {Colores.TEXTO_PRINCIPAL};
            outline: none;
        }}
        QTableWidget::item {{
            padding: 8px 12px;
            border: none;
            border-bottom: 1px solid {Colores.BORDE_NORMAL};
            background-color: {Colores.FONDO_TARJETA};
        }}
        QTableWidget::item:selected {{
            background-color: {Colores.AZUL_FONDO};
            color: {Colores.TEXTO_PRINCIPAL};
        }}
        QTableWidget::item:hover {{
            background-color: {Colores.FONDO_HOVER};
        }}
        QHeaderView::section {{
            background-color: {Colores.FONDO_PRINCIPAL};
            color: {Colores.TEXTO_SECUNDARIO};
            padding: 12px 8px;
            border: none;
            border-bottom: 2px solid {Colores.AZUL_PRIMARIO};
            font-weight: 700;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        QHeaderView::section:hover {{
            background-color: {Colores.FONDO_TARJETA};
            color: {Colores.TEXTO_PRINCIPAL};
        }}
        QTableWidget QTableCornerButton::section {{
            background-color: {Colores.FONDO_PRINCIPAL};
            border: none;
        }}
        QScrollBar:vertical {{
            background: {Colores.FONDO_TARJETA};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {Colores.FONDO_HOVER};
            min-height: 30px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {Colores.AZUL_PRIMARIO};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: {Colores.FONDO_TARJETA};
            height: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: {Colores.FONDO_HOVER};
            min-width: 30px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {Colores.AZUL_PRIMARIO};
        }}
        QMessageBox {{
            background-color: {Colores.FONDO_TARJETA};
        }}
        QMessageBox QLabel {{
            color: {Colores.TEXTO_PRINCIPAL};
            font-size: 14px;
        }}
        QMessageBox QPushButton {{
            min-width: 80px;
            padding: 8px 16px;
            background-color: {Colores.FONDO_HOVER};
        }}
        QMessageBox QPushButton:hover {{
            background-color: {Colores.AZUL_PRIMARIO};
        }}
        """
    
    @staticmethod
    def estilo_boton_primario() -> str:
        return f"""
            QPushButton {{
                background-color: {Colores.AZUL_PRIMARIO};
                color: white;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {Colores.AZUL_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colores.AZUL_FONDO};
            }}
        """
    
    @staticmethod
    def estilo_boton_exito() -> str:
        return f"""
            QPushButton {{
                background-color: {Colores.VERDE_EXITO};
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00a383;
            }}
            QPushButton:pressed {{
                background-color: {Colores.VERDE_FONDO};
            }}
        """
    
    @staticmethod
    def estilo_boton_peligro() -> str:
        return f"""
            QPushButton {{
                background-color: {Colores.ROJO_ERROR};
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #d63031;
            }}
            QPushButton:pressed {{
                background-color: {Colores.ROJO_FONDO};
            }}
            QPushButton:disabled {{
                background-color: {Colores.FONDO_HOVER};
                color: {Colores.TEXTO_DESHABILITADO};
            }}
        """
    
    @staticmethod
    def estilo_boton_advertencia() -> str:
        return f"""
            QPushButton {{
                background-color: {Colores.AMARILLO_ADVERTENCIA};
                color: #1e293b;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e1c06a;
            }}
            QPushButton:pressed {{
                background-color: {Colores.AMARILLO_FONDO};
            }}
            QPushButton:disabled {{
                background-color: {Colores.FONDO_HOVER};
                color: {Colores.TEXTO_DESHABILITADO};
            }}
        """
    
    @staticmethod
    def estilo_boton_purpura() -> str:
        return f"""
            QPushButton {{
                background-color: {Colores.PURPURA};
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #8c7ae6;
            }}
            QPushButton:pressed {{
                background-color: {Colores.PURPURA_FONDO};
            }}
        """

class BaseDatos:
    def __init__(self):
        self.ruta_db = self._obtener_ruta_base_datos()
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self._inicializar_conexion()
    
    def _obtener_ruta_base_datos(self) -> Path:
        sistema = platform.system().lower()
        home = Path.home()
        
        if sistema == "windows":
            base = Path(os.environ.get('LOCALAPPDATA', home))
        else:
            base = Path(os.environ.get('XDG_DATA_HOME', home / '.local' / 'share'))
        
        carpeta_app = base / "JoyeriaSystem"
        
        try:
            carpeta_app.mkdir(parents=True, exist_ok=True)
        except Exception:
            carpeta_app = Path(".")
        
        return carpeta_app / "joyeria.db"
    
    def _inicializar_conexion(self):
        try:
            self._conectar()
            self._verificar_integridad()
            self._crear_tablas()
            self._inicializar_administrador()
        except Exception as e:
            print(f"⚠️ Error de conexión: {e}. Intentando reparar...")
            self._reparar_base_datos()
    
    def _conectar(self):
        self.conn = sqlite3.connect(str(self.ruta_db))
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.cursor = self.conn.cursor()
    
    def _verificar_integridad(self):
        self.cursor.execute("PRAGMA integrity_check")
        resultado = self.cursor.fetchone()
        if resultado and resultado[0] != "ok":
            raise sqlite3.DatabaseError(f"Base de datos corrupta: {resultado[0]}")
    
    def _reparar_base_datos(self):
        if self.conn:
            self.conn.close()
        
        if self.ruta_db.exists():
            try:
                self.ruta_db.unlink()
            except Exception:
                backup = f"{self.ruta_db}.backup_{datetime.now().timestamp()}"
                self.ruta_db.rename(backup)
        
        self._conectar()
        self._crear_tablas()
        self._inicializar_administrador()
    
    def _crear_tablas(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                usuario TEXT PRIMARY KEY,
                clave TEXT NOT NULL,
                nombre TEXT NOT NULL,
                rol TEXT DEFAULT 'usuario',
                email TEXT,
                fecha_registro TEXT,
                activo INTEGER DEFAULT 1
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT,
                material TEXT,
                peso REAL DEFAULT 0.0,
                precio REAL DEFAULT 0.0,
                cantidad INTEGER DEFAULT 0,
                proveedor TEXT,
                descripcion TEXT,
                fecha_registro TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario_materiales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                peso REAL DEFAULT 0.0
            )
        ''')
        self.conn.commit()
    
    def _inicializar_administrador(self):
        self.cursor.execute(
            "SELECT usuario FROM usuarios WHERE usuario = ?",
            (Config.DEFAULT_ADMIN_USER,)
        )
        
        if not self.cursor.fetchone():
            clave_hash = hashlib.sha256(
                Config.DEFAULT_ADMIN_PASS.encode('utf-8')
            ).hexdigest()
            
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute('''
                INSERT INTO usuarios (usuario, clave, nombre, rol, email, fecha_registro, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                Config.DEFAULT_ADMIN_USER, 
                clave_hash, 
                "Administrador", 
                "admin", 
                "juseppimienta@gmail.com", 
                fecha_actual, 
                1
            ))
            
            self.conn.commit()
    
    def verificar_credenciales(self, usuario: str, clave: str) -> Optional[Dict[str, Any]]:
        if not usuario or not clave:
            return None
        
        self.cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = ?", 
            (usuario,)
        )
        fila = self.cursor.fetchone()
        
        if not fila:
            return None
        
        if not bool(fila[6]):
            return None
        
        clave_hash = hashlib.sha256(clave.encode('utf-8')).hexdigest()
        
        if fila[1] == clave_hash:
            return {
                "usuario": fila[0],
                "nombre": fila[2],
                "rol": fila[3],
                "email": fila[4]
            }
        
        return None

    def obtener_productos(self, filtro_categoria: str = None, filtro_material: str = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM productos WHERE 1=1"
        params = []
        
        if filtro_categoria:
            query += " AND categoria = ?"
            params.append(filtro_categoria)
        
        if filtro_material:
            query += " AND material = ?"
            params.append(filtro_material)
        
        query += " ORDER BY nombre"
        
        self.cursor.execute(query, tuple(params))
        filas = self.cursor.fetchall()
        
        return [self._fila_a_producto(fila) for fila in filas]
    
    def obtener_producto_por_id(self, id_producto: int) -> Optional[Dict[str, Any]]:
        if not id_producto:
            return None
        
        self.cursor.execute(
            "SELECT * FROM productos WHERE id = ?", 
            (id_producto,)
        )
        fila = self.cursor.fetchone()
        
        return self._fila_a_producto(fila) if fila else None
    
    def agregar_producto(self, datos: Dict[str, Any]) -> bool:
        if not datos or not datos.get('nombre'):
            return False
        
        try:
            self.cursor.execute('''
                INSERT INTO productos 
                (nombre, categoria, material, peso, precio, cantidad, proveedor, descripcion, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datos.get('nombre', ''),
                datos.get('categoria', ''),
                datos.get('material', ''),
                datos.get('peso', 0),
                datos.get('precio', 0),
                datos.get('cantidad', 0),
                datos.get('proveedor', ''),
                datos.get('descripcion', ''),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al agregar producto: {e}")
            self.conn.rollback()
            return False
    
    def actualizar_producto(self, id_producto: int, datos: Dict[str, Any]) -> bool:
        if not id_producto or not datos or not datos.get('nombre'):
            return False
        
        try:
            self.cursor.execute('''
                UPDATE productos 
                SET nombre=?, categoria=?, material=?, peso=?, precio=?, cantidad=?, proveedor=?, descripcion=?
                WHERE id=?
            ''', (
                datos.get('nombre', ''),
                datos.get('categoria', ''),
                datos.get('material', ''),
                datos.get('peso', 0),
                datos.get('precio', 0),
                datos.get('cantidad', 0),
                datos.get('proveedor', ''),
                datos.get('descripcion', ''),
                id_producto
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            self.conn.rollback()
            return False
    
    def eliminar_producto(self, id_producto: int) -> bool:
        if not id_producto:
            return False
        
        try:
            self.cursor.execute(
                "DELETE FROM productos WHERE id = ?", 
                (id_producto,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar producto: {e}")
            self.conn.rollback()
            return False
    
    def buscar_productos(self, texto: str) -> List[Dict[str, Any]]:
        if not texto:
            return []
        
        patron = f"%{texto}%"
        self.cursor.execute('''
            SELECT * FROM productos 
            WHERE nombre LIKE ? 
               OR categoria LIKE ? 
               OR material LIKE ? 
               OR proveedor LIKE ?
            ORDER BY nombre
        ''', (patron, patron, patron, patron))
        
        filas = self.cursor.fetchall()
        return [self._fila_a_producto(fila) for fila in filas]
    
    def _fila_a_producto(self, fila: tuple) -> Dict[str, Any]:
        if not fila:
            return None
        
        return {
            "id": fila[0],
            "nombre": fila[1] or "",
            "categoria": fila[2] or "",
            "material": fila[3] or "",
            "peso": fila[4] or 0.0,
            "precio": fila[5] or 0.0,
            "cantidad": fila[6] or 0,
            "proveedor": fila[7] or "",
            "descripcion": fila[8] or "",
            "fecha_registro": fila[9] or ""
        }
    
    # --- CRUD Inventario de Materiales ---
    
    def obtener_materiales_inventario(self) -> List[Dict[str, Any]]:
        self.cursor.execute("SELECT id, nombre, peso FROM inventario_materiales ORDER BY nombre")
        filas = self.cursor.fetchall()
        return [{"id": f[0], "nombre": f[1], "peso": f[2]} for f in filas]
    
    def agregar_incrementar_material(self, nombre: str, peso: float) -> bool:
        try:
            self.cursor.execute("SELECT id, peso FROM inventario_materiales WHERE nombre = ?", (nombre,))
            existente = self.cursor.fetchone()
            
            if existente:
                nuevo_peso = existente[1] + peso
                self.cursor.execute("UPDATE inventario_materiales SET peso = ? WHERE id = ?", (nuevo_peso, existente[0]))
            else:
                self.cursor.execute("INSERT INTO inventario_materiales (nombre, peso) VALUES (?, ?)", (nombre, peso))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error en inventario materiales: {e}")
            self.conn.rollback()
            return False

    def editar_material_inventario(self, id_mat: int, nombre: str, peso: float) -> bool:
        try:
            self.cursor.execute("UPDATE inventario_materiales SET nombre=?, peso=? WHERE id=?", (nombre, peso, id_mat))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error editando material: {e}")
            self.conn.rollback()
            return False

    def eliminar_material_inventario(self, id_mat: int) -> bool:
        try:
            self.cursor.execute("DELETE FROM inventario_materiales WHERE id = ?", (id_mat,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error eliminando material: {e}")
            self.conn.rollback()
            return False

    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        try:
            self.cursor.execute("SELECT COUNT(*) FROM productos")
            total_items = self.cursor.fetchone()[0] or 0
            
            self.cursor.execute("SELECT SUM(peso) FROM productos")
            peso_total = float(self.cursor.fetchone()[0] or 0)
            
            self.cursor.execute("SELECT AVG(precio) FROM productos")
            precio_promedio = float(self.cursor.fetchone()[0] or 0)
            
            self.cursor.execute('''
                SELECT nombre FROM productos 
                ORDER BY (precio * cantidad) DESC LIMIT 1
            ''')
            item_mas_valioso = self.cursor.fetchone()
            item_mas_valioso = item_mas_valioso[0] if item_mas_valioso else "N/A"
            
            self.cursor.execute(
                "SELECT COUNT(*) FROM productos WHERE cantidad <= ?",
                (Config.STOCK_BAJO,)
            )
            bajo_stock = self.cursor.fetchone()[0] or 0
            
            return {
                "total_items": total_items,
                "peso_total": peso_total,
                "precio_promedio": precio_promedio,
                "item_mas_valioso": item_mas_valioso,
                "bajo_stock": bajo_stock
            }
        except Exception as e:
            print(f"Error en estadísticas generales: {e}")
            return {}
    
    def obtener_estadisticas_por_material(self) -> List[Dict[str, Any]]:
        try:
            self.cursor.execute('''
                SELECT 
                    material,
                    SUM(peso) as peso_total,
                    SUM(precio * cantidad) as valor_total,
                    COUNT(*) as cantidad_items,
                    AVG(precio) as precio_promedio
                FROM productos 
                WHERE material != '' AND material IS NOT NULL
                GROUP BY material
                ORDER BY peso_total DESC
            ''')
            
            filas = self.cursor.fetchall()
            
            return [
                {
                    "material": fila[0],
                    "peso_total": float(fila[1] or 0),
                    "valor_total": float(fila[2] or 0),
                    "cantidad_items": fila[3] or 0,
                    "precio_promedio": float(fila[4] or 0)
                }
                for fila in filas
            ]
        except Exception as e:
            print(f"Error en estadísticas por material: {e}")
            return []
   
    def obtener_categorias(self) -> List[str]:
        self.cursor.execute(
            "SELECT DISTINCT categoria FROM productos WHERE categoria != '' ORDER BY categoria"
        )
        return [fila[0] for fila in self.cursor.fetchall() if fila[0]]
    
    def obtener_materiales(self) -> List[str]:
        self.cursor.execute(
            "SELECT DISTINCT material FROM productos WHERE material != '' ORDER BY material"
        )
        return [fila[0] for fila in self.cursor.fetchall() if fila[0]]
    
    def cerrar(self):
        if self.conn:
            self.conn.close()

class TarjetaEstadistica(QFrame):
    def __init__(self, titulo: str, icono: str, color_acento: str, color_fondo: str, parent=None):
        super().__init__(parent)
        self._configurar_apariencia(titulo, icono, color_acento, color_fondo)
    
    def _configurar_apariencia(self, titulo: str, icono: str, color_acento: str, color_fondo: str):
        self.setFixedHeight(80)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colores.FONDO_TARJETA};
                border-radius: 12px;
                border: 1px solid {Colores.BORDE_NORMAL};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        icono_label = QLabel(icono)
        icono_label.setFixedSize(44, 44)
        icono_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icono_label.setStyleSheet(f"""
            background-color: {color_fondo};
            color: {color_acento};
            font-size: 22px;
            border-radius: 10px;
        """)
        
        texto_layout = QVBoxLayout()
        texto_layout.setSpacing(2)
        
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(f"""
            color: {Colores.TEXTO_SECUNDARIO};
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        
        self.valor_label = QLabel("...")
        self.valor_label.setStyleSheet(f"""
            color: {color_acento};
            font-size: 20px;
            font-weight: bold;
        """)
        
        texto_layout.addWidget(titulo_label)
        texto_layout.addWidget(self.valor_label)
        
        layout.addWidget(icono_label)
        layout.addLayout(texto_layout)
        layout.addStretch()
    
    def establecer_valor(self, valor: str):
        self.valor_label.setText(valor)

class BotonAccion(QPushButton):
    def __init__(self, texto: str, tipo: str = "primario", icono: str = None, parent=None):
        super().__init__(parent)
        
        texto_completo = f"{icono}  {texto}" if icono else texto
        self.setText(texto_completo)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        
        estilos = {
            "primario": Estilos.estilo_boton_primario(),
            "exito": Estilos.estilo_boton_exito(),
            "peligro": Estilos.estilo_boton_peligro(),
            "advertencia": Estilos.estilo_boton_advertencia(),
            "purpura": Estilos.estilo_boton_purpura()
        }
        
        self.setStyleSheet(estilos.get(tipo, Estilos.estilo_boton_primario()))

class TablaInventario(QTableWidget):
    def __init__(self):
        super().__init__()
        self._configurar_tabla()
    
    def _configurar_tabla(self):
        self.setColumnCount(9)
        self.setHorizontalHeaderLabels([
            "ID", "Nombre", "Categoría", "Material", 
            "Peso (g)", "Precio ($)", "Stock", "Proveedor", "Fecha"
        ])
        
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)

        self.setAlternatingRowColors(False) 
        self.verticalHeader().setDefaultSectionSize(32)
        
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
    
    def cargar_productos(self, productos: List[Dict[str, Any]]):
        self.setRowCount(len(productos))
        
        for i, p in enumerate(productos):
            self._agregar_fila_producto(i, p)
    
    def _agregar_fila_producto(self, fila: int, producto: Dict[str, Any]):
        self.setItem(fila, 0, QTableWidgetItem(str(producto['id'])))
        self.setItem(fila, 1, QTableWidgetItem(producto['nombre']))
        self.setItem(fila, 2, QTableWidgetItem(producto['categoria']))
        self.setItem(fila, 3, QTableWidgetItem(producto['material']))
        self.setItem(fila, 4, QTableWidgetItem(f"{producto['peso']:.2f}"))
        self.setItem(fila, 5, QTableWidgetItem(f"${producto['precio']:,.2f}"))
        
        stock_item = QTableWidgetItem(str(producto['cantidad']))
        self._aplicar_estilo_stock(stock_item, producto['cantidad'])
        self.setItem(fila, 6, stock_item)    
      
        self.setItem(fila, 7, QTableWidgetItem(producto['proveedor']))
        fecha = producto['fecha_registro'][:10] if producto['fecha_registro'] else ""
        self.setItem(fila, 8, QTableWidgetItem(fecha))
    
    def _aplicar_estilo_stock(self, item: QTableWidgetItem, cantidad: int):
        if cantidad == Config.STOCK_CRITICO:
            item.setBackground(QColor(Colores.ROJO_FONDO))
            item.setForeground(QColor(Colores.ROJO_ERROR))
        elif cantidad <= Config.STOCK_BAJO:
            item.setBackground(QColor(Colores.AMARILLO_FONDO))
            item.setForeground(QColor(Colores.AMARILLO_ADVERTENCIA))
    
    def obtener_id_seleccionado(self) -> Optional[int]:
        fila = self.currentRow()
        if fila < 0:
            return None
        
        item = self.item(fila, 0)
        return int(item.text()) if item else None
    
    def obtener_nombre_seleccionado(self) -> Optional[str]:
        fila = self.currentRow()
        if fila < 0:
            return None
        
        item = self.item(fila, 1)
        return item.text() if item else None

class VentanaLogin(QDialog):
    def __init__(self):
        super().__init__()
        self.db = BaseDatos()
        self.usuario_actual = None
        self.posicion_arrastre = None
        
        self._configurar_ventana()
        self._crear_interfaz()
        self._aplicar_efectos()
    
    def _configurar_ventana(self):
        self.setWindowTitle(f"{Config.APP_NAME} - Login")
        self.setFixedSize(Config.LOGIN_WIDTH, Config.LOGIN_HEIGHT)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(Estilos.obtener_stylesheet_general())
    
    def _crear_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tarjeta = QFrame()
        self.tarjeta.setStyleSheet(f"""
            QFrame {{
                background-color: {Colores.FONDO_TARJETA};
                border-radius: 20px;
                border: 1px solid {Colores.BORDE_NORMAL};
            }}
        """)
        
        tarjeta_layout = QVBoxLayout(self.tarjeta)
        tarjeta_layout.setSpacing(20)
        tarjeta_layout.setContentsMargins(40, 50, 40, 40)
        
        self._crear_encabezado(tarjeta_layout)
        self._crear_campos_entrada(tarjeta_layout)
        self._crear_botones(tarjeta_layout)

        self.estado_label = QLabel("")
        self.estado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.estado_label.setStyleSheet("font-size: 12px;")
        tarjeta_layout.addWidget(self.estado_label)

        layout.addStretch()
        layout.addWidget(self.tarjeta, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.tarjeta.mousePressEvent = self._evento_prensa_mouse
        self.tarjeta.mouseMoveEvent = self._evento_movimiento_mouse
        self.tarjeta.mouseReleaseEvent = self._evento_liberacion_mouse
    
    def _crear_encabezado(self, layout: QVBoxLayout):
        logo = QLabel("")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 56px; border: none; background: transparent;")
        
        titulo = QLabel("Sistema de Inventario")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {Colores.TEXTO_PRINCIPAL};
            margin-bottom: 8px;
        """)
        
        subtitulo = QLabel("Joyería")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet(f"""
            font-size: 14px;
            color: {Colores.TEXTO_SECUNDARIO};
            margin-bottom: 25px;
        """)
        
        layout.addWidget(logo)
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
    
    def _crear_campos_entrada(self, layout: QVBoxLayout):
        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("👤  Usuario")
        self.usuario_input.setFixedHeight(50)
        self.usuario_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colores.FONDO_INPUT};
                border: 2px solid {Colores.BORDE_NORMAL};
                border-radius: 12px;
                padding: 10px 16px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Colores.AZUL_PRIMARIO};
            }}
        """)

        self.clave_input = QLineEdit()
        self.clave_input.setPlaceholderText("🔒  Contraseña")
        self.clave_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave_input.setFixedHeight(50)
        self.clave_input.setStyleSheet(self.usuario_input.styleSheet())

        self.usuario_input.returnPressed.connect(self.clave_input.setFocus)
        self.clave_input.returnPressed.connect(self._intentar_login)
        
        layout.addWidget(self.usuario_input)
        layout.addWidget(self.clave_input)
    
    def _crear_botones(self, layout: QVBoxLayout):
        self.btn_ingresar = QPushButton("ENTRAR")
        self.btn_ingresar.setFixedHeight(52)
        self.btn_ingresar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ingresar.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colores.AZUL_PRIMARIO};
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background-color: {Colores.AZUL_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colores.AZUL_FONDO};
            }}
        """)
        self.btn_ingresar.clicked.connect(self._intentar_login)

        self.btn_salir = QPushButton("Salir")
        self.btn_salir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_salir.setStyleSheet(f"""
            background-color: transparent;
            color: {Colores.TEXTO_SECUNDARIO};
            border: none;
            font-size: 13px;
            padding: 8px;
        """)
        self.btn_salir.clicked.connect(self.reject)
        
        layout.addWidget(self.btn_ingresar)
        layout.addWidget(self.btn_salir)
    
    def _aplicar_efectos(self):
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(40)
        sombra.setXOffset(0)
        sombra.setYOffset(15)
        sombra.setColor(QColor(0, 0, 0, 180))
        self.tarjeta.setGraphicsEffect(sombra)

    def _evento_prensa_mouse(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.posicion_arrastre = event.globalPosition().toPoint()
    
    def _evento_movimiento_mouse(self, event):
        if self.posicion_arrastre is not None:
            delta = event.globalPosition().toPoint() - self.posicion_arrastre
            self.move(self.pos() + delta)
            self.posicion_arrastre = event.globalPosition().toPoint()
    
    def _evento_liberacion_mouse(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.posicion_arrastre = None
    
    def _intentar_login(self):
        usuario = self.usuario_input.text().strip()
        clave = self.clave_input.text().strip()

        if not usuario or not clave:
            self._mostrar_estado("Por favor complete todos los campos", "error")
            return
        
        self._mostrar_estado("Verificando credenciales...", "info")
        QApplication.processEvents()
        
        usuario_data = self.db.verificar_credenciales(usuario, clave)
        
        if usuario_data:
            self._mostrar_estado("✅ Acceso concedido", "exito")
            QTimer.singleShot(500, lambda: self._completar_login(usuario_data))
        else:
            self._mostrar_estado("❌ Usuario o contraseña incorrectos", "error")
            self.clave_input.clear()
            self.clave_input.setFocus()
    
    def _mostrar_estado(self, mensaje: str, tipo: str):
        colores = {
            "info": Colores.AZUL_PRIMARIO,
            "exito": Colores.VERDE_EXITO,
            "error": Colores.ROJO_ERROR
        }
        color = colores.get(tipo, Colores.TEXTO_SECUNDARIO)
        self.estado_label.setText(mensaje)
        self.estado_label.setStyleSheet(f"color: {color}; font-size: 12px;")
    
    def _completar_login(self, usuario_data: Dict[str, Any]):
        self.usuario_actual = usuario_data
        self.db.cerrar()
        self.accept()

class DialogoProducto(QDialog):
    def __init__(self, db: BaseDatos, producto: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.producto = producto
        
        titulo = "Editar Producto" if producto else "Nuevo Producto"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(550)
        self.setStyleSheet(Estilos.obtener_stylesheet_general())
        
        self._crear_interfaz()
        
        if producto:
            self._cargar_datos_producto()
    
    def _crear_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        contenedor = QFrame()
        contenedor.setStyleSheet(f"""
            QFrame {{
                background-color: {Colores.FONDO_TARJETA};
                border-radius: 16px;
                border: 1px solid {Colores.BORDE_NORMAL};
            }}
        """)
        
        contenedor_layout = QVBoxLayout(contenedor)
        contenedor_layout.setContentsMargins(24, 24, 24, 24)
        contenedor_layout.setSpacing(18)
        
        self._crear_formulario(contenedor_layout)
        self._crear_botones(contenedor_layout)
        
        layout.addWidget(contenedor)
    
    def _crear_formulario(self, layout: QVBoxLayout):
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del producto")
        form_layout.addRow("Nombre:", self.nombre_input)
        
        self.categoria_combo = QComboBox()
        self.categoria_combo.setEditable(True)
        categorias = Config.CATEGORIAS + [
            c for c in self.db.obtener_categorias() 
            if c not in Config.CATEGORIAS
        ]
        self.categoria_combo.addItems(categorias)
        form_layout.addRow("Categoría:", self.categoria_combo)
        
        self.material_combo = QComboBox()
        self.material_combo.setEditable(True)
        materiales = Config.MATERIALES + [
            m for m in self.db.obtener_materiales() 
            if m not in Config.MATERIALES
        ]
        self.material_combo.addItems(materiales)
        form_layout.addRow("Material:", self.material_combo)
        
        peso_precio_layout = QHBoxLayout()
        
        self.peso_input = QDoubleSpinBox()
        self.peso_input.setRange(0, 100000)
        self.peso_input.setSuffix(" g")
        self.peso_input.setDecimals(2)
        
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setRange(0, 10000000)
        self.precio_input.setPrefix("$ ")
        self.precio_input.setDecimals(2)
        
        peso_precio_layout.addWidget(self.peso_input)
        peso_precio_layout.addWidget(self.precio_input)
        form_layout.addRow("Peso / Precio:", peso_precio_layout)
        
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 100000)
        form_layout.addRow("Stock:", self.stock_input)

        self.proveedor_input = QLineEdit()
        self.proveedor_input.setPlaceholderText("Nombre del proveedor")
        form_layout.addRow("Proveedor:", self.proveedor_input)
        
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(80)
        self.descripcion_input.setPlaceholderText("Descripción del producto...")
        form_layout.addRow("Descripción:", self.descripcion_input)
        
        layout.addLayout(form_layout)
    
    def _crear_botones(self, layout: QVBoxLayout):
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(12)
        
        self.btn_cancelar = BotonAccion("Cancelar", tipo="peligro")
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_guardar = BotonAccion("Guardar Producto", tipo="exito", icono="💾")
        self.btn_guardar.clicked.connect(self._validar_y_guardar)
        
        botones_layout.addWidget(self.btn_cancelar)
        botones_layout.addWidget(self.btn_guardar)
        
        layout.addLayout(botones_layout)
    
    def _cargar_datos_producto(self):
        if not self.producto:
            return
        
        self.nombre_input.setText(self.producto['nombre'])
        self.categoria_combo.setCurrentText(self.producto['categoria'])
        self.material_combo.setCurrentText(self.producto['material'])
        self.peso_input.setValue(self.producto['peso'])
        self.precio_input.setValue(self.producto['precio'])
        self.stock_input.setValue(self.producto['cantidad'])
        self.proveedor_input.setText(self.producto['proveedor'])
        self.descripcion_input.setText(self.producto['descripcion'])
    
    def _validar_y_guardar(self):
        if not self.nombre_input.text().strip():
            QMessageBox.warning(self, "Validación", "El nombre del producto es obligatorio.")
            return
        
        self.accept()
    
    def obtener_datos(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre_input.text().strip(),
            "categoria": self.categoria_combo.currentText().strip(),
            "material": self.material_combo.currentText().strip(),
            "peso": self.peso_input.value(),
            "precio": self.precio_input.value(),
            "cantidad": self.stock_input.value(),
            "proveedor": self.proveedor_input.text().strip(),
            "descripcion": self.descripcion_input.toPlainText().strip()
        }

class DialogoEntradaMaterial(QDialog):
    def __init__(self, db: BaseDatos, material_data: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.material_data = material_data
        self.setWindowTitle("Agregar Material" if not material_data else "Editar Material")
        self.setFixedSize(350, 200)
        self.setStyleSheet(Estilos.obtener_stylesheet_general())
        self._crear_interfaz()
        if material_data:
            self.nombre_input.setText(material_data['nombre'])
            self.peso_input.setValue(material_data['peso'])
    
    def _crear_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        form = QFormLayout()
        form.setSpacing(10)
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del material")
        form.addRow("Material:", self.nombre_input)
        
        self.peso_input = QDoubleSpinBox()
        self.peso_input.setRange(0, 100000)
        self.peso_input.setSuffix(" g")
        self.peso_input.setDecimals(2)
        form.addRow("Peso:", self.peso_input)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
    
    def obtener_datos(self):
        return {
            "nombre": self.nombre_input.text().strip(),
            "peso": self.peso_input.value()
        }

class DialogoInventarioMateriales(QDialog):
    def __init__(self, db: BaseDatos, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Inventario de Materiales")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(Estilos.obtener_stylesheet_general())
        self._crear_interfaz()
        self._cargar_datos()
    
    def _crear_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        titulo = QLabel("📊 Inventario de Materiales (Stock Independiente)")
        titulo.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Colores.TEXTO_PRINCIPAL};")
        layout.addWidget(titulo)
        
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Material", "Peso Total (g)"])
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setAlternatingRowColors(False)
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.tabla)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_agregar = BotonAccion("Agregar", tipo="exito", icono="➕")
        self.btn_agregar.clicked.connect(self._agregar_material)
        
        self.btn_editar = BotonAccion("Modificar", tipo="advertencia", icono="✏️")
        self.btn_editar.clicked.connect(self._editar_material)
        self.btn_editar.setEnabled(False)
        
        self.btn_eliminar = BotonAccion("Eliminar", tipo="peligro", icono="🗑️")
        self.btn_eliminar.clicked.connect(self._eliminar_material)
        self.btn_eliminar.setEnabled(False)
        
        self.btn_cerrar = BotonAccion("Cerrar", tipo="primario")
        self.btn_cerrar.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cerrar)
        
        layout.addLayout(btn_layout)
        
        self.tabla.itemSelectionChanged.connect(self._verificar_seleccion)
    
    def _cargar_datos(self):
        materiales = self.db.obtener_materiales_inventario()
        self.tabla.setRowCount(len(materiales))
        for i, m in enumerate(materiales):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(m['id'])))
            self.tabla.setItem(i, 1, QTableWidgetItem(m['nombre']))
            self.tabla.setItem(i, 2, QTableWidgetItem(f"{m['peso']:.2f}"))
    
    def _verificar_seleccion(self):
        selected = self.tabla.currentRow() >= 0
        self.btn_editar.setEnabled(selected)
        self.btn_eliminar.setEnabled(selected)
    
    def _agregar_material(self):
        dialogo = DialogoEntradaMaterial(self.db, parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            if not datos['nombre']:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
                return
            
            if self.db.agregar_incrementar_material(datos['nombre'], datos['peso']):
                self._cargar_datos()
                QMessageBox.information(self, "Éxito", "Material agregado/incrementado correctamente.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo guardar el material.")
    
    def _editar_material(self):
        row = self.tabla.currentRow()
        if row < 0: return
        
        id_mat = int(self.tabla.item(row, 0).text())
        nombre = self.tabla.item(row, 1).text()
        peso = float(self.tabla.item(row, 2).text())
        
        dialogo = DialogoEntradaMaterial(self.db, {"id": id_mat, "nombre": nombre, "peso": peso}, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            if self.db.editar_material_inventario(id_mat, datos['nombre'], datos['peso']):
                self._cargar_datos()
                QMessageBox.information(self, "Éxito", "Material actualizado.")
    
    def _eliminar_material(self):
        row = self.tabla.currentRow()
        if row < 0: return
        
        id_mat = int(self.tabla.item(row, 0).text())
        nombre = self.tabla.item(row, 1).text()
        
        confirm = QMessageBox.question(self, "Confirmar", f"¿Eliminar el material '{nombre}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if self.db.eliminar_material_inventario(id_mat):
                self._cargar_datos()

class VentanaPrincipal(QMainWindow):
    def __init__(self, usuario: Dict[str, Any]):
        super().__init__()
        self.usuario = usuario
        self.db = BaseDatos()
        
        self._configurar_ventana()
        self._crear_interfaz()
        self._iniciar_timer_reloj()
        self._cargar_datos()
    
    def _configurar_ventana(self):
        self.setWindowTitle(f"{Config.APP_NAME} | {self.usuario['nombre']}")
        self.setMinimumSize(Config.MAIN_WINDOW_MIN_WIDTH, Config.MAIN_WINDOW_MIN_HEIGHT)
        self.setStyleSheet(Estilos.obtener_stylesheet_general())
    
    def _crear_interfaz(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        self._crear_barra_superior(layout)
        self._crear_tarjetas_estadisticas(layout)
        self._crear_area_principal(layout)
        
        self.statusBar().showMessage("Sistema listo, Bienvenido")
        self.statusBar().setStyleSheet(f"""
            background-color: {Colores.FONDO_PRINCIPAL};
            color: {Colores.TEXTO_SECUNDARIO};
            border-top: 1px solid {Colores.BORDE_NORMAL};
            padding: 4px 10px;
        """)
    
    def _crear_barra_superior(self, layout: QVBoxLayout):
        barra = QFrame()
        barra.setFixedHeight(60)
        barra.setStyleSheet(f"""
            QFrame {{
                background-color: {Colores.FONDO_TARJETA};
                border-radius: 12px;
                border: 1px solid {Colores.BORDE_NORMAL};
            }}
        """)
        
        barra_layout = QHBoxLayout(barra)
        barra_layout.setContentsMargins(20, 10, 20, 10)
        
        usuario_label = QLabel(f"👤  {self.usuario['nombre']}")
        usuario_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {Colores.TEXTO_PRINCIPAL};
        """)
        
        self.reloj_label = QLabel()
        self.reloj_label.setStyleSheet(f"""
            font-size: 15px;
            color: {Colores.TEXTO_SECUNDARIO};
            font-family: 'Consolas', 'Monaco', monospace;
        """)
        
        btn_salir = BotonAccion("Cerrar Sesión", tipo="peligro")
        btn_salir.clicked.connect(self.close)
        
        barra_layout.addWidget(usuario_label)
        barra_layout.addStretch()
        barra_layout.addWidget(self.reloj_label)
        barra_layout.addStretch()
        barra_layout.addWidget(btn_salir)
        
        layout.addWidget(barra)
    
    def _crear_tarjetas_estadisticas(self, layout: QVBoxLayout):
        grid = QGridLayout()
        grid.setSpacing(16)
        
        self.tarjeta_items = TarjetaEstadistica(
            "Total Items", "📦", Colores.AZUL_PRIMARIO, Colores.AZUL_FONDO
        )
        self.tarjeta_peso = TarjetaEstadistica(
            "Peso Total", "⚖️", Colores.AMARILLO_ADVERTENCIA, Colores.AMARILLO_FONDO
        )
        self.tarjeta_alertas = TarjetaEstadistica(
            "Alertas Stock", "⚠️", Colores.ROJO_ERROR, Colores.ROJO_FONDO
        )
        
        grid.addWidget(self.tarjeta_items, 0, 0)
        grid.addWidget(self.tarjeta_peso, 0, 1)
        grid.addWidget(self.tarjeta_alertas, 0, 2)
        
        layout.addLayout(grid)
    
    def _crear_area_principal(self, layout: QVBoxLayout):
        contenedor = QFrame()
        contenedor.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
            }}
        """)
        
        contenedor_layout = QVBoxLayout(contenedor)
        contenedor_layout.setSpacing(16)
        contenedor_layout.setContentsMargins(0, 0, 0, 0)
        
        self._crear_barra_herramientas(contenedor_layout)
        self.tabla = TablaInventario()
        self.tabla.itemSelectionChanged.connect(self._verificar_seleccion)
        self.tabla.doubleClicked.connect(self._editar_producto)
        
        contenedor_layout.addWidget(self.tabla)
        layout.addWidget(contenedor)
    
    def _crear_barra_herramientas(self, layout: QVBoxLayout):
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: transparent;")
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(12)
        
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText(" Buscar por nombre, categoría o material ")
        self.buscar_input.setMinimumHeight(45)
        self.buscar_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colores.FONDO_TARJETA};
                border: 2px solid {Colores.BORDE_NORMAL};
                border-radius: 12px;
                padding: 10px 18px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Colores.AZUL_PRIMARIO};
            }}
        """)
        self.buscar_input.textChanged.connect(self._filtrar_productos)
        
        toolbar_layout.addWidget(self.buscar_input, 2)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.btn_materiales = BotonAccion("Materiales", tipo="purpura", icono="📊")
        self.btn_materiales.clicked.connect(self._mostrar_inventario_materiales)
        btn_layout.addWidget(self.btn_materiales)

        self.btn_agregar = BotonAccion("Agregar", tipo="primario", icono="➕")
        self.btn_agregar.clicked.connect(self._agregar_producto)
        btn_layout.addWidget(self.btn_agregar)

        self.btn_editar = BotonAccion("Editar", tipo="advertencia", icono="✏️")
        self.btn_editar.clicked.connect(self._editar_producto)
        self.btn_editar.setEnabled(False)
        btn_layout.addWidget(self.btn_editar)

        self.btn_eliminar = BotonAccion("Eliminar", tipo="peligro", icono="🗑️")
        self.btn_eliminar.clicked.connect(self._eliminar_producto)
        self.btn_eliminar.setEnabled(False)
        btn_layout.addWidget(self.btn_eliminar)

        self.btn_exportar = BotonAccion("Exportar", tipo="primario", icono="📥")
        self.btn_exportar.clicked.connect(self._exportar_csv)
        btn_layout.addWidget(self.btn_exportar)
        
        toolbar_layout.addLayout(btn_layout, 3)
        layout.addWidget(toolbar)
    
    def _iniciar_timer_reloj(self):
        self._actualizar_reloj()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._actualizar_reloj)
        self.timer.start(1000)
    
    def _actualizar_reloj(self):
        locale = QLocale(QLocale.Language.Spanish)
        QLocale.setDefault(locale)
        ahora = QDateTime.currentDateTime()
        formato = ahora.toString("dddd, dd/MM/yyyy hh:mm:ss")
        if formato:
            formato = formato[0].upper() + formato[1:]
        self.reloj_label.setText(formato)

    def _cargar_datos(self):
        self._filtrar_productos()
    
    def _filtrar_productos(self):
        texto = self.buscar_input.text().strip()
        if texto:
            productos = self.db.buscar_productos(texto)
        else:
            productos = self.db.obtener_productos()
        self.tabla.cargar_productos(productos)
        self._actualizar_estadisticas()
    
    def _actualizar_estadisticas(self):
        stats = self.db.obtener_estadisticas_generales()
        self.tarjeta_items.establecer_valor(str(stats.get('total_items', 0)))
        self.tarjeta_peso.establecer_valor(f"{stats.get('peso_total', 0):.1f} g")
        self.tarjeta_alertas.establecer_valor(str(stats.get('bajo_stock', 0)))
    
    def _verificar_seleccion(self):
        hay_seleccion = self.tabla.currentRow() >= 0
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_eliminar.setEnabled(hay_seleccion)
    
    def _agregar_producto(self):
        dialogo = DialogoProducto(self.db, parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            if self.db.agregar_producto(datos):
                self._filtrar_productos()
                QMessageBox.information(self, "Éxito", "Producto agregado correctamente.")
    
    def _editar_producto(self):
        id_producto = self.tabla.obtener_id_seleccionado()
        if not id_producto:
            return
        
        producto = self.db.obtener_producto_por_id(id_producto)
        if producto:
            dialogo = DialogoProducto(self.db, producto, self)
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                datos = dialogo.obtener_datos()
                if self.db.actualizar_producto(id_producto, datos):
                    self._filtrar_productos()
                    QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo actualizar el producto.")
    
    def _eliminar_producto(self):
        id_producto = self.tabla.obtener_id_seleccionado()
        nombre = self.tabla.obtener_nombre_seleccionado()
        if not id_producto:
            return
        
        confirmacion = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el producto '{nombre}'?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmacion == QMessageBox.StandardButton.Yes:
            if self.db.eliminar_producto(id_producto):
                self._filtrar_productos()
                QMessageBox.information(self, "Eliminado", "Producto eliminado correctamente.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el producto.")
    
    def _mostrar_inventario_materiales(self):
        dialogo = DialogoInventarioMateriales(self.db, self)
        dialogo.exec()
    
    def _exportar_csv(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Copia de Seguridad",
            f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "Archivos CSV (*.csv)"
        )
        
        if not ruta:
            return
        
        try:
            with open(ruta, 'w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                headers = []
                for col in range(self.tabla.columnCount()):
                    header = self.tabla.horizontalHeaderItem(col)
                    headers.append(header.text() if header else f"Col_{col}")
                writer.writerow(headers)
                
                for row in range(self.tabla.rowCount()):
                    fila_datos = []
                    for col in range(self.tabla.columnCount()):
                        item = self.tabla.item(row, col)
                        fila_datos.append(item.text() if item else '')
                    writer.writerow(fila_datos)
            
            QMessageBox.information(self, "Exportado", f"Datos exportados correctamente a:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar los datos:\n{str(e)}")

    def closeEvent(self, event):
        self.db.cerrar()
        event.accept()

def main():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    try:
        login = VentanaLogin()
        pantalla = app.primaryScreen().geometry()
        x = (pantalla.width() - login.width()) // 2
        y = (pantalla.height() - login.height()) // 2
        login.move(x, y)
        
        if login.exec() == QDialog.DialogCode.Accepted:
            ventana = VentanaPrincipal(login.usuario_actual)
            ventana.show()
            sys.exit(app.exec())
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"Error fatal: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
