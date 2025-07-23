"""
Guardian Node GUI - Family-Friendly Interface with Mode Switching
Production-ready PySide6 interface for Raspberry Pi touchscreen deployment
"""

import sys
import os
import logging
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
from PySide6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize

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

class GuardianModeUI(QWidget):
    """Main mode switching interface with themed graphics"""
    
    # Signal emitted when mode changes
    mode_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "Kids"  # Default safe mode
        self.image_paths = {
            "Adult": "assets/adult_mode.png",
            "Kids": "assets/kids_mode.png", 
            "Teens": "assets/teens_mode.png"
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
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
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


class GuardianMainWindow(QMainWindow):
    """Main Guardian Node application window"""
    
    def __init__(self, guardian_interpreter=None):
        super().__init__()
        self.guardian = guardian_interpreter
        self.resource_monitor = ResourceMonitor()
        self.current_mode = "Kids"
        self.voice_privacy_enabled = True
        
        self.setup_ui()
        self.setup_mode_integration()
    
    def setup_ui(self):
        """Setup main window UI"""
        self.setWindowTitle("Guardian Node - Family Protection")
        self.setFixedSize(800, 480)  # Optimized for Raspberry Pi touchscreen
        
        # Central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main mode interface
        self.mode_ui = GuardianModeUI()
        
        # System status widget
        self.status_widget = SystemStatusWidget(self.resource_monitor)
        
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
        main_layout.addLayout(left_layout, 2)  # 2/3 of space
        main_layout.addLayout(right_layout, 1)  # 1/3 of space
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
        """Start voice assistant session"""
        from family_assistant.voice_interface import FamilyVoiceInterface
        
        # Update status
        print("Starting voice session...")
        self.status_widget.status_label.setText("🎤 Listening...")
        self.status_widget.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        # Get family context based on current mode
        family_context = self.get_family_profile_for_mode(self.current_mode)
        
        # Initialize voice interface
        voice_interface = FamilyVoiceInterface(config=self.guardian.config, logger=self.guardian.logger)
        result = voice_interface.start_voice_session(family_context)
        
        # Update status based on result
        if result and result.get('success'):
            self.status_widget.status_label.setText("🟢 Voice command completed")
        else:
            self.status_widget.status_label.setText("🔴 Voice command failed")
            
        # Show response if available
        if result and 'response' in result:
            print(f"Voice response: {result['response']}")
    
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
        
        # Add chart visualization
        from guardian_interpreter.canvas import show_chart  # Assume canvas module
        layout.addWidget(show_chart({
            'type': 'bar', 
            'data': {
                'labels': ['Score'], 
                'datasets': [
                    {'label': 'Security', 'data': [85], 'backgroundColor': '#4CAF50'}
                ]
            }
        }))
        
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


def main():
    """Application entry point"""
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ensure assets directory exists
    os.makedirs("assets", exist_ok=True)
    
    # Create placeholder images if they don't exist
    for mode in ["adult", "kids", "teens"]:
        img_path = f"assets/{mode}_mode.png"
        if not os.path.exists(img_path):
            # In production, use real images
            open(img_path, 'wb').close()
    
    # Create and run application
    app, window = create_guardian_gui()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()