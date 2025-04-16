import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QHBoxLayout,
                             QLineEdit, QTextEdit, QCheckBox, QComboBox, QFrame)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect, QTimer, pyqtProperty
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QFont, QFontMetrics


class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurações
        self._size = 64
        self._progress = 0
        self._max_progress = 100
        self._line_width = 5
        self._animation_duration = 1000
        
        # Cores
        self._active_color = QColor("#007ACC")
        self._background_color = QColor("#3E3E42")
        self._text_color = QColor("#FFFFFF")
        
        # Configurar tamanho mínimo
        self.setMinimumSize(self._size, self._size)
        
        # Temporizador para a animação
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_animation)
        self._animated_progress = 0
        self._target_progress = 0
        
    def _update_animation(self):
        if abs(self._animated_progress - self._target_progress) < 0.5:
            self._animated_progress = self._target_progress
            self._timer.stop()
        else:
            # Acelerar ou desacelerar de acordo com a distância
            delta = (self._target_progress - self._animated_progress) / 10.0
            self._animated_progress += delta
        
        self.update()  # Redesenhar o widget
    
    def sizeHint(self):
        return QSize(self._size, self._size)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calcular o retângulo para desenhar o círculo
        rect = event.rect()
        width = rect.width()
        height = rect.height()
        size = min(width, height)
        
        # Centralizar o círculo
        x = (width - size) // 2
        y = (height - size) // 2
        
        # Desenhar círculo de fundo
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._background_color)
        painter.drawEllipse(x + self._line_width//2, y + self._line_width//2, 
                           size - self._line_width, size - self._line_width)
        
        # Desenhar arco de progresso
        pen = QPen(self._active_color)
        pen.setWidth(self._line_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        # Calcular ângulos em graus
        start_angle = 90 * 16  # Começa em 90 graus (topo)
        span_angle = -int(360 * 16 * self._animated_progress / self._max_progress)
        
        # Ajustar retângulo para linha de progresso
        adjusted_size = size - self._line_width
        painter.drawArc(x + self._line_width//2, y + self._line_width//2, 
                      adjusted_size, adjusted_size, 
                      start_angle, span_angle)
        
        # Desenhar texto com o percentual
        percentage = int(self._animated_progress)
        painter.setPen(self._text_color)
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        
        text = f"{percentage}%"
        metrics = QFontMetrics(font)
        text_width = metrics.width(text)
        text_height = metrics.height()
        
        painter.drawText((width - text_width) // 2, 
                       (height + text_height) // 2 - 2, text)
        
    def get_progress(self):
        return self._progress
    
    def set_progress(self, value):
        self._progress = max(0, min(value, self._max_progress))
        self._target_progress = self._progress
        
        # Iniciar animação
        if not self._timer.isActive():
            self._timer.start(16)  # ~60 FPS
        
        self.update()
    
    # Definir uma propriedade para uso em animações
    progress = pyqtProperty(float, get_progress, set_progress)


class ExpandableSidebar(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configurar a janela como uma barra lateral
        self.setWindowTitle("Barra Lateral Expansível")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Define tamanho e posição inicial
        screen_geometry = QApplication.desktop().screenGeometry()
        self.sidebar_collapsed_width = 80
        self.sidebar_expanded_width = 300
        self.sidebar_height = screen_geometry.height() // 2
        
        # Valores para controlar a posição corretamente
        self.screen_width = screen_geometry.width()
        self.right_margin = 10  # Margem da direita em pixels
        
        # Iniciar com a barra recolhida
        self.is_expanded = False
        
        # Calcular posição inicial (garantindo que a borda direita esteja fixa)
        self.x_collapsed = self.screen_width - self.sidebar_collapsed_width - self.right_margin
        self.x_expanded = self.screen_width - self.sidebar_expanded_width - self.right_margin
        self.y_position = (screen_geometry.height() - self.sidebar_height) // 2
        
        # Definir geometria inicial
        self.setGeometry(self.x_collapsed, self.y_position, 
                         self.sidebar_collapsed_width, self.sidebar_height)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout horizontal principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Widget da barra de ícones (sempre visível)
        self.icons_bar = QWidget()
        self.icons_bar.setFixedWidth(self.sidebar_collapsed_width)
        icons_layout = QVBoxLayout(self.icons_bar)
        icons_layout.setContentsMargins(5, 10, 5, 10)
        icons_layout.setSpacing(10)
        
        # Título da barra
        title_label = QLabel("Menu")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        icons_layout.addWidget(title_label)
        
        # Botões na barra de ícones
        self.btn_files = self.create_sidebar_button("Arquivos", "SP_FileIcon")
        self.btn_files.clicked.connect(lambda: self.on_button_clicked(0))
        icons_layout.addWidget(self.btn_files)
        
        self.btn_edit = self.create_sidebar_button("Editar", "SP_FileDialogContentsView")
        self.btn_edit.clicked.connect(lambda: self.on_button_clicked(1))
        icons_layout.addWidget(self.btn_edit)
        
        self.btn_settings = self.create_sidebar_button("Opções", "SP_DialogApplyButton")
        self.btn_settings.clicked.connect(lambda: self.on_button_clicked(2))
        icons_layout.addWidget(self.btn_settings)
        
        self.btn_help = self.create_sidebar_button("Ajuda", "SP_DialogHelpButton")
        self.btn_help.clicked.connect(lambda: self.on_button_clicked(3))
        icons_layout.addWidget(self.btn_help)
        
        # Adicionar o Progress Bar Circular
        self.progress_bar = CircularProgressBar()
        icons_layout.addWidget(self.progress_bar, 0, Qt.AlignCenter)
        
        # Botão para incrementar progresso em 5%
        self.btn_increment_progress = self.create_sidebar_button("Avançar", "SP_MediaPlay")
        self.btn_increment_progress.clicked.connect(self.increment_progress)
        icons_layout.addWidget(self.btn_increment_progress)
        
        # Expandir/Recolher botão
        icons_layout.addStretch()
        self.btn_expand = self.create_sidebar_button("Expandir", "SP_ArrowRight")
        self.btn_expand.clicked.connect(self.toggle_sidebar)
        icons_layout.addWidget(self.btn_expand)
        
        # Botão para fechar
        self.btn_close = self.create_sidebar_button("Fechar", "SP_TitleBarCloseButton")
        self.btn_close.clicked.connect(self.close)
        icons_layout.addWidget(self.btn_close)
        
        # Widget de conteúdo expandido (painéis)
        self.content_widget = QWidget()
        self.content_widget.setFixedWidth(self.sidebar_expanded_width - self.sidebar_collapsed_width)
        self.content_widget.setVisible(False)  # Inicialmente oculto
        
        # Criar um layout para o conteúdo
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 10, 10, 10)
        
        # Criar um widget empilhado para alternar entre diferentes conteúdos
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Adicionar diferentes páginas ao stacked widget
        # Página 1: Arquivos
        files_page = QWidget()
        files_layout = QVBoxLayout(files_page)
        files_layout.addWidget(QLabel("<b>Arquivos</b>"))
        files_layout.addWidget(QLabel("Diretório:"))
        files_path = QLineEdit()
        files_path.setPlaceholderText("/caminho/para/diretório")
        files_layout.addWidget(files_path)
        files_layout.addWidget(QPushButton("Navegar..."))
        files_layout.addWidget(QCheckBox("Incluir subdiretórios"))
        files_layout.addWidget(QCheckBox("Somente leitura"))
        files_layout.addStretch()
        self.stacked_widget.addWidget(files_page)
        
        # Página 2: Editar
        edit_page = QWidget()
        edit_layout = QVBoxLayout(edit_page)
        edit_layout.addWidget(QLabel("<b>Editor</b>"))
        edit_layout.addWidget(QTextEdit())
        edit_layout.addWidget(QPushButton("Aplicar Mudanças"))
        self.stacked_widget.addWidget(edit_page)
        
        # Página 3: Opções
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.addWidget(QLabel("<b>Configurações</b>"))
        settings_layout.addWidget(QLabel("Tema:"))
        themes_combo = QComboBox()
        themes_combo.addItems(["Claro", "Escuro", "Sistema"])
        settings_layout.addWidget(themes_combo)
        settings_layout.addWidget(QLabel("Idioma:"))
        lang_combo = QComboBox()
        lang_combo.addItems(["Português", "English", "Español"])
        settings_layout.addWidget(lang_combo)
        settings_layout.addWidget(QCheckBox("Iniciar com o sistema"))
        settings_layout.addWidget(QCheckBox("Verificar atualizações"))
        settings_layout.addStretch()
        self.stacked_widget.addWidget(settings_page)
        
        # Página 4: Ajuda
        help_page = QWidget()
        help_layout = QVBoxLayout(help_page)
        help_layout.addWidget(QLabel("<b>Ajuda</b>"))
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setText("Esta é uma barra lateral expansível de exemplo.\n\n"
                         "Clique nos ícones à esquerda para navegar entre diferentes seções.\n\n"
                         "Você pode expandir e recolher esta barra clicando no botão 'Expandir'.")
        help_layout.addWidget(help_text)
        help_layout.addWidget(QPushButton("Verificar Atualizações"))
        help_layout.addWidget(QPushButton("Sobre"))
        self.stacked_widget.addWidget(help_page)
        
        # Adicionar widgets ao layout principal
        main_layout.addWidget(self.icons_bar)
        main_layout.addWidget(self.content_widget)
        
        # Separador entre barra de ícones e conteúdo
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.separator.setFixedWidth(1)
        self.separator.setVisible(False)  # Inicialmente oculto
        main_layout.insertWidget(1, self.separator)
        
        # Estilizar a janela
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D30;
                border: 1px solid #3E3E42;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #3E3E42;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #505054;
            }
            QPushButton:pressed {
                background-color: #007ACC;
            }
            QLabel {
                color: white;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #252526;
                color: white;
                border: 1px solid #3E3E42;
                border-radius: 3px;
                padding: 3px;
            }
            QCheckBox {
                color: white;
            }
            QFrame {
                color: #3E3E42;
            }
        """)
        
        # Permitir mover a janela com o mouse
        self.oldPos = None
    
    def increment_progress(self):
        # Obter o progresso atual
        current_progress = self.progress_bar.get_progress()
        
        # Incrementar em 5%
        new_progress = current_progress + 5
        
        # Resetar para 0 se ultrapassar 100%
        if new_progress > 100:
            new_progress = 0
            
        # Atualizar a barra de progresso
        self.progress_bar.set_progress(new_progress)
    
    def create_sidebar_button(self, tooltip, icon_name):
        button = QPushButton("")
        
        # Obter o ícone do sistema
        icon_attr = getattr(self.style(), icon_name, None)
        if icon_attr:
            button.setIcon(self.style().standardIcon(icon_attr))
        
        button.setIconSize(QSize(24, 24))
        button.setToolTip(tooltip)
        button.setMinimumHeight(40)
        return button
    
    def toggle_sidebar(self):
        # Inverter o estado de expansão
        self.is_expanded = not self.is_expanded
        
        # Atualizar botão de expansão
        if self.is_expanded:
            self.btn_expand.setIcon(self.style().standardIcon(self.style().SP_ArrowLeft))
            self.content_widget.setVisible(True)
            self.separator.setVisible(True)
            target_width = self.sidebar_expanded_width
            target_x = self.x_expanded
        else:
            self.btn_expand.setIcon(self.style().standardIcon(self.style().SP_ArrowRight))
            self.content_widget.setVisible(False)
            self.separator.setVisible(False)
            target_width = self.sidebar_collapsed_width
            target_x = self.x_collapsed
        
        # Animar a mudança de geometria
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(
            target_x,
            self.y_position,
            target_width,
            self.sidebar_height
        ))
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
    
    def on_button_clicked(self, index):
        # Mudar para a página correspondente e expandir se necessário
        if not self.is_expanded:
            self.toggle_sidebar()
        self.stacked_widget.setCurrentIndex(index)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
            
            # Atualizar as posições de referência quando a janela é movida
            if self.is_expanded:
                self.x_expanded = self.x()
                self.x_collapsed = self.x_expanded + (self.sidebar_expanded_width - self.sidebar_collapsed_width)
            else:
                self.x_collapsed = self.x()
                self.x_expanded = self.x_collapsed - (self.sidebar_expanded_width - self.sidebar_collapsed_width)
            
            self.y_position = self.y()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = None
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    sidebar = ExpandableSidebar()
    sidebar.show()
    sys.exit(app.exec_())
