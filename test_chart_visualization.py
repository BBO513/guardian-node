#!/usr/bin/env python3
"""
Test script for chart visualization in Guardian GUI
"""

import sys
import os

# Add the guardian_interpreter directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'guardian_interpreter'))

def test_chart_visualization():
    """Test chart visualization with mock data"""
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
        from canvas import show_chart
        
        app = QApplication(sys.argv)
        
        window = QMainWindow()
        window.setWindowTitle("Guardian Chart Test")
        window.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create bar chart
        bar_chart = show_chart({
            'type': 'bar',
            'data': {
                'labels': ['Security', 'Privacy', 'Content'],
                'datasets': [
                    {
                        'label': 'Score',
                        'data': [85, 92, 78],
                        'backgroundColor': '#4CAF50'
                    }
                ]
            }
        })
        layout.addWidget(bar_chart)
        
        # Create pie chart button
        pie_button = QPushButton("Show Pie Chart")
        
        def show_pie():
            # Replace bar chart with pie chart
            layout.removeWidget(bar_chart)
            bar_chart.hide()
            
            pie_chart = show_chart({
                'type': 'pie',
                'data': {
                    'labels': ['Secure', 'Warning', 'Critical'],
                    'datasets': [
                        {
                            'label': 'Devices',
                            'data': [8, 2, 1],
                            'backgroundColor': ['#4CAF50', '#FFC107', '#F44336']
                        }
                    ]
                }
            })
            layout.insertWidget(0, pie_chart)
        
        pie_button.clicked.connect(show_pie)
        layout.addWidget(pie_button)
        
        window.setCentralWidget(central_widget)
        window.show()
        
        print("✅ Chart visualization test running")
        print("Close the window to complete the test")
        
        return app.exec()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("PySide6 is required for this test")
        return 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_chart_visualization())