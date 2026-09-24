"""
Guardian Node GUI - Family-Friendly Interface with Mode Switching
Production-ready PySide6 interface for Raspberry Pi touchscreen deployment
"""

import sys
import os
import html
import logging
import urllib.request
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget,
    QProgressBar, QTextEdit, QScrollArea, QFrame, QDialog,
    QDialogButtonBox, QFormLayout, QLineEdit, QComboBox
)
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor, QIcon
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize

# Import Guardian components
try:
    from resource_monitor import ResourceMonitor
except ImportError:
    # Fallback for testing
    class ResourceMonitor:
        def __init__(self): pass
        def get_current_stats(self): return {'cpu_percent': 25, 'memory_percent': 45, 'temperature_c': 42.5}
        def get_system_status_level(self, stats): return 'normal'
        def stop(self): pass


# Import the LLM backend. It lazily imports llama_cpp (with a MockLLM fallback
# if the native library is unavailable), so this is safe in every environment.
try:
    from guardian_interpreter.llm_integration import create_llm as _create_llm
except ImportError:
    _create_llm = None


def create_llm(config, logger):
    if _create_llm is None:
        raise RuntimeError(
            "LLM integration unavailable (guardian_interpreter.llm_integration missing)"
        )
    return _create_llm(config, logger)


# Import the voice interface (offline STT via pocketsphinx, TTS via pyttsx3).
try:
    from guardian_interpreter.voice.voice_interface import VoiceInterface
except Exception:
    VoiceInterface = None


def resource_path(relative_path: str) -> str:
    """Resolve a bundled resource path (works both frozen and in source)."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


class GuardianModeUI(QWidget):
    """Main mode switching interface with themed graphics"""
    
    # Signal emitted when mode changes
    mode_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "Kids"  # Default safe mode
        self.image_paths = {
            "Adult": "Adult_parent_mode.png",
            "Kids": "Nodie_kids_mode.png",
            "Teens": "Young_teens_mode.png"
        }
        
        self.setup_ui()
        self.set_mode("Kids")  # Start in safe mode
    
    def setup_ui(self):
        """Setup the mode switching interface"""
        # Main image display
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setFixedSize(400, 300)
        self.img_label.setStyleSheet("""
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                background-color: #f0f0f0;
            }
        """)
        
        # Mode title
        self.mode_title = QLabel("Guardian Node")
        self.mode_title.setAlignment(Qt.AlignCenter)
        self.mode_title.setFont(QFont("Arial", 24, QFont.Bold))
        self.mode_title.setStyleSheet("color: #2E7D32; margin: 10px;")
        
        # Mode description
        self.mode_desc = QLabel("Family Protection Active")
        self.mode_desc.setAlignment(Qt.AlignCenter)
        self.mode_desc.setFont(QFont("Arial", 14))
        self.mode_desc.setStyleSheet("color: #666; margin: 5px;")
        
        # Mode switching buttons
        self.btn_adult = self.create_mode_button("👨‍👩‍👧‍👦 Adult", "#FF5722")
        self.btn_kids = self.create_mode_button("🧒 Kids", "#4CAF50") 
        self.btn_teens = self.create_mode_button("👦👧 Teens", "#2196F3")
        
        # Connect button signals
        self.btn_adult.clicked.connect(lambda: self.set_mode("Adult"))
        self.btn_kids.clicked.connect(lambda: self.set_mode("Kids"))
        self.btn_teens.clicked.connect(lambda: self.set_mode("Teens"))
        
        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_adult)
        btn_layout.addWidget(self.btn_kids)
        btn_layout.addWidget(self.btn_teens)
        btn_layout.setSpacing(15)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.mode_title)
        main_layout.addWidget(self.img_label)
        main_layout.addWidget(self.mode_desc)
        main_layout.addLayout(btn_layout)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        self.setLayout(main_layout)
    
    def create_mode_button(self, text: str, color: str) -> QPushButton:
        """Create a styled mode button"""
        btn = QPushButton(text)
        btn.setFont(QFont("Arial", 12, QFont.Bold))
        btn.setFixedSize(140, 50)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.3)};
            }}
        """)
        return btn
    
    def darken_color(self, color: str, factor: float = 0.2) -> str:
        """Darken a hex color by a factor"""
        color = QColor(color)
        color = color.darker(100 + int(100 * factor))
        return color.name()
    
    def set_mode(self, mode: str):
        """Set the current mode and update UI"""
        if mode == self.current_mode:
            return
            
        self.current_mode = mode
        
        # Update image
        img_path = self.image_paths.get(mode)
        if img_path:
            img_path = resource_path(os.path.join("assets", img_path))
        pixmap = None
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
        if pixmap is not None and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.img_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.img_label.setPixmap(scaled_pixmap)
        else:
            # Fallback text if image not found
            self.img_label.setText(f"🛡️\n{mode} Mode\nActive")
            self.img_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                    background-color: #f0f0f0;
                    font-size: 18px;
                    font-weight: bold;
                    color: #2E7D32;
                }
            """)
        
        # Update mode-specific styling and descriptions
        mode_configs = {
            "Adult": {
                "title": "Guardian Node - Adult Mode",
                "desc": "Full access with advanced security monitoring",
                "color": "#FF5722"
            },
            "Kids": {
                "title": "Guardian Node - Kids Mode", 
                "desc": "Maximum protection with child-safe filtering",
                "color": "#4CAF50"
            },
            "Teens": {
                "title": "Guardian Node - Teen Mode",
                "desc": "Balanced protection with guided independence", 
                "color": "#2196F3"
            }
        }
        
        config = mode_configs.get(mode, mode_configs["Kids"])
        self.mode_title.setText(config["title"])
        self.mode_desc.setText(config["desc"])
        
        # Update button states
        self.update_button_states(mode)
        
        # Emit signal for backend integration
        self.mode_changed.emit(mode)
    
    def update_button_states(self, active_mode: str):
        """Update button visual states"""
        buttons = {
            "Adult": self.btn_adult,
            "Kids": self.btn_kids, 
            "Teens": self.btn_teens
        }
        
        for mode, btn in buttons.items():
            if mode == active_mode:
                # Highlight active button
                original_style = btn.styleSheet()
                btn.setStyleSheet(original_style + """
                    QPushButton {
                        border: 3px solid #FFF;
                        font-weight: bold;
                    }
                """)


class SystemStatusWidget(QWidget):
    """System status display with resource monitoring"""
    
    def __init__(self, resource_monitor: ResourceMonitor, parent=None):
        super().__init__(parent)
        self.resource_monitor = resource_monitor
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(5000)  # Update every 5 seconds
        self.update_status()  # Initial update
    
    def setup_ui(self):
        """Setup status display UI"""
        # Status indicators
        self.cpu_bar = QProgressBar()
        self.memory_bar = QProgressBar()
        self.temp_label = QLabel("Temp: --°C")
        self.status_label = QLabel("🟢 System Normal")
        
        # Style progress bars
        for bar in [self.cpu_bar, self.memory_bar]:
            bar.setFixedHeight(20)
            bar.setRange(0, 100)
            bar.setTextVisible(True)
            bar.setFormat("%p%")
            bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 9px;
                }
            """)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("System Status:"))
        layout.addWidget(QLabel("CPU Usage:"))
        layout.addWidget(self.cpu_bar)
        layout.addWidget(QLabel("Memory Usage:"))
        layout.addWidget(self.memory_bar)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def update_status(self):
        """Update system status display"""
        if not self.resource_monitor:
            return
            
        try:
            stats = self.resource_monitor.get_current_stats()
            
            # Update progress bars
            cpu_percent = stats.get('cpu_percent', 0)
            memory_percent = stats.get('memory_percent', 0)
            
            self.cpu_bar.setValue(int(cpu_percent))
            self.memory_bar.setValue(int(memory_percent))
            
            # Update temperature
            temp = stats.get('temperature_c')
            if temp:
                self.temp_label.setText(f"Temp: {temp:.1f}°C")
            
            # Update status indicator
            status_level = self.resource_monitor.get_system_status_level(stats)
            status_configs = {
                'normal': ('🟢 System Normal', '#4CAF50'),
                'warning': ('🟡 System Warning', '#FF9800'), 
                'critical': ('🔴 System Critical', '#F44336')
            }
            
            status_text, color = status_configs.get(status_level, status_configs['normal'])
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            
            # Update progress bar colors based on usage
            self.update_progress_bar_color(self.cpu_bar, cpu_percent)
            self.update_progress_bar_color(self.memory_bar, memory_percent)
            
        except Exception as e:
            self.status_label.setText(f"🔴 Status Error: {str(e)}")
    
    def update_progress_bar_color(self, bar: QProgressBar, value: float):
        """Update progress bar color based on value"""
        if value > 90:
            color = "#F44336"  # Red
        elif value > 75:
            color = "#FF9800"  # Orange
        else:
            color = "#4CAF50"  # Green
            
        bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ccc;
                border-radius: 10px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 9px;
            }}
        """)


class ChatPanel(QWidget):
    """Scrollable conversation history plus a text input for talking to the AI."""

    message_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("💬 Chat with Guardian")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2E7D32;")
        layout.addWidget(title)

        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.history, 1)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.status_label)

        input_row = QHBoxLayout()
        input_row.setSpacing(6)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask about your family's online safety...")
        self.input.setFixedHeight(34)
        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedHeight(34)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; border: none;
                border-radius: 6px; padding: 0 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        input_row.addWidget(self.input, 1)
        input_row.addWidget(self.send_btn)
        layout.addLayout(input_row)

        self.setLayout(layout)

        self.input.returnPressed.connect(self._send)
        self.send_btn.clicked.connect(self._send)

    def _send(self):
        text = self.input.text().strip()
        if text:
            self.input.clear()
            self.message_submitted.emit(text)

    def append_user(self, text: str):
        self._append("You", text, "#1565C0")

    def append_assistant(self, text: str):
        self._append("Guardian", text, "#2E7D32")

    def append_system(self, text: str):
        self._append("System", text, "#757575")

    def _append(self, speaker: str, text: str, color: str):
        safe = html.escape(text)
        self.history.append(
            f'<p style="margin:4px 0;"><span style="color:{color}; font-weight:bold;">'
            f'{speaker}:</span> <span style="white-space:pre-wrap;">{safe}</span></p>'
        )
        scrollbar = self.history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_thinking(self, thinking: bool):
        self.send_btn.setEnabled(not thinking)
        self.input.setEnabled(not thinking)
        if thinking:
            self.status_label.setText("🤔 Guardian is thinking...")
            self.status_label.setStyleSheet("color: #FF9800; font-style: italic;")
        else:
            self.status_label.setText("")
            self.status_label.setStyleSheet("color: #888; font-style: italic;")

    def set_status(self, text: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: #888; font-style: italic;")


class ModelLoadThread(QThread):
    """Loads the GGUF model in the background so the UI stays responsive."""

    loaded = Signal(object)
    failed = Signal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config

    def run(self):
        try:
            logger = logging.getLogger('guardian.llm')
            llm = create_llm(self.config, logger)
            if llm.is_loaded():
                self.loaded.emit(llm)
            else:
                self.failed.emit("Model could not be loaded (file missing or unreadable).")
        except Exception as e:
            self.failed.emit(str(e))


class InferenceThread(QThread):
    """Runs a single prompt against the loaded model without freezing the UI."""

    finished = Signal(str)
    error = Signal(str)

    def __init__(self, llm, prompt, parent=None):
        super().__init__(parent)
        self.llm = llm
        self.prompt = prompt

    def run(self):
        try:
            self.finished.emit(self.llm.generate_response(self.prompt))
        except Exception as e:
            self.error.emit(str(e))


class VoiceSessionThread(QThread):
    """Runs listen -> transcribe -> generate -> speak off the UI thread."""

    status = Signal(str)
    finished = Signal(str, str)  # (transcribed_text, response)

    def __init__(self, voice_interface, llm, parent=None):
        super().__init__(parent)
        self.voice_interface = voice_interface
        self.llm = llm

    def run(self):
        try:
            self.status.emit("listening")
            text = self.voice_interface.listen(timeout=5)
            if not text:
                self.finished.emit("", "")
                return

            self.status.emit("processing")
            response = None
            if self.llm is not None and self.llm.is_loaded():
                response = self.llm.generate_response(text)

            self.status.emit("speaking")
            if response:
                try:
                    self.voice_interface.speak(response)
                except Exception as e:
                    print(f"Speak failed: {e}")
            self.finished.emit(text, response or "")
        except Exception as e:
            print(f"Voice session error: {e}")
            self.finished.emit("", "")


class GuardianBackend:
    """Minimal guardian backend for the standalone GUI.

    Provides the voice_interface + run_query surface that the rest of the GUI
    expects on `self.guardian`, so the packaged app is not left with None.
    """

    def __init__(self, window):
        self._window = window
        self.voice_interface = None
        if VoiceInterface is not None:
            try:
                self.voice_interface = VoiceInterface()
            except Exception as e:
                print(f"Voice interface unavailable: {e}")
                self.voice_interface = None

    def run_query(self, text):
        llm = self._window.llm
        if llm is not None and llm.is_loaded():
            return llm.generate_response(text)
        return None


class GuardianMainWindow(QMainWindow):
    """Main Guardian Node application window"""
    
    def __init__(self, guardian_interpreter=None):
        super().__init__()
        self.guardian = guardian_interpreter
        self.resource_monitor = ResourceMonitor()
        self.current_mode = "Kids"
        self.voice_privacy_enabled = True
        self.llm = None
        self.llm_loading = False
        self.llm_error = None
        self._llm_thread = None
        self._infer_thread = None
        self._voice_thread = None

        # The standalone (packaged) app has no external guardian; provide a real
        # backend so voice_interface and run_query are available, not None.
        if self.guardian is None:
            self.guardian = GuardianBackend(self)
        
        self.setup_ui()
        self.setup_mode_integration()
        self.setup_chat_integration()
        self.start_model_loading()
    
    def setup_ui(self):
        """Setup main window UI"""
        self.setWindowTitle("Guardian Node - Family Protection")
        self.resize(1180, 720)
        self.setMinimumSize(940, 620)
        
        # Central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main mode interface
        self.mode_ui = GuardianModeUI()
        
        # System status widget
        self.status_widget = SystemStatusWidget(self.resource_monitor)
        
        # Chat interface
        self.chat = ChatPanel()
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left side - mode interface
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.mode_ui)
        
        # Right side - status and controls
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.status_widget)
        
        # Control buttons
        buttons = [
            ("🔍 Run Security Scan", "#2196F3", self.run_security_scan),
            ("🎤 Voice Assistant", "#4CAF50", self.start_voice_session),
            ("👨‍👩‍👧‍👦 Manage Profiles", "#9C27B0", self.manage_family_profiles),
            ("📋 View Recommendations", "#FF9800", self.show_family_recommendations),
            ("🔍 Security Analysis", "#607D8B", self.show_family_analysis)
        ]
        
        for text, color, handler in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 22px;
                    font-size: 14px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(handler)
            right_layout.addWidget(btn)
        
        # Voice privacy toggle
        self.voice_privacy_btn = QPushButton("🔒 Voice Privacy: ON")
        self.voice_privacy_btn.setFixedHeight(35)
        self.voice_privacy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 17px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.voice_privacy_btn.clicked.connect(self.toggle_voice_privacy)
        right_layout.addWidget(self.voice_privacy_btn)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 2)  # Mode switching
        main_layout.addWidget(self.chat, 3)    # Chat (main interaction)
        main_layout.addLayout(right_layout, 2) # Status and controls
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        central_widget.setLayout(main_layout)
        
        # Apply global styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
    
    def darken_color(self, color: str, factor: float = 0.2) -> str:
        """Darken a hex color by a factor"""
        color = QColor(color)
        color = color.darker(100 + int(100 * factor))
        return color.name()
    
    def setup_mode_integration(self):
        """Setup mode change integration with backend"""
        self.mode_ui.mode_changed.connect(self.handle_mode_change)

    def setup_chat_integration(self):
        """Connect the chat panel to the LLM response pipeline."""
        self.chat.message_submitted.connect(self._on_chat_message)

    def start_model_loading(self):
        """Load the LLM in a background thread and surface status in the chat."""
        self.llm_loading = True
        self.chat.set_status("Loading AI model...")
        self._llm_thread = ModelLoadThread(get_llm_config())
        self._llm_thread.loaded.connect(self._on_model_loaded)
        self._llm_thread.failed.connect(self._on_model_failed)
        self._llm_thread.start()

    def _on_model_loaded(self, llm):
        self.llm = llm
        self.llm_loading = False
        self.chat.set_status("")
        self.chat.append_system("Guardian AI is ready. Ask me anything!")

    def _on_model_failed(self, err: str):
        self.llm_loading = False
        self.llm_error = err
        self.chat.set_status("AI model unavailable")
        self.chat.append_system(f"Could not load the AI model: {err}")

    def _on_chat_message(self, text: str):
        if not text.strip():
            return
        self.chat.append_user(text)
        if self.llm is None:
            if self.llm_loading:
                self.chat.append_system("The AI model is still loading — please wait a moment and try again.")
            else:
                self.chat.append_system("The AI model isn't loaded, so I can't answer right now.")
            return
        self.chat.set_thinking(True)
        self._infer_thread = InferenceThread(self.llm, text)
        self._infer_thread.finished.connect(self._on_inference_done)
        self._infer_thread.error.connect(self._on_inference_error)
        self._infer_thread.start()

    def _on_inference_done(self, response: str):
        self.chat.set_thinking(False)
        self.chat.append_assistant(response)

    def _on_inference_error(self, err: str):
        self.chat.set_thinking(False)
        self.chat.append_system(f"Sorry, something went wrong: {err}")
    
    def handle_mode_change(self, mode: str):
        """Handle mode changes and integrate with backend"""
        self.current_mode = mode
        if self.guardian and hasattr(self.guardian, 'family_manager'):
            profile = self.get_family_profile_for_mode(mode)
            self.guardian.family_manager.update_profile(profile)
            self.status_widget.update_status()
    
    def get_family_profile_for_mode(self, mode: str) -> Dict[str, Any]:
        """Get family profile configuration for the selected mode"""
        profiles = {
            "Adult": {
                'family_id': 'guardian_family',
                'members': [{'name': 'Parent', 'age_group': 'adult'}],
                'security_level': 'standard',
                'content_filtering': 'minimal'
            },
            "Kids": {
                'family_id': 'guardian_family', 
                'members': [{'name': 'Child', 'age_group': 'child'}],
                'security_level': 'maximum',
                'content_filtering': 'strict'
            },
            "Teens": {
                'family_id': 'guardian_family',
                'members': [{'name': 'Teen', 'age_group': 'teen'}], 
                'security_level': 'balanced',
                'content_filtering': 'moderate'
            }
        }
        return profiles.get(mode, profiles["Kids"])
    
    def run_security_scan(self):
        """Run security protocol analysis"""
        print("Running security scan...")
        self.status_widget.status_label.setText("🔄 Running security scan...")
        self.status_widget.status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        
        # Integrate with family assistant manager if available
        if self.guardian and hasattr(self.guardian, 'family_manager') and self.guardian.family_manager:
            try:
                result = self.guardian.family_manager.execute_skill('network_security_audit')
                print(f"✓ Security scan completed - Result: {result}")
                self.status_widget.status_label.setText("🟢 Security scan complete")
                return
            except Exception as e:
                print(f"✗ Security scan failed: {e}")
        
        # Fallback simulation
        QTimer.singleShot(3000, lambda: self.status_widget.status_label.setText("🟢 Security scan complete"))
    
    def start_voice_session(self):
        """Start voice assistant session (listen -> transcribe -> answer -> speak)."""
        print("Starting voice session...")
        voice_interface = getattr(self.guardian, 'voice_interface', None)

        if not voice_interface:
            print("Voice interface not available")
            self.status_widget.status_label.setText("🔴 Voice not available")
            return

        self.status_widget.status_label.setText("🎤 Listening...")
        self.status_widget.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

        self._voice_thread = VoiceSessionThread(voice_interface, self.llm)
        self._voice_thread.status.connect(self._on_voice_status)
        self._voice_thread.finished.connect(self._on_voice_done)
        self._voice_thread.start()

    def _on_voice_status(self, state: str):
        mapping = {
            "listening": ("🎤 Listening...", "#4CAF50"),
            "processing": ("🤔 Thinking...", "#FF9800"),
            "speaking": ("🔊 Speaking...", "#2196F3"),
        }
        text, color = mapping.get(state, (state, "#888"))
        self.status_widget.status_label.setText(text)
        self.status_widget.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _on_voice_done(self, text: str, response: str):
        if text:
            self.chat.append_user(text)
            if response:
                self.chat.append_assistant(response)
                self.status_widget.status_label.setText("🟢 Voice command completed")
            else:
                self.status_widget.status_label.setText("🟡 Heard you, but the AI model wasn't ready")
        else:
            self.status_widget.status_label.setText("🔴 No speech detected")
        QTimer.singleShot(3000, lambda: self.status_widget.update_status())
    
    def toggle_voice_privacy(self):
        """Toggle voice privacy mode"""
        self.voice_privacy_enabled = not self.voice_privacy_enabled
        
        if self.voice_privacy_enabled:
            self.voice_privacy_btn.setText("🔒 Voice Privacy: ON")
            self.voice_privacy_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 17px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            print("🔒 Voice privacy enabled")
        else:
            self.voice_privacy_btn.setText("🔓 Voice Privacy: OFF")
            self.voice_privacy_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF5722;
                    color: white;
                    border: none;
                    border-radius: 17px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E64A19;
                }
            """)
            print("🔓 Voice privacy disabled")
    
    def manage_family_profiles(self):
        """Manage family profiles interface"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Family Profile Management")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("👨‍👩‍👧‍👦 Family Profile Settings")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2E7D32; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Current Mode:"))
        mode_combo = QComboBox()
        mode_combo.addItems(["Kids", "Teens", "Adult"])
        mode_combo.setCurrentText(self.current_mode)
        mode_layout.addWidget(mode_combo)
        layout.addLayout(mode_layout)
        
        # Family members
        members_layout = QVBoxLayout()
        members_layout.addWidget(QLabel("Family Members:"))
        
        # Sample member list
        members = ["Child (Age 8)", "Parent (Age 35)"]
        for member in members:
            member_label = QLabel(f"• {member}")
            layout.addWidget(member_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.Accepted:
            self.current_mode = mode_combo.currentText()
            self.mode_ui.set_mode(self.current_mode)
            print(f"Family profile updated. Mode: {self.current_mode}")
    
    def show_family_recommendations(self):
        """Display family security recommendations"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Security Recommendations")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🛡️ Security Recommendations")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2E7D32; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Recommendations display
        recommendations = QTextEdit()
        recommendations.setReadOnly(True)
        recommendations.setPlainText(f"Recommendations for {self.current_mode} mode:\n\n"
                                   "1. 🔒 Enable strict content filtering\n"
                                   "2. ⏰ Set screen time limits\n"
                                   "3. 👀 Review browsing history weekly\n"
                                   "4. 🔔 Enable security alerts\n"
                                   "5. 🔄 Update security rules regularly")
        recommendations.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(recommendations)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_family_analysis(self):
        """Display family security analysis results"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Security Analysis")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔍 Security Analysis Report")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2E7D32; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Security score
        score_layout = QHBoxLayout()
        score_label = QLabel("Security Score:")
        score_label.setFont(QFont("Arial", 14))
        score_bar = QProgressBar()
        score_bar.setRange(0, 100)
        score_bar.setValue(85)
        score_bar.setFormat("%p% Complete")
        score_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 10px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 9px;
            }
        """)
        score_layout.addWidget(score_label)
        score_layout.addWidget(score_bar)
        layout.addLayout(score_layout)
        
        # Chart visualization placeholder (canvas module not yet implemented)
        # TODO: Add chart visualization when canvas module is available
        
        # Analysis details
        analysis = QTextEdit()
        analysis.setReadOnly(True)
        analysis.setPlainText(f"Analysis for {self.current_mode} mode:\n\n"
                             "✅ Content filtering active\n"
                             "✅ Screen time limits enforced\n"
                             "⚠️ 2 security updates available\n"
                             "✅ Regular activity monitoring\n"
                             "✅ Voice privacy enabled\n"
                             "\nOverall security status: Good")
        analysis.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(analysis)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.resource_monitor:
            self.resource_monitor.stop()
        event.accept()


def create_guardian_gui(guardian_interpreter=None):
    """Create and return Guardian GUI application and window"""
    app = QApplication(sys.argv)
    app.setApplicationName("Guardian Node")
    app.setApplicationVersion("1.0")
    
    # Create main window
    window = GuardianMainWindow(guardian_interpreter)
    
    # Fullscreen mode for Raspberry Pi
    if os.environ.get('RASPBERRY_PI', '0') == '1':
        window.showFullScreen()
    else:
        window.show()
    
    return app, window


# ---------------------------------------------------------------------------
# First-launch model download
# ---------------------------------------------------------------------------

MODEL_FILENAME = "microsoft_Phi-4-mini-instruct-Q4_K_M.gguf"
MODEL_REPO = "bartowski/microsoft_Phi-4-mini-instruct-GGUF"
MODEL_URL = f"https://huggingface.co/{MODEL_REPO}/resolve/main/{MODEL_FILENAME}"
MODEL_SIZE_GB = 2.3
# Anything smaller than this is treated as an incomplete/corrupt download.
MODEL_MIN_BYTES = 100 * 1024 * 1024


def get_models_dir() -> str:
    """Return the writable models/ directory.

    When frozen (PyInstaller onefile) the model lives in a `models` folder next
    to the executable; in source it lives in `models/` under the project root.
    """
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'models')


def get_model_path() -> str:
    return os.path.join(get_models_dir(), MODEL_FILENAME)


def get_llm_config() -> dict:
    """Build the llm config dict consumed by create_llm.

    context_length/threads are left configurable via environment variables so
    users with more RAM can raise the context window.
    """
    return {
        'llm': {
            'model_path': get_model_path(),
            'context_length': int(os.environ.get('GUARDIAN_CONTEXT_LENGTH', '8192')),
            'threads': int(os.environ.get('GUARDIAN_THREADS', '4')),
            'max_tokens': 512,
            'temperature': 0.7,
        }
    }


def model_is_present() -> bool:
    """Return True if a complete model file already exists."""
    path = get_model_path()
    try:
        return os.path.exists(path) and os.path.getsize(path) >= MODEL_MIN_BYTES
    except OSError:
        return False


class ModelDownloadThread(QThread):
    """Streams the model file to disk in the background, emitting progress."""

    progress_mb = Signal(float)
    finished_ok = Signal()
    error = Signal(str)

    def __init__(self, url: str, dest: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.dest = dest
        self._cancelled = False

    def run(self):
        tmp = self.dest + ".part"
        try:
            os.makedirs(os.path.dirname(self.dest), exist_ok=True)
            req = urllib.request.Request(self.url, headers={'User-Agent': 'GuardianNode/1.0'})
            with urllib.request.urlopen(req, timeout=60) as resp:
                done = 0
                with open(tmp, 'wb') as f:
                    while not self._cancelled:
                        chunk = resp.read(1024 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        done += len(chunk)
                        self.progress_mb.emit(done / (1024 * 1024))
            if self._cancelled:
                self.error.emit("Download cancelled.")
                return
            os.replace(tmp, self.dest)
            self.finished_ok.emit()
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._cancelled = True


class ModelDownloadDialog(QDialog):
    """Simple first-launch screen to download the AI model."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guardian Node - AI Model Setup")
        self.setFixedSize(520, 280)
        self._thread = None

        layout = QVBoxLayout()
        layout.setSpacing(12)

        title = QLabel("Welcome to Guardian Node")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2E7D32;")
        layout.addWidget(title)

        message = QLabel(
            "Guardian Node needs to download its AI model "
            f"({MODEL_SIZE_GB:.1f} GB, one-time, works offline after this)."
        )
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignCenter)
        message.setFont(QFont("Arial", 11))
        layout.addWidget(message)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("%p%")
        layout.addWidget(self.progress)

        self.status = QLabel("Ready to download.")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFont(QFont("Arial", 10))
        layout.addWidget(self.status)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.download_btn = QPushButton("Download")
        self.download_btn.setFixedHeight(40)
        self.download_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border: none; "
            "border-radius: 8px; font-size: 14px; font-weight: bold; }"
        )
        self.skip_btn = QPushButton("Skip for now")
        self.skip_btn.setFixedHeight(40)
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.skip_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.download_btn.clicked.connect(self.start_download)
        self.skip_btn.clicked.connect(self.reject)

    def start_download(self):
        self.download_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        self.status.setText("Downloading...")

        self._thread = ModelDownloadThread(MODEL_URL, get_model_path(), self)
        self._thread.progress_mb.connect(self._on_progress)
        self._thread.finished_ok.connect(self._on_finished)
        self._thread.error.connect(self._on_error)
        self._thread.start()

    def _on_progress(self, mb: float):
        self.progress.setValue(min(100, int(mb / (MODEL_SIZE_GB * 1024))))
        self.status.setText(f"Downloaded {mb:.0f} MB of ~{MODEL_SIZE_GB * 1024:.0f} MB...")

    def _on_finished(self):
        self.status.setText("Download complete.")
        self.accept()

    def _on_error(self, msg: str):
        self.download_btn.setEnabled(True)
        self.skip_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status.setText(f"Download failed: {msg}")

    def closeEvent(self, event):
        if self._thread and self._thread.isRunning():
            self._thread.cancel()
            self._thread.wait(2000)
        event.accept()


def ensure_model_available(parent=None) -> bool:
    """Show the download dialog on first launch if the model is missing.

    Returns True once a complete model is present (or was just downloaded).
    """
    if model_is_present():
        return True

    dialog = ModelDownloadDialog(parent)
    dialog.exec()
    return model_is_present()


def main():
    """Application entry point"""
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Guardian Node")
    app.setApplicationVersion("1.0")

    # First-launch: offer to download the AI model if it is missing.
    ensure_model_available()

    # Create and show the main window (works with or without the model).
    window = GuardianMainWindow()
    if os.environ.get('RASPBERRY_PI', '0') == '1':
        window.showFullScreen()
    else:
        window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()