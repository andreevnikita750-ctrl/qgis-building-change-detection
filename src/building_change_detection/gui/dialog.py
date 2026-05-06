# -*- coding: utf-8 -*-
"""
User interface dialog for Building Change Detection
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QSpinBox, QDoubleSpinBox, QProgressBar, QTableWidget,
    QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from qgis.core import QgsProject
from ..core.matcher import BuildingMatcher
from ..core.analyzer import ChangeAnalyzer


class AnalysisWorker(QThread):
    """Worker thread for background analysis"""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, matcher, current_layer, historical_layer, analyzer_params):
        super().__init__()
        self.matcher = matcher
        self.current_layer = current_layer
        self.historical_layer = historical_layer
        self.analyzer_params = analyzer_params
    
    def run(self):
        try:
            self.progress.emit(50)
            
            # Run matching
            matches = self.matcher.match(self.current_layer, self.historical_layer)
            
            self.progress.emit(75)
            
            # Create analyzer and result layer
            analyzer = ChangeAnalyzer(
                matches,
                self.current_layer,
                self.historical_layer,
                self.analyzer_params['distance_threshold']
            )
            result_layer = analyzer.create_result_layer()
            stats = analyzer.get_statistics()
            
            self.progress.emit(100)
            self.finished.emit({'layer': result_layer, 'stats': stats})
            
        except Exception as e:
            self.error.emit(str(e))


class BuildingChangeDetectionDialog(QDialog):
    """Main dialog for building change detection analysis"""
    
    def __init__(self, iface, parent=None):
        """Initialize dialog"""
        super().__init__(parent)
        self.iface = iface
        self.worker = None
        self.setWindowTitle('Building Change Detection')
        self.setGeometry(100, 100, 600, 500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Building Change Detection Analysis')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Layer selection
        layout.addWidget(QLabel('Current Buildings Layer:'))
        self.current_layer_combo = QComboBox()
        self._populate_layer_combo(self.current_layer_combo)
        layout.addWidget(self.current_layer_combo)
        
        layout.addWidget(QLabel('Historical Buildings Layer:'))
        self.historical_layer_combo = QComboBox()
        self._populate_layer_combo(self.historical_layer_combo)
        layout.addWidget(self.historical_layer_combo)
        
        # Parameters
        params_layout = QHBoxLayout()
        
        params_layout.addWidget(QLabel('Distance Threshold (m):'))
        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(0, 1000)
        self.distance_spin.setValue(50.0)
        self.distance_spin.setSingleStep(10)
        params_layout.addWidget(self.distance_spin)
        
        params_layout.addWidget(QLabel('Confidence Threshold:'))
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.0, 1.0)
        self.confidence_spin.setValue(0.7)
        self.confidence_spin.setSingleStep(0.1)
        params_layout.addWidget(self.confidence_spin)
        
        layout.addLayout(params_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Analyze button
        self.analyze_button = QPushButton('Analyze')
        self.analyze_button.clicked.connect(self.run_analysis)
        layout.addWidget(self.analyze_button)
        
        # Results table
        layout.addWidget(QLabel('Analysis Results:'))
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(['Category', 'Count'])
        self.results_table.setMaximumHeight(150)
        layout.addWidget(self.results_table)
        
        # Close button
        close_button = QPushButton('Close')
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def _populate_layer_combo(self, combo):
        """Populate combo box with polygon layers"""
        combo.clear()
        for layer in QgsProject.instance().layerTreeRoot().children():
            if hasattr(layer, 'layer'):
                actual_layer = layer.layer()
                if hasattr(actual_layer, 'geometryType'):
                    from qgis.core import QgsWkbTypes
                    if actual_layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                        combo.addItem(actual_layer.name(), actual_layer)
    
    def run_analysis(self):
        """Run the building change detection analysis"""
        current_layer = self.current_layer_combo.currentData()
        historical_layer = self.historical_layer_combo.currentData()
        
        if not current_layer or not historical_layer:
            QMessageBox.warning(self, 'Input Error', 'Please select both layers')
            return
        
        if current_layer.id() == historical_layer.id():
            QMessageBox.warning(self, 'Input Error', 'Please select different layers')
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.analyze_button.setEnabled(False)
        
        # Create matcher
        matcher = BuildingMatcher(
            self.distance_spin.value(),
            self.confidence_spin.value()
        )
        
        # Start worker thread
        self.worker = AnalysisWorker(
            matcher,
            current_layer,
            historical_layer,
            {'distance_threshold': self.distance_spin.value()}
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.analysis_finished)
        self.worker.error.connect(self.analysis_error)
        self.worker.start()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def analysis_finished(self, result):
        """Handle analysis completion"""
        self.progress_bar.setVisible(False)
        self.analyze_button.setEnabled(True)
        
        # Add result layer to map
        result_layer = result['layer']
        QgsProject.instance().addMapLayer(result_layer)
        
        # Show statistics
        stats = result['stats']
        self._display_statistics(stats)
        
        QMessageBox.information(
            self, 'Success',
            'Analysis completed! Result layer added to map.'
        )
    
    def analysis_error(self, error_msg):
        """Handle analysis error"""
        self.progress_bar.setVisible(False)
        self.analyze_button.setEnabled(True)
        QMessageBox.critical(self, 'Error', 'Analysis failed: ' + error_msg)
    
    def _display_statistics(self, stats):
        """Display analysis statistics in table"""
        self.results_table.setRowCount(5)
        
        data = [
            ('Unchanged', stats['unchanged']),
            ('Moved', stats['moved']),
            ('Removed', stats['removed']),
            ('Added', stats['added']),
            ('Total Changes', stats['total_changes']),
        ]
        
        for row, (category, count) in enumerate(data):
            self.results_table.setItem(row, 0, QTableWidgetItem(category))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(count)))
