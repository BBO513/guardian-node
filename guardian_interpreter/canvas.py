"""
Canvas module for Guardian Node GUI
Provides chart visualization capabilities
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PySide6.QtCore import Qt, QRect, QSize

class ChartWidget(QWidget):
    """Widget for displaying simple charts"""
    
    def __init__(self, chart_config, parent=None):
        super().__init__(parent)
        self.chart_config = chart_config
        self.setMinimumSize(300, 150)
        self.setMaximumHeight(200)
    
    def paintEvent(self, event):
        """Paint the chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get chart type and data
        chart_type = self.chart_config.get('type', 'bar')
        data = self.chart_config.get('data', {})
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        if chart_type == 'bar':
            self._draw_bar_chart(painter, labels, datasets)
        elif chart_type == 'pie':
            self._draw_pie_chart(painter, labels, datasets)
        else:
            # Fallback to text
            painter.drawText(self.rect(), Qt.AlignCenter, "Chart type not supported")
    
    def _draw_bar_chart(self, painter, labels, datasets):
        """Draw a bar chart"""
        if not datasets or not labels:
            return
            
        # Chart dimensions
        width = self.width()
        height = self.height()
        padding = 20
        chart_width = width - 2 * padding
        chart_height = height - 2 * padding
        
        # Find max value for scaling
        max_value = 0
        for dataset in datasets:
            data_points = dataset.get('data', [])
            if data_points:
                max_value = max(max_value, max(data_points))
        
        if max_value == 0:
            max_value = 100  # Default if no data
        
        # Draw axes
        painter.setPen(QPen(QColor('#333333'), 2))
        painter.drawLine(padding, height - padding, width - padding, height - padding)  # X-axis
        painter.drawLine(padding, padding, padding, height - padding)  # Y-axis
        
        # Draw bars
        bar_width = chart_width / (len(labels) * len(datasets) + len(labels) + 1)
        x_offset = padding + bar_width
        
        for dataset_index, dataset in enumerate(datasets):
            data_points = dataset.get('data', [])
            color = dataset.get('backgroundColor', '#4CAF50')
            
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor('#333333'), 1))
            
            for i, value in enumerate(data_points):
                if i < len(labels):
                    bar_height = (value / max_value) * chart_height
                    x = x_offset + i * (bar_width * (len(datasets) + 1))
                    y = height - padding - bar_height
                    
                    # Draw bar
                    painter.drawRect(x + dataset_index * bar_width, y, bar_width, bar_height)
                    
                    # Draw value
                    painter.drawText(
                        QRect(x + dataset_index * bar_width, y - 20, bar_width, 20),
                        Qt.AlignCenter,
                        str(value)
                    )
            
            # Draw legend
            legend_x = padding
            legend_y = padding / 2
            legend_width = 10
            legend_height = 10
            
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRect(legend_x + dataset_index * 100, legend_y, legend_width, legend_height)
            painter.drawText(
                QRect(legend_x + dataset_index * 100 + legend_width + 5, legend_y, 80, legend_height),
                Qt.AlignLeft | Qt.AlignVCenter,
                dataset.get('label', f'Dataset {dataset_index}')
            )
        
        # Draw labels
        for i, label in enumerate(labels):
            x = x_offset + i * (bar_width * (len(datasets) + 1)) + (bar_width * len(datasets)) / 2
            painter.drawText(
                QRect(x - 40, height - padding + 5, 80, 20),
                Qt.AlignCenter,
                label
            )
    
    def _draw_pie_chart(self, painter, labels, datasets):
        """Draw a pie chart"""
        if not datasets or not labels:
            return
            
        # Use first dataset
        dataset = datasets[0]
        data_points = dataset.get('data', [])
        
        if not data_points:
            return
            
        # Chart dimensions
        width = self.width()
        height = self.height()
        padding = 20
        diameter = min(width, height) - 2 * padding
        center_x = width / 2
        center_y = height / 2
        
        # Calculate total for percentages
        total = sum(data_points)
        if total == 0:
            return
            
        # Draw pie segments
        start_angle = 0
        for i, value in enumerate(data_points):
            if i < len(labels):
                angle = (value / total) * 360 * 16  # QPainter uses 1/16th of a degree
                
                # Get color
                if 'backgroundColor' in dataset and isinstance(dataset['backgroundColor'], list):
                    color = dataset['backgroundColor'][i % len(dataset['backgroundColor'])]
                else:
                    colors = ['#4CAF50', '#2196F3', '#FFC107', '#F44336', '#9C27B0']
                    color = colors[i % len(colors)]
                
                painter.setBrush(QBrush(QColor(color)))
                painter.setPen(QPen(QColor('#FFFFFF'), 1))
                
                # Draw segment
                painter.drawPie(
                    center_x - diameter / 2,
                    center_y - diameter / 2,
                    diameter,
                    diameter,
                    start_angle,
                    angle
                )
                
                start_angle += angle
        
        # Draw legend
        legend_y = height - padding
        for i, label in enumerate(labels):
            if i < len(data_points):
                # Get color
                if 'backgroundColor' in dataset and isinstance(dataset['backgroundColor'], list):
                    color = dataset['backgroundColor'][i % len(dataset['backgroundColor'])]
                else:
                    colors = ['#4CAF50', '#2196F3', '#FFC107', '#F44336', '#9C27B0']
                    color = colors[i % len(colors)]
                
                legend_x = padding + i * 100
                legend_width = 10
                legend_height = 10
                
                painter.setBrush(QBrush(QColor(color)))
                painter.drawRect(legend_x, legend_y, legend_width, legend_height)
                
                # Calculate percentage
                percentage = (data_points[i] / total) * 100
                
                painter.drawText(
                    QRect(legend_x + legend_width + 5, legend_y, 80, legend_height),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    f"{label} ({percentage:.1f}%)"
                )

def show_chart(chart_config):
    """
    Create and return a chart widget
    
    Args:
        chart_config: Dictionary with chart configuration
        
    Returns:
        ChartWidget instance
    """
    return ChartWidget(chart_config)

# Example usage
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Chart Test")
    window.setGeometry(100, 100, 500, 300)
    
    # Bar chart example
    bar_chart = show_chart({
        'type': 'bar',
        'data': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr'],
            'datasets': [
                {
                    'label': 'Sales',
                    'data': [12, 19, 3, 5],
                    'backgroundColor': '#4CAF50'
                },
                {
                    'label': 'Revenue',
                    'data': [7, 11, 5, 8],
                    'backgroundColor': '#2196F3'
                }
            ]
        }
    })
    
    window.setCentralWidget(bar_chart)
    window.show()
    
    sys.exit(app.exec())