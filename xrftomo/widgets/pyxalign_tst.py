from pyxalign import options as opts
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, 
    QFileDialog, QMessageBox, QScrollArea, QFrame, QGroupBox, QPushButton
)
from PyQt5.QtCore import Qt
import dataclasses
import inspect
import json
import os
from typing import Any, Dict, List, Tuple, Union


class CollapsibleGroupBox(QGroupBox):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(True)  # Start expanded
        self.setMaximumWidth(390)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold; 
                font-size: 14px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Connect the toggled signal to show/hide content
        self.toggled.connect(self._on_toggled)
        
    def _on_toggled(self, checked: bool):
        """Handle the toggle event to show/hide the group content"""
        if hasattr(self, 'content_widget'):
            self.content_widget.setVisible(checked)


class OptionsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = "pyxalign_options.json"
        self.widget_map = {}  # Map to store widget references
        self.init_ui()
        self.load_options()
        self.load_saved_settings()
        
    def init_ui(self):
        width = 480
        """Initialize the user interface"""
        self.setWindowTitle("PyXAlign Options Widget")
        self.setGeometry(50, 50, width, width)
        self.setMaximumWidth(width)
        

        # Main layout
        main_layout = QVBoxLayout()
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create scroll content widget
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_content.setLayout(self.scroll_layout)
        
        # Set scroll area widget
        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Add buttons
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Options")
        refresh_btn.clicked.connect(self.load_options)
        button_layout.addWidget(refresh_btn)
        
        expand_all_btn = QPushButton("Expand All")
        expand_all_btn.clicked.connect(self.expand_all_groups)
        button_layout.addWidget(expand_all_btn)
        
        collapse_all_btn = QPushButton("Collapse All")
        collapse_all_btn.clicked.connect(self.collapse_all_groups)
        button_layout.addWidget(collapse_all_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def closeEvent(self, event):
        """Save settings when the widget is closed"""
        self.save_current_settings()
        event.accept()
        
    def load_options(self):
        """Load all available options from the opts module"""
        # Clear existing content
        for i in reversed(range(self.scroll_layout.count())):
            child = self.scroll_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Get all option classes from the opts module
        option_classes = self.get_option_classes()
        
        for class_name, option_class in option_classes.items():
            self.create_option_group(class_name, option_class)
    
    def get_option_classes(self) -> Dict[str, Any]:
        """Get all dataclass option classes from the opts module"""
        option_classes = {}
        
        for name, obj in inspect.getmembers(opts):
            if (inspect.isclass(obj) and 
                hasattr(obj, '__dataclass_fields__') and 
                name.endswith('Options')):
                option_classes[name] = obj
        
        return option_classes
    
    def create_option_group(self, class_name: str, option_class: Any):
        """Create a group for a specific option class"""
        group_box = CollapsibleGroupBox(class_name)
        group_layout = QVBoxLayout()
        
        # Create a content widget to hold all the fields
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        
        # Create an instance of the option class to get default values
        try:
            option_instance = option_class()
            self.create_option_fields(option_instance, content_layout, class_name)
        except Exception as e:
            error_label = QLabel(f"Error creating {class_name}: {str(e)}")
            error_label.setStyleSheet("color: red;")
            content_layout.addWidget(error_label)
        
        # Store the content widget reference for toggling
        group_box.content_widget = content_widget
        group_layout.addWidget(content_widget)
        group_box.setLayout(group_layout)
        self.scroll_layout.addWidget(group_box)
    
    def create_option_fields(self, option_instance: Any, layout: QVBoxLayout, path_prefix=""):
        """Recursively create widgets for all fields in an option instance"""
        if not hasattr(option_instance, '__dataclass_fields__'):
            return
        
        for field_name, field_info in option_instance.__dataclass_fields__.items():
            field_value = getattr(option_instance, field_name)
            field_type = field_info.type
            
            # Check if this field has nested dataclass fields
            has_sub_options = (inspect.isclass(field_type) and 
                             hasattr(field_type, '__dataclass_fields__'))
            
            if has_sub_options:
                # Create a regular sub-group for nested dataclass (not collapsible)
                sub_group = QGroupBox(field_name)
                sub_group.setStyleSheet("""
                    QGroupBox {
                        font-weight: bold; 
                        font-size: 12px;
                        border: 1px solid #dddddd;
                        border-radius: 3px;
                        margin-top: 1ex;
                        padding-top: 8px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 8px;
                        padding: 0 3px 0 3px;
                    }
                """)
                sub_layout = QVBoxLayout()
                
                # Pass the current path prefix for nested fields
                current_path = f"{path_prefix}.{field_name}" if path_prefix else field_name
                self.create_option_fields(field_value, sub_layout, current_path)
                sub_group.setLayout(sub_layout)
                layout.addWidget(sub_group)
            else:
                # Create widget for simple field
                self.create_field_widget(field_name, field_value, field_type, layout, path_prefix)
    
    def create_field_widget(self, field_name: str, field_value: Any, field_type: Any, layout: QVBoxLayout, path_prefix=""):
        """Create appropriate widget based on field type"""
        # Create horizontal layout for label and widget
        field_layout = QHBoxLayout()
        
        # Create label
        label = QLabel(field_name)
        label.setMinimumWidth(150)
        label.setStyleSheet("QLabel { font-weight: normal; }")
        field_layout.addWidget(label)
        
        # Create widget based on type
        widget = self.create_type_specific_widget(field_value, field_type)
        field_layout.addWidget(widget)
        
        # Store widget reference for saving/loading
        widget_path = f"{path_prefix}.{field_name}" if path_prefix else field_name
        widget_type = self.get_widget_type(field_type)
        self.widget_map[widget_path] = {
            'widget': widget,
            'type': widget_type
        }
        
        # Add stretch to push widgets to the left
        field_layout.addStretch()
        
        layout.addLayout(field_layout)
    
    def get_widget_type(self, field_type: Any) -> str:
        """Determine the widget type based on field type"""
        type_str = str(field_type)
        
        if field_type == bool or 'bool' in type_str:
            return 'bool'
        elif field_type == int or 'int' in type_str:
            return 'int'
        elif field_type == float or 'float' in type_str:
            return 'float'
        elif field_type == str or 'str' in type_str:
            return 'str'
        elif field_type == tuple or 'tuple' in type_str or 'Sequence' in type_str:
            return 'tuple'
        else:
            return 'str'  # Default to string
    
    def create_type_specific_widget(self, value: Any, field_type: Any) -> QWidget:
        """Create appropriate widget based on the field type"""
        # Handle different type annotations
        type_str = str(field_type)
        button1size = 70
        # Check for bool type
        if field_type == bool or 'bool' in type_str:
            button = QPushButton()
            button.setCheckable(True)
            button.setChecked(bool(value))
            button.setText("True" if bool(value) else "False")
            
            # Connect the toggled signal to update the text
            button.toggled.connect(lambda checked, btn=button: btn.setText("True" if checked else "False"))
            
            # Style the button
            button.setStyleSheet("""
                QPushButton {
                    min-width: 60px;
                    padding: 5px;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    background-color: #f0f0f0;
                }
                QPushButton:checked {
                    background-color: #4CAF50;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:checked:hover {
                    background-color: #45a049;
                }
            """)
            
            return button
        
        # Check for int type
        elif field_type == int or 'int' in type_str:
            line_edit = QLineEdit()
            line_edit.setText(str(value))
            line_edit.setFixedWidth(button1size)
            return line_edit
        
        # Check for float type
        elif field_type == float or 'float' in type_str:
            line_edit = QLineEdit()
            line_edit.setText(str(value))
            line_edit.setFixedWidth(button1size)
            return line_edit
        
        # Check for str type
        elif field_type == str or 'str' in type_str:
            line_edit = QLineEdit()
            line_edit.setText(str(value))
            line_edit.setFixedWidth(button1size)
            return line_edit
        
        # Check for tuple type
        elif field_type == tuple or 'tuple' in type_str or 'Sequence' in type_str:
            line_edit = QLineEdit()
            line_edit.setText(str(value))
            line_edit.setEnabled(False)  # Disabled for tuples
            line_edit.setFixedWidth(button1size)
            return line_edit
        
        # Default to QLineEdit for unknown types
        else:
            line_edit = QLineEdit()
            line_edit.setText(str(value))
            line_edit.setFixedWidth(button1size)
            return line_edit
    
    def expand_all_groups(self):
        """Expand all collapsible groups"""
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, CollapsibleGroupBox):
                    widget.setChecked(True)
    
    def collapse_all_groups(self):
        """Collapse all collapsible groups"""
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, CollapsibleGroupBox):
                    widget.setChecked(False)
    
    def save_current_settings(self):
        """Save all current widget values to JSON file"""
        settings = {}
        
        for path, widget_info in self.widget_map.items():
            widget = widget_info['widget']
            widget_type = widget_info['type']
            
            if widget_type == 'bool':
                settings[path] = widget.isChecked()
            elif widget_type in ['int', 'float', 'str']:
                settings[path] = widget.text()
            elif widget_type == 'tuple':
                settings[path] = widget.text()  # Keep as string for tuples
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            print(f"Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_saved_settings(self):
        """Load saved settings from JSON file and apply to widgets"""
        if not os.path.exists(self.settings_file):
            return
        
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
            
            for path, value in settings.items():
                if path in self.widget_map:
                    widget_info = self.widget_map[path]
                    widget = widget_info['widget']
                    widget_type = widget_info['type']
                    
                    if widget_type == 'bool':
                        widget.setChecked(bool(value))
                        widget.setText("True" if bool(value) else "False")
                    elif widget_type in ['int', 'float', 'str']:
                        widget.setText(str(value))
                    elif widget_type == 'tuple':
                        widget.setText(str(value))
            
            print(f"Settings loaded from {self.settings_file}")
        except Exception as e:
            print(f"Error loading settings: {e}")


def main():
    app = QApplication([])
    widget = OptionsWidget()
    widget.show()
    app.exec_()


if __name__ == "__main__":
    main()

