import os
import math
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QPoint, pyqtSignal, QSize
from qgis.PyQt.QtGui import (QIcon, QColor, QPalette, QFont, QPainter, QPixmap, QPolygon, QPen, 
                             QBrush, QPainterPath)
from qgis.PyQt.QtWidgets import (QAction, QMenu, QToolButton, QDialog, QVBoxLayout, QHBoxLayout, 
                                 QGridLayout, QLabel, QPushButton, QSpinBox, QDoubleSpinBox, 
                                 QButtonGroup, QFrame, QMessageBox, QSizePolicy, QWidget, 
                                 QLineEdit, QComboBox, QFormLayout, QScrollArea, QTableWidget, 
                                 QTableWidgetItem, QHeaderView)
from qgis.PyQt.QtTest import QTest
from qgis.core import (QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, 
                       Qgis, QgsApplication, QgsField, QgsSymbol, QgsRendererRange, 
                       QgsGraduatedSymbolRenderer, QgsSingleSymbolRenderer,
                       QgsSimpleMarkerSymbolLayer, QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer, QgsMarkerSymbol, QgsLineSymbol,
                       QgsFillSymbol, QgsWkbTypes, QgsPalLayerSettings, 
                       QgsVectorLayerSimpleLabeling, QgsRuleBasedLabeling,
                       QgsTextFormat, QgsTextBufferSettings, QgsUnitTypes,
                       QgsCategorizedSymbolRenderer, QgsRendererCategory,
                       QgsLayerTreeLayer, QgsRasterLayer, QgsSvgMarkerSymbolLayer)
from qgis.PyQt.QtCore import QVariant
from qgis.gui import QgsProjectionSelectionDialog
from qgis.utils import iface


class QuickStyle:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # Initialize plugin directory
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QuickStyle_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QuickStyle')
        self.toolbar = self.iface.addToolBar(u'QuickStyle')
        self.toolbar.setObjectName(u'QuickStyle')
        
        # CRS dropdown menu
        self.crs_menu = None
        self.crs_tool_button = None
        
        # Color palettes and options for different tools
        self.colors = [
            '#e41a1c', '#3579b1', '#00e4f6', '#0000ff', 
            '#ff00ff', '#ff69b4', '#5e17eb', '#ffa500',
            '#00fa9a', '#e10052', '#9bbce7', '#c8ff6d', 
            '#22c89e', '#ffd93d', '#008e9b', '#ff9671'
        ]
        

    def tr(self, message):
        return QCoreApplication.translate('QuickStyle', message)

    def get_icon_path(self, icon_name):
        """Get the full path to an icon file"""
        return os.path.join(self.plugin_dir, icon_name)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True,
                   add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        # Use direct file path for icon
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            icon = QIcon()  # Empty icon if file doesn't exist
            
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        # Tool 1: Set CRS with dropdown
        self.create_crs_tool()
        
        # Tool 2: Add Field
        icon_path = self.get_icon_path('add_field.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Add Field'),
            callback=self.add_field,
            parent=self.iface.mainWindow(),
            status_tip='Add Field to Selected Layer',
            whats_this='Add a new field to the selected vector layer',
            add_to_menu=False
        )
        
        # Tool 3: Open Attribute Table
        icon_path = self.get_icon_path('open_attribute_table.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Open Attribute Table'),
            callback=self.open_attribute_table,
            parent=self.iface.mainWindow(),
            status_tip='Open Attribute Table',
            whats_this='Open attribute table for the selected layer',
            add_to_menu=False
        )
        
        # Tool 4: Show Selected Features
        icon_path = self.get_icon_path('show_selected_features.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Show Selected Features'),
            callback=self.show_selected_features,
            parent=self.iface.mainWindow(),
            status_tip='Show Selected Features',
            whats_this='Show selected features in attribute table',
            add_to_menu=False
        )
        
        # Tool 5: Symbology
        icon_path = self.get_icon_path('Symbology.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Symbology'),
            callback=self.run_symbology,
            parent=self.iface.mainWindow(),
            status_tip='Apply Symbology',
            whats_this='Apply symbology to the selected vector layer',
            add_to_menu=False
        )
        
        # Tool 6: Label
        icon_path = self.get_icon_path('label.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Configure Labels'),
            callback=self.run_labeling,
            parent=self.iface.mainWindow(),
            status_tip='Configure Labels',
            whats_this='Configure labels for the active vector layer',
            add_to_menu=False
        )
        
        # Tool 7: Categorize Vector Layer
        icon_path = self.get_icon_path('categorize.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Categorize Layer'),
            callback=self.run_categorize,
            parent=self.iface.mainWindow(),
            status_tip='Categorize Layer',
            whats_this='Categorize vector layer by field values',
            add_to_menu=False
        )
        
        # Tool 8: Rule-Based Categorization
        icon_path = self.get_icon_path('RuleBased.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Rule-Based Categorize'),
            callback=self.run_rule_based,
            parent=self.iface.mainWindow(),
            status_tip='Rule-Based Categorize',
            whats_this='Apply rule-based categorization to vector layer',
            add_to_menu=False
        )

    def create_crs_tool(self):
        """Create CRS tool with dropdown menu"""
        # Create tool button
        self.crs_tool_button = QToolButton()
        self.crs_tool_button.setPopupMode(QToolButton.MenuButtonPopup)
        
        # Create main action
        icon_path = self.get_icon_path('crs.png')
        crs_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
        crs_action = QAction(crs_icon, self.tr(u'Set CRS'), self.iface.mainWindow())
        crs_action.setStatusTip('Set CRS for Selected Layer')
        crs_action.setWhatsThis('Set coordinate reference system for the selected layer')
        crs_action.triggered.connect(self.choose_other_crs)
        
        self.crs_tool_button.setDefaultAction(crs_action)
        
        # Create dropdown menu
        self.crs_menu = QMenu()
        
        # Add predefined CRS options
        crs_options = [
            ('EPSG:28992', 'EPSG:28992 (RD New)'),
            ('EPSG:2154', 'EPSG:2154 (RGF93 / Lambert-93)'),
            ('EPSG:31370', 'EPSG:31370 (BD72 / Belgian Lambert 72)'),
            ('EPSG:3857', 'EPSG:3857 (WGS 84 / Pseudo-Mercator)')
        ]
        
        for epsg_code, description in crs_options:
            action = self.crs_menu.addAction(description)
            action.triggered.connect(lambda checked, code=epsg_code: self.set_predefined_crs(code))
        
        # Add separator and "Choose Other" option
        self.crs_menu.addSeparator()
        choose_other_action = self.crs_menu.addAction("Choose Other...")
        choose_other_action.triggered.connect(self.choose_other_crs)
        
        self.crs_tool_button.setMenu(self.crs_menu)
        
        # Add to toolbar
        self.toolbar.addWidget(self.crs_tool_button)
        
        # Add to actions list for cleanup
        self.actions.append(crs_action)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginVectorMenu(self.tr(u'&QuickStyle'), action)
            self.iface.removeToolBarIcon(action)
        
        # Remove toolbar
        if self.toolbar:
            del self.toolbar

    # Helper methods
    def get_active_vector_layer(self):
        """Get the active vector layer"""
        active_layer = iface.activeLayer()
        
        if not active_layer or not isinstance(active_layer, QgsVectorLayer):
            iface.messageBar().pushMessage(
                "Error", "Please select a vector layer!", 
                level=Qgis.Critical, duration=5
            )
            return None
        return active_layer

    def get_active_layer(self):
        """Get the active layer (vector or raster)"""
        active_layer = iface.activeLayer()
        
        if not active_layer:
            iface.messageBar().pushMessage(
                "Error", "Please select a layer!", 
                level=Qgis.Critical, duration=5
            )
            return None
        
        if not isinstance(active_layer, (QgsVectorLayer, QgsRasterLayer)):
            iface.messageBar().pushMessage(
                "Error", "Please select a vector or raster layer!", 
                level=Qgis.Critical, duration=5
            )
            return None
            
        return active_layer

    # Tool 1: CRS Methods
    def set_predefined_crs(self, epsg_code):
        """Set predefined CRS for the selected layer"""
        layer = self.get_active_layer()
        if not layer:
            return
        
        try:
            # Create CRS object
            crs = QgsCoordinateReferenceSystem(epsg_code)
            if not crs.isValid():
                iface.messageBar().pushMessage(
                    "Error", f"Invalid CRS: {epsg_code}", 
                    level=Qgis.Critical, duration=5
                )
                return
            
            # Set CRS
            layer.setCrs(crs)
            
            # Refresh map
            iface.mapCanvas().refresh()
            
            # Show success message with layer type
            layer_type = "vector" if isinstance(layer, QgsVectorLayer) else "raster"
            iface.messageBar().pushMessage(
                "Success", f"CRS set to {epsg_code} for {layer_type} layer: {layer.name()}", 
                level=Qgis.Success, duration=5
            )
            
        except Exception as e:
            iface.messageBar().pushMessage(
                "Error", f"Failed to set CRS: {str(e)}", 
                level=Qgis.Critical, duration=5
            )

    def choose_other_crs(self):
        """Open CRS selection dialog"""
        layer = self.get_active_layer()
        if not layer:
            return
        
        try:
            # Open QGIS native CRS selection dialog
            crs_dialog = QgsProjectionSelectionDialog(self.iface.mainWindow())
            crs_dialog.setCrs(layer.crs())
            
            if crs_dialog.exec():
                selected_crs = crs_dialog.crs()
                if selected_crs.isValid():
                    # Set CRS
                    layer.setCrs(selected_crs)
                    
                    # Refresh map
                    iface.mapCanvas().refresh()
                    
                    # Show success message with layer type
                    layer_type = "vector" if isinstance(layer, QgsVectorLayer) else "raster"
                    iface.messageBar().pushMessage(
                        "Success", f"CRS set to {selected_crs.authid()} for {layer_type} layer: {layer.name()}", 
                        level=Qgis.Success, duration=5
                    )
                    
        except Exception as e:
            iface.messageBar().pushMessage(
                "Error", f"Failed to set CRS: {str(e)}", 
                level=Qgis.Critical, duration=5
            )

    # Tool 2: Add Field Methods
    def add_field(self):
        """Add field to the selected layer with custom dialog"""
        layer = self.get_active_vector_layer()
        if not layer:
            return
        
        try:
            # Create and show custom add field dialog
            self.show_add_field_dialog(layer)
            
        except Exception as e:
            iface.messageBar().pushMessage(
                "Error", f"Failed to add field: {str(e)}", 
                level=Qgis.Critical, duration=5
            )
    
    def show_add_field_dialog(self, layer):
        """Show custom add field dialog with defaults"""
        # Create dialog
        dialog = QDialog(self.iface.mainWindow())
        dialog.setWindowTitle("Add Field")
        dialog.setModal(True)
        dialog.resize(300, 150)
        
        # Create layout
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Field name input
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter field name...")
        name_edit.setMaxLength(10)  # Maximum 10 characters
        form_layout.addRow("Name:", name_edit)
        
        # Field type combo
        type_combo = QComboBox()
        type_combo.addItems(["Text (string)", "Whole number (integer)", "Decimal number (real)", "Date"])
        type_combo.setCurrentText("Text (string)")  # Default selection
        form_layout.addRow("Type:", type_combo)
        
        # Field length input
        length_spin = QSpinBox()
        length_spin.setMinimum(1)
        length_spin.setMaximum(10000)
        length_spin.setValue(255)  # Default value
        form_layout.addRow("Length:", length_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Connect buttons
        def on_ok():
            field_name = name_edit.text().strip()
            if not field_name:
                iface.messageBar().pushMessage(
                    "Error", "Please enter a field name!", 
                    level=Qgis.Critical, duration=3
                )
                return
            
            # Check if field name already exists
            existing_fields = [field.name() for field in layer.fields()]
            if field_name in existing_fields:
                iface.messageBar().pushMessage(
                    "Error", f"Field '{field_name}' already exists!", 
                    level=Qgis.Critical, duration=3
                )
                return
            
            # Get field type
            type_text = type_combo.currentText()
            if "string" in type_text.lower() or "text" in type_text.lower():
                field_type = QVariant.String
                type_name = "String"
            elif "integer" in type_text.lower() or "whole" in type_text.lower():
                field_type = QVariant.Int
                type_name = "Integer"
            elif "real" in type_text.lower() or "decimal" in type_text.lower():
                field_type = QVariant.Double
                type_name = "Double"
            elif "date" in type_text.lower():
                field_type = QVariant.Date
                type_name = "Date"
            else:
                field_type = QVariant.String
                type_name = "String"
            
            # Create field
            field = QgsField(field_name, field_type, type_name, length_spin.value())
            
            # Add field to layer
            if not layer.isEditable():
                layer.startEditing()
            
            if layer.addAttribute(field):
                # Auto-save changes
                if layer.commitChanges():
                    # Re-enable editing mode to keep it active
                    layer.startEditing()
                    iface.messageBar().pushMessage(
                        "Success", f"Field '{field_name}' added and saved to layer: {layer.name()}", 
                        level=Qgis.Success, duration=5
                    )
                    # Refresh attribute table if open
                    iface.mapCanvas().refresh()
                else:
                    layer.startEditing()  # Restart editing if commit failed
                    iface.messageBar().pushMessage(
                        "Warning", f"Field '{field_name}' added but could not auto-save. Please save manually.", 
                        level=Qgis.Warning, duration=5
                    )
                dialog.accept()
            else:
                iface.messageBar().pushMessage(
                    "Error", f"Failed to add field '{field_name}'", 
                    level=Qgis.Critical, duration=5
                )
        
        def on_cancel():
            dialog.reject()
        
        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(on_cancel)
        
        # Show dialog
        dialog.exec()

    # Tool 3: Open Attribute Table
    def open_attribute_table(self):
        """Open attribute table for the selected layer"""
        layer = self.get_active_vector_layer()
        if not layer:
            return
        
        try:
            # Use QGIS native functionality to open attribute table
            iface.showAttributeTable(layer)
            
        except Exception as e:
            iface.messageBar().pushMessage(
                "Error", f"Failed to open attribute table: {str(e)}", 
                level=Qgis.Critical, duration=5
            )

    # Tool 4: Show Selected Features
    def show_selected_features(self):
        """Show selected features in attribute table"""
        layer = self.get_active_vector_layer()
        if not layer:
            return
        
        try:
            # Check if there are selected features
            selected_count = layer.selectedFeatureCount()
            if selected_count == 0:
                iface.messageBar().pushMessage(
                    "Warning", "No features are selected in the layer!", 
                    level=Qgis.Warning, duration=5
                )
                return
            
            # Use QGIS native functionality with Shift+F6 shortcut
            main_window = iface.mainWindow()
            
            # Send Shift+F6 shortcut to show selected features in attribute table
            QTest.keyClick(main_window, Qt.Key_F6, Qt.ShiftModifier)
            
        except Exception as e:
            iface.messageBar().pushMessage(
                "Error", f"Failed to show selected features: {str(e)}", 
                level=Qgis.Critical, duration=5
            )

    # Tool 5: Symbology Methods - UPDATED
    def run_symbology(self):
        """Run the new SVG-based symbology dialog"""
        layer = self.iface.activeLayer()
        
        if not layer or not isinstance(layer, QgsVectorLayer):
            QMessageBox.information(
                self.iface.mainWindow(),
                "Symbology", 
                "No vector layer is selected"
            )
            return
            
        # Create and show the NEW symbology dialog
        dialog = SymbologyDialog(layer, self.iface.mainWindow())
        
        # Run the dialog event loop
        if dialog.exec_() == QDialog.Accepted:
            # Apply symbology if user clicked OK
            if dialog.apply_symbology():
                dialog.save_settings()
                # Show success message
                self.iface.messageBar().pushMessage(
                    "Success", 
                    "Symbology applied successfully!", 
                    level=Qgis.Success,
                    duration=3
                )

    # Tool 6: Labeling Methods
    def run_labeling(self):
        """Run labeling dialog"""
        # Check if there's an active layer
        active_layer = iface.activeLayer()
        
        if not active_layer or not isinstance(active_layer, QgsVectorLayer):
            iface.messageBar().pushMessage(
                "Error", "Please select a vector layer!", 
                level=Qgis.Critical, duration=5
            )
            return
            
        # Open dialog
        dialog = LabelingDialog(active_layer, self)
        dialog.exec_()

    # Tool 7: Categorize Methods
    def run_categorize(self):
        """Run categorization dialog"""
        layer = self.iface.activeLayer()
        if not layer or not layer.isValid():
            return

        dlg = QDialog()
        dlg.setWindowTitle("Select Field for Categorization")
        dlg.setFixedSize(850, 400)
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(245, 245, 245))
        dlg.setPalette(palette)
        
        layout = QVBoxLayout()
        title = QLabel("Click a field to categorize:")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 10px;")
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        grid = QGridLayout(widget)
        grid.setSpacing(15)
        grid.setContentsMargins(25, 15, 25, 15)
        
        # Get fields with unique value counts and filter them
        fields = []
        for field in layer.fields():
            unique_values = layer.uniqueValues(layer.fields().lookupField(field.name()))
            unique_count = len(unique_values)
            # Apply filtering conditions
            if 1 < unique_count <= 30:
                fields.append((field.name(), unique_count))
        
        if not fields:
            no_fields_label = QLabel("No suitable fields found (need 2-30 unique values)")
            no_fields_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_fields_label)
        else:
            row, col = 0, 0
            for i, (field_name, count) in enumerate(fields):
                btn = QPushButton(f"{field_name} ({count})")
                btn.setMinimumSize(150, 45)
                btn.setFont(QFont("Arial", 10))
                
                bg_color = '#f8f8f8' if i % 2 == 0 else '#f0f0f0'
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {bg_color};
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                    }}
                    QPushButton:hover {{
                        background: #e0e0e0;
                    }}
                """)
                
                btn.clicked.connect(lambda _, f=field_name: self.apply_categorization(layer, f, dlg))
                grid.addWidget(btn, row, col)
                col += 1
                if col >= 5:  # 5 columns
                    col = 0
                    row += 1
        
        scroll.setWidget(widget)
        layout.addWidget(scroll)
        dlg.setLayout(layout)
        dlg.exec_()

    def apply_categorization(self, layer, field_name, dlg):
        """Apply categorization to layer"""
        dlg.close()

        unique_values = sorted(layer.uniqueValues(layer.fields().lookupField(field_name)))

        if layer.geometryType() == 0:  # Point
            symbol = QgsMarkerSymbol.createSimple({'name': 'diamond', 'size': '4.4'})
        elif layer.geometryType() == 1:  # Line
            symbol = QgsLineSymbol.createSimple({'width': '1.0'})
        else:  # Polygon
            # Create QgsFillSymbol with outline-only configuration
            symbol = QgsFillSymbol()
            # Remove default fill layer and add simple line layer for outline
            symbol.deleteSymbolLayer(0)  # Remove default simple fill layer
            line_layer = QgsSimpleLineSymbolLayer(QColor('#000000'), 1.0)
            symbol.appendSymbolLayer(line_layer)

        categories = []
        for i, value in enumerate(unique_values):
            cat_symbol = symbol.clone()
            if layer.geometryType() == 2:  # For polygons
                cat_symbol.symbolLayer(0).setColor(QColor(self.colors[i % len(self.colors)]))
            else:
                cat_symbol.setColor(QColor(self.colors[i % len(self.colors)]))
            category = QgsRendererCategory(value, cat_symbol, str(value))
            categories.append(category)

        layer.setRenderer(QgsCategorizedSymbolRenderer(field_name, categories))
        
        # Enable feature counts through layer tree
        root = QgsProject.instance().layerTreeRoot()
        layer_tree_layer = root.findLayer(layer)
        if layer_tree_layer:
            layer_tree_layer.setCustomProperty("showFeatureCount", True)
        
        # Force refresh
        layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(layer.id())
        iface.mapCanvas().refreshAllLayers()

    # Tool 8: Rule-Based Methods
    def run_rule_based(self):
        """Run rule-based categorization dialog"""
        layer = self.iface.activeLayer()
        if not layer or not isinstance(layer, QgsVectorLayer):
            return

        # Load saved field selections
        settings = QSettings()
        last_fields = {
            'field1': settings.value("RuleBasedCategorization/field1", ""),
            'field2': settings.value("RuleBasedCategorization/field2", ""),
            'field3': settings.value("RuleBasedCategorization/field3", "(Optional)")
        }

        dlg = QDialog()
        dlg.setWindowTitle("Rule-Based Categorization")
        dlg.setMinimumSize(600, 400)
        dlg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(245, 245, 245))
        dlg.setPalette(palette)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Field selection
        field_layout = QHBoxLayout()
        self.field1_combo = QComboBox()
        self.field2_combo = QComboBox()
        self.field3_combo = QComboBox()
        self.field3_combo.addItem("(Optional)")
        
        fields = [field.name() for field in layer.fields()]
        
        # Populate combos and set saved selections
        for combo, field_name in zip(
            [self.field1_combo, self.field2_combo, self.field3_combo],
            ['field1', 'field2', 'field3']
        ):
            combo.addItems(fields)
            if last_fields[field_name] in fields:
                combo.setCurrentText(last_fields[field_name])
            elif combo == self.field3_combo:
                combo.setCurrentText("(Optional)")
        
        field_layout.addWidget(QLabel("Field 1:"))
        field_layout.addWidget(self.field1_combo)
        field_layout.addWidget(QLabel("Field 2:"))
        field_layout.addWidget(self.field2_combo)
        field_layout.addWidget(QLabel("Field 3:"))
        field_layout.addWidget(self.field3_combo)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Combination", "Count"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Apply button
        btn_apply = QPushButton("Apply Categorization")
        btn_apply.clicked.connect(lambda: self.apply_rule_based_categorization(layer, dlg))
        
        # Connect signals
        for combo in [self.field1_combo, self.field2_combo, self.field3_combo]:
            combo.currentTextChanged.connect(lambda: self.update_rule_based_results(layer))
        
        layout.addLayout(field_layout)
        layout.addWidget(self.results_table)
        layout.addWidget(btn_apply)
        
        dlg.setLayout(layout)
        self.update_rule_based_results(layer)
        dlg.exec_()

    def update_rule_based_results(self, layer):
        """Update results table for rule-based categorization"""
        field1 = self.field1_combo.currentText()
        field2 = self.field2_combo.currentText()
        field3 = self.field3_combo.currentText()
        
        fields = [field1, field2]
        if field3 != "(Optional)":
            fields.append(field3)
        
        combinations = {}
        for feature in layer.getFeatures():
            values = [str(feature[field]) if feature[field] is not None else "NULL" for field in fields]
            combo = " + ".join(values)
            combinations[combo] = combinations.get(combo, 0) + 1
        
        self.results_table.setRowCount(len(combinations))
        for row, (combo, count) in enumerate(combinations.items()):
            self.results_table.setItem(row, 0, QTableWidgetItem(combo))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(count)))

    def apply_rule_based_categorization(self, layer, dlg):
        """Apply rule-based categorization"""
        # Save current field selections
        settings = QSettings()
        settings.setValue("RuleBasedCategorization/field1", self.field1_combo.currentText())
        settings.setValue("RuleBasedCategorization/field2", self.field2_combo.currentText())
        settings.setValue("RuleBasedCategorization/field3", self.field3_combo.currentText())
        
        field1 = self.field1_combo.currentText()
        field2 = self.field2_combo.currentText()
        field3 = self.field3_combo.currentText()
        
        fields = [field1, field2]
        if field3 != "(Optional)":
            fields.append(field3)
        
        categories = []
        for i in range(self.results_table.rowCount()):
            combo = self.results_table.item(i, 0).text()
            count = int(self.results_table.item(i, 1).text())
            
            if layer.geometryType() == 0:  # Point
                symbol = QgsMarkerSymbol.createSimple({'name': 'diamond', 'size': '4.4'})
            elif layer.geometryType() == 1:  # Line
                symbol = QgsLineSymbol.createSimple({'width': '1.0'})
            else:  # Polygon
                # Create QgsFillSymbol with outline-only configuration
                symbol = QgsFillSymbol()
                # Remove default fill layer and add simple line layer for outline
                symbol.deleteSymbolLayer(0)  # Remove default simple fill layer
                line_layer = QgsSimpleLineSymbolLayer(QColor('#000000'), 1.0)
                symbol.appendSymbolLayer(line_layer)
            
            color = QColor(self.colors[i % len(self.colors)])
            if layer.geometryType() == 2:
                symbol.symbolLayer(0).setColor(color)
            else:
                symbol.setColor(color)
            
            # Use clean combo text without counts
            combo_text = combo.split(' [')[0].strip()
            categories.append(QgsRendererCategory(combo, symbol, combo_text))
        
        # Create expression with proper field quoting
        expression = "concat(" + ", ' + ', ".join([f'coalesce(to_string("{field}"), \'NULL\')' for field in fields]) + ")"
        
        # Create and set renderer
        renderer = QgsCategorizedSymbolRenderer(expression, categories)
        layer.setRenderer(renderer)
        
        # Configure feature count display
        layer_tree_layer = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
        if layer_tree_layer:
            layer_tree_layer.setCustomProperty("showFeatureCount", True)
            # Force refresh by toggling visibility
            was_visible = layer_tree_layer.isVisible()
            layer_tree_layer.setItemVisibilityChecked(False)
            layer_tree_layer.setItemVisibilityChecked(True)
            if not was_visible:
                layer_tree_layer.setItemVisibilityChecked(False)
        
        # Refresh everything
        layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(layer.id())
        iface.mapCanvas().refreshAllLayers()
        
        dlg.close()


# NEW SymbologyDialog Class (SVG-based)
class SymbologyDialog(QDialog):
    """Dialog for symbology configuration"""
    
    def __init__(self, layer, parent=None):
        super().__init__(parent)
        self.layer = layer
        self.geometry_type = layer.geometryType()
        self.svg_folder = os.path.join(os.path.dirname(__file__), 'svg')
        
        # Color palette
        self.colors = [
            '#e41a1c', '#3579b1', '#00e4f6', '#0000ff', '#ff00ff', '#ff69b4',
            '#5e17eb', '#ffa500', '#00fa9a', '#e10052', '#9bbce7', '#c8ff6d',
            '#22c89e', '#ffd93d', '#008e9b', '#ff9671'
        ]
        
        # SVG marker shapes for points
        self.svg_shapes = [
            'diamond_red.svg', 'dot_blue.svg', 'effect_drop_shadow.svg', 
            'honeycomb_faux_3d.svg', 'shield_disability.svg', 'topo_airport.svg',
            'topo_hospital.svg', 'triangle_green.svg'
        ]
        
        # Size options for points (mm)
        self.point_sizes = [6, 7, 8, 9, 10, 11, 12]
        
        # Width options for lines and polygons (mm)
        self.line_widths = [0.3, 0.4, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        
        # Selected values
        self.selected_shape = None
        self.selected_size = 8  # default changed from 9 to 8
        self.selected_width = None
        self.selected_color = None
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Symbology')
        self.setMinimumSize(400, 400)
        self.resize(500, 530)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
                padding: 5px;
            }
            QPushButton:hover {
                border-color: #4CAF50;
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Geometry type label
        geometry_name = self.get_geometry_name()
        title_label = QLabel(f"Configure {geometry_name} Symbology")
        title_label.setStyleSheet("font-size: 16px; margin: 10px 0px;")
        layout.addWidget(title_label)
        
        # Check for missing SVG files
        if self.geometry_type == QgsWkbTypes.PointGeometry:
            missing_svgs = self.check_missing_svgs()
            if missing_svgs:
                error_msg = f"Warning: Missing SVG files: {', '.join(missing_svgs)}"
                error_label = QLabel(error_msg)
                error_label.setStyleSheet("color: red; font-weight: bold; margin: 5px 0px;")
                layout.addWidget(error_label)
        
        # Add geometry-specific controls
        if self.geometry_type == QgsWkbTypes.PointGeometry:
            self.add_point_controls(layout)
        elif self.geometry_type == QgsWkbTypes.LineGeometry:
            self.add_line_controls(layout)
        elif self.geometry_type == QgsWkbTypes.PolygonGeometry:
            self.add_polygon_controls(layout)
        
        # Add color selection
        self.add_color_controls(layout)
        
        # Add buttons
        self.add_action_buttons(layout)
        
        self.setLayout(layout)
    
    def get_geometry_name(self):
        """Get human-readable geometry type name"""
        if self.geometry_type == QgsWkbTypes.PointGeometry:
            return "Point"
        elif self.geometry_type == QgsWkbTypes.LineGeometry:
            return "Line"
        elif self.geometry_type == QgsWkbTypes.PolygonGeometry:
            return "Polygon"
        return "Unknown"
    
    def check_missing_svgs(self):
        """Check for missing SVG files and return list of missing files"""
        missing = []
        for svg_file in self.svg_shapes:
            svg_path = os.path.join(self.svg_folder, svg_file)
            if not os.path.exists(svg_path):
                missing.append(svg_file)
        return missing
    
    def add_point_controls(self, layout):
        """Add point-specific controls"""
        frame = QFrame()
        frame_layout = QVBoxLayout()
        
        # Shape selection
        shape_label = QLabel("Marker Shape:")
        frame_layout.addWidget(shape_label)
        
        shape_grid = QGridLayout()
        self.shape_buttons = []
        
        for i, svg_file in enumerate(self.svg_shapes):
            if i >= 8:  # Limit to 8 shapes as specified
                break
            row = i // 4
            col = i % 4
            
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked, shape=svg_file: self.select_shape(shape))
            
            svg_path = os.path.join(self.svg_folder, svg_file)
            if os.path.exists(svg_path):
                btn.setIcon(QIcon(svg_path))
                btn.setIconSize(QSize(40, 40))
            else:
                btn.setText("?")
                btn.setEnabled(False)
            
            self.shape_buttons.append((btn, svg_file))
            shape_grid.addWidget(btn, row, col)
        
        frame_layout.addLayout(shape_grid)
        
        # Size selection
        size_label = QLabel("Marker Size (mm):")
        frame_layout.addWidget(size_label)
        
        size_layout = QHBoxLayout()
        self.size_buttons = []
        
        for size in self.point_sizes:
            btn = QPushButton(str(size))
            btn.setFixedSize(50, 30)
            btn.clicked.connect(lambda checked, s=size: self.select_size(s))
            self.size_buttons.append(btn)
            size_layout.addWidget(btn)
        
        frame_layout.addLayout(size_layout)
        frame.setLayout(frame_layout)
        layout.addWidget(frame)
    
    def add_line_controls(self, layout):
        """Add line-specific controls"""
        frame = QFrame()
        frame_layout = QVBoxLayout()
        
        width_label = QLabel("Line Width (mm):")
        frame_layout.addWidget(width_label)
        
        width_grid = QGridLayout()
        self.width_buttons = []
        
        for i, width in enumerate(self.line_widths):
            row = i // 5
            col = i % 5
            
            btn = QPushButton(str(width))
            btn.setFixedSize(50, 30)
            btn.clicked.connect(lambda checked, w=width: self.select_width(w))
            self.width_buttons.append(btn)
            width_grid.addWidget(btn, row, col)
        
        frame_layout.addLayout(width_grid)
        frame.setLayout(frame_layout)
        layout.addWidget(frame)
    
    def add_polygon_controls(self, layout):
        """Add polygon-specific controls"""
        frame = QFrame()
        frame_layout = QVBoxLayout()
        
        width_label = QLabel("Outline Width (mm):")
        frame_layout.addWidget(width_label)
        
        width_grid = QGridLayout()
        self.width_buttons = []
        
        for i, width in enumerate(self.line_widths):
            row = i // 5
            col = i % 5
            
            btn = QPushButton(str(width))
            btn.setFixedSize(50, 30)
            btn.clicked.connect(lambda checked, w=width: self.select_width(w))
            self.width_buttons.append(btn)
            width_grid.addWidget(btn, row, col)
        
        frame_layout.addLayout(width_grid)
        frame.setLayout(frame_layout)
        layout.addWidget(frame)
    
    def add_color_controls(self, layout):
        """Add color selection controls"""
        frame = QFrame()
        frame_layout = QVBoxLayout()
        
        color_label = QLabel("Color:")
        frame_layout.addWidget(color_label)
        
        color_grid = QGridLayout()
        self.color_buttons = []
        
        for i, color in enumerate(self.colors):
            row = i // 8
            col = i % 8
            
            btn = QPushButton()
            btn.setFixedSize(50, 30)
            btn.setStyleSheet(f"background-color: {color}; border: 2px solid #ddd;")
            btn.clicked.connect(lambda checked, c=color: self.select_color(c))
            self.color_buttons.append((btn, color))
            color_grid.addWidget(btn, row, col)
        
        frame_layout.addLayout(color_grid)
        frame.setLayout(frame_layout)
        layout.addWidget(frame)
    
    def add_action_buttons(self, layout):
        """Add OK and Cancel buttons"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.setFixedSize(70, 30)
        ok_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(70, 30)
        cancel_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def select_shape(self, shape):
        """Select a marker shape"""
        self.selected_shape = shape
        self.update_shape_selection()
    
    def select_size(self, size):
        """Select marker size"""
        self.selected_size = size
        self.update_size_selection()
    
    def select_width(self, width):
        """Select line/polygon width"""
        self.selected_width = width
        self.update_width_selection()
    
    def select_color(self, color):
        """Select color"""
        self.selected_color = color
        self.update_color_selection()
    
    def update_shape_selection(self):
        """Update visual selection for shapes"""
        for btn, shape in self.shape_buttons:
            if shape == self.selected_shape:
                btn.setStyleSheet("border: 3px solid #4CAF50; background-color: #e8f5e8;")
            else:
                btn.setStyleSheet("")
    
    def update_size_selection(self):
        """Update visual selection for sizes"""
        for btn in self.size_buttons:
            if float(btn.text()) == self.selected_size:
                btn.setStyleSheet("border: 3px solid #4CAF50; background-color: #e8f5e8; font-weight: bold;")
            else:
                btn.setStyleSheet("")
    
    def update_width_selection(self):
        """Update visual selection for widths"""
        for btn in self.width_buttons:
            if float(btn.text()) == self.selected_width:
                btn.setStyleSheet("border: 3px solid #4CAF50; background-color: #e8f5e8; font-weight: bold;")
            else:
                btn.setStyleSheet("")
    
    def update_color_selection(self):
        """Update visual selection for colors"""
        for btn, color in self.color_buttons:
            if color == self.selected_color:
                btn.setStyleSheet(f"background-color: {color}; border: 3px solid #4CAF50;")
            else:
                btn.setStyleSheet(f"background-color: {color}; border: 2px solid #ddd;")
    
    def load_settings(self):
        """Load saved settings"""
        settings = QSettings()
        
        if self.geometry_type == QgsWkbTypes.PointGeometry:
            # Point settings
            try:
                self.selected_shape = settings.value('symbology/point_shape', self.svg_shapes[0] if self.svg_shapes else None)
                self.selected_size = float(settings.value('symbology/point_size', 8))
                self.selected_color = settings.value('symbology/point_color', None)
            except (ValueError, TypeError):
                self.selected_shape = self.svg_shapes[0] if self.svg_shapes else None
                self.selected_size = 8
                self.selected_color = None
            
        elif self.geometry_type == QgsWkbTypes.LineGeometry:
            # Line settings
            try:
                self.selected_width = float(settings.value('symbology/line_width', 0.5))
                self.selected_color = settings.value('symbology/line_color', '#3579b1')
            except (ValueError, TypeError):
                self.selected_width = 0.5
                self.selected_color = '#3579b1'
                
        elif self.geometry_type == QgsWkbTypes.PolygonGeometry:
            # Polygon settings
            try:
                self.selected_width = float(settings.value('symbology/polygon_width', 1.0))
                self.selected_color = settings.value('symbology/polygon_color', '#e41a1c')
            except (ValueError, TypeError):
                self.selected_width = 1.0
                self.selected_color = '#e41a1c'
        
        # Update UI selections
        if hasattr(self, 'shape_buttons'):
            self.update_shape_selection()
        if hasattr(self, 'size_buttons'):
            self.update_size_selection()
        if hasattr(self, 'width_buttons'):
            self.update_width_selection()
        if hasattr(self, 'color_buttons'):
            self.update_color_selection()
    
    def save_settings(self):
        """Save current settings"""
        settings = QSettings()
        
        if self.geometry_type == QgsWkbTypes.PointGeometry:
            if self.selected_shape is not None:
                settings.setValue('symbology/point_shape', self.selected_shape)
            if self.selected_size is not None:
                settings.setValue('symbology/point_size', self.selected_size)
            if self.selected_color is not None:
                settings.setValue('symbology/point_color', self.selected_color)
                
        elif self.geometry_type == QgsWkbTypes.LineGeometry:
            if self.selected_width is not None:
                settings.setValue('symbology/line_width', self.selected_width)
            if self.selected_color is not None:
                settings.setValue('symbology/line_color', self.selected_color)
                
        elif self.geometry_type == QgsWkbTypes.PolygonGeometry:
            if self.selected_width is not None:
                settings.setValue('symbology/polygon_width', self.selected_width)
            if self.selected_color is not None:
                settings.setValue('symbology/polygon_color', self.selected_color)
    
    def apply_symbology(self):
        """Apply selected symbology to the layer"""
        try:
            if self.geometry_type == QgsWkbTypes.PointGeometry:
                self.apply_point_symbology()
            elif self.geometry_type == QgsWkbTypes.LineGeometry:
                self.apply_line_symbology()
            elif self.geometry_type == QgsWkbTypes.PolygonGeometry:
                self.apply_polygon_symbology()
            
            # Refresh layer
            self.layer.triggerRepaint()
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply symbology: {str(e)}")
            return False
    
    def apply_point_symbology(self):
        """Apply point symbology"""
        if not self.selected_shape:
            return
        
        svg_path = os.path.join(self.svg_folder, self.selected_shape)
        if not os.path.exists(svg_path):
            QMessageBox.warning(self, "Warning", f"SVG file not found: {self.selected_shape}")
            return
        
        # Create SVG marker symbol
        symbol = QgsMarkerSymbol()
        svg_layer = QgsSvgMarkerSymbolLayer(svg_path)
        svg_layer.setSize(self.selected_size)
        
        # Apply color only to diamond shape using setColor
        if self.selected_color and self.selected_shape == 'diamond_red.svg':
            svg_layer.setColor(QColor(self.selected_color))
        
        symbol.changeSymbolLayer(0, svg_layer)
        
        # Apply renderer
        renderer = QgsSingleSymbolRenderer(symbol)
        self.layer.setRenderer(renderer)
    
    def apply_line_symbology(self):
        """Apply line symbology"""
        if self.selected_width is None or self.selected_color is None:
            return
        
        symbol = QgsLineSymbol()
        line_layer = QgsSimpleLineSymbolLayer()
        line_layer.setWidth(self.selected_width)
        line_layer.setColor(QColor(self.selected_color))
        line_layer.setPenCapStyle(Qt.RoundCap)
        line_layer.setPenJoinStyle(Qt.RoundJoin)
        
        symbol.changeSymbolLayer(0, line_layer)
        
        renderer = QgsSingleSymbolRenderer(symbol)
        self.layer.setRenderer(renderer)
    
    def apply_polygon_symbology(self):
        """Apply polygon symbology"""
        if self.selected_width is None or self.selected_color is None:
            return
        
        # Use your reference code approach
        # Create QgsFillSymbol with outline-only configuration
        symbol = QgsFillSymbol()
        # Remove default fill layer and add simple line layer for outline
        symbol.deleteSymbolLayer(0)  # Remove default simple fill layer
        line_layer = QgsSimpleLineSymbolLayer(QColor(self.selected_color), self.selected_width)
        symbol.appendSymbolLayer(line_layer)
        
        renderer = QgsSingleSymbolRenderer(symbol)
        self.layer.setRenderer(renderer)


# Labeling Dialog Class (keep this as it is)
class LabelingDialog(QDialog):
    def __init__(self, layer, parent_plugin, parent=None):
        super().__init__(parent)
        self.layer = layer
        self.parent_plugin = parent_plugin
        self.selected_fields = []
        self.selected_text_size = 11  # Default text size
        self.selected_colors = []
        
        # Use parent plugin's color palette and options
        self.colors = parent_plugin.colors
        self.text_sizes = [10, 11, 12, 13, 14, 15]
        
        # Load saved selections for this layer (current project only)
        self.load_layer_settings()
        
        self.init_ui()
        
        # Set default orange color as selected if no colors were loaded
        if not self.selected_colors:
            self.selected_colors = ['#ffa500']
        
        # Update color buttons after UI is fully initialized
        self.update_color_buttons()
        
    def load_layer_settings(self):
        """Load saved field and color selections for this layer (current project only)"""
        # Use project-specific storage instead of persistent QSettings
        project = QgsProject.instance()
        layer_id = self.layer.id()
        
        # Load saved fields from project
        saved_fields = project.readListEntry('labeling_plugin', f'layer_{layer_id}_fields')[0]
        if saved_fields:
            # Verify fields still exist in layer
            current_fields = [field.name() for field in self.layer.fields()]
            self.selected_fields = [field for field in saved_fields if field in current_fields]
        
        # Load saved colors from project
        saved_colors = project.readListEntry('labeling_plugin', f'layer_{layer_id}_colors')[0]
        if saved_colors:
            # Verify colors are valid
            self.selected_colors = [color for color in saved_colors if color in self.colors]
        
    def save_layer_settings(self):
        """Save field and color selections for this layer (current project only)"""
        # Use project-specific storage instead of persistent QSettings
        project = QgsProject.instance()
        layer_id = self.layer.id()
        project.writeEntry('labeling_plugin', f'layer_{layer_id}_fields', self.selected_fields)
        project.writeEntry('labeling_plugin', f'layer_{layer_id}_colors', self.selected_colors)
        
    def init_ui(self):
        self.setWindowTitle("Configure Labels")
        # Make dialog resizable instead of fixed size
        self.setMinimumSize(570, 490)
        self.resize(570, 490)
        self.setStyleSheet("background-color: #f5f5f5;")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Field Selection Section
        field_section = self.create_field_section()
        main_layout.addWidget(field_section)
        
        # Text Size Section
        text_size_section = self.create_text_size_section()
        main_layout.addWidget(text_size_section)
        
        # Color Selection Section
        color_section = self.create_color_section()
        main_layout.addWidget(color_section)
        
        # Spacer
        main_layout.addStretch()
        
        # OK/Cancel Buttons
        button_layout = self.create_button_section()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def create_field_section(self):
        # Container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        
        # Label
        label = QLabel("Select one or more fields to label:")
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("color: #333333;")
        layout.addWidget(label)
        
        # Get layer fields
        fields = [field.name() for field in self.layer.fields()]
        
        # Create scroll area for field buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMaximumHeight(150)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Widget to hold buttons
        button_widget = QWidget()
        
        # Determine layout based on number of fields (5 per row)
        if len(fields) <= 5:
            rows = 1
            cols = len(fields)
        elif len(fields) <= 10:
            rows = 2
            cols = 5
        else:
            rows = (len(fields) + 4) // 5
            cols = 5
        
        grid_layout = QGridLayout(button_widget)
        grid_layout.setSpacing(5)
        
        self.field_buttons = []
        for i, field in enumerate(fields):
            button = QPushButton(field)
            button.setFixedSize(75, 30)  # Increased width 1.5x (50 -> 75)
            button.setFont(QFont("Arial", 10))
            button.setStyleSheet("""
                QPushButton {
                    border: 2px solid #555555;
                    border-radius: 5px;
                    background-color: transparent;
                    color: #333333;
                }
                QPushButton:hover {
                    border-color: #BBBBBB;
                }
                QPushButton:checked {
                    border-color: #04AA6D;
                }
            """)
            button.setCheckable(True)
            button.setChecked(field in self.selected_fields)  # Set saved state
            button.clicked.connect(lambda checked, f=field: self.on_field_selected(f))
            
            row = i // cols
            col = i % cols
            grid_layout.addWidget(button, row, col)
            self.field_buttons.append(button)
        
        scroll_area.setWidget(button_widget)
        layout.addWidget(scroll_area)
        
        return container
        
    def create_text_size_section(self):
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        
        # Label (changed from mm to points)
        label = QLabel("Select text size (points):")
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("color: #333333;")
        layout.addWidget(label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        self.text_size_buttons = []
        for size in self.text_sizes:
            button = QPushButton(str(size))
            button.setFixedSize(50, 30)
            button.setFont(QFont("Arial", 10))
            button.setStyleSheet("""
                QPushButton {
                    border: 2px solid #555555;
                    border-radius: 5px;
                    background-color: transparent;
                    color: #333333;
                }
                QPushButton:hover {
                    border-color: #BBBBBB;
                }
                QPushButton:checked {
                    border-color: #04AA6D;
                }
            """)
            button.setCheckable(True)
            button.setChecked(size == 11)  # Default selection
            button.clicked.connect(lambda checked, s=size: self.on_text_size_selected(s))
            button_layout.addWidget(button)
            self.text_size_buttons.append(button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return container
        
    def create_color_section(self):
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        
        # Label (removed "default: yellow" text)
        label = QLabel("Select text color:")
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("color: #333333;")
        layout.addWidget(label)
        
        # Color grid (2 rows, 8 columns)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)
        
        self.color_buttons = []
        for i, color in enumerate(self.colors):
            button = QPushButton()
            button.setFixedSize(30, 30)
            button.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid {color};
                    border-radius: 5px;
                    background-color: {color};
                }}
                QPushButton:hover {{
                    border-color: {self.get_brighter_color(color)};
                    background-color: {self.get_brighter_color(color)};
                }}
                QPushButton:checked {{
                    border: 3px solid #04AA6D;
                }}
            """)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, c=color: self.on_color_selected(c))
            
            row = i // 8
            col = i % 8
            grid_layout.addWidget(button, row, col)
            self.color_buttons.append(button)
        
        layout.addLayout(grid_layout)
        return container
        
    def update_color_buttons(self):
        """Update color button states based on selected_colors"""
        for i, button in enumerate(self.color_buttons):
            button.setChecked(self.colors[i] in self.selected_colors)
        
    def create_button_section(self):
        layout = QHBoxLayout()
        layout.addStretch()
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(75, 30)  # Increased width 1.5x (50 -> 75)
        ok_button.setFont(QFont("Arial", 10))
        ok_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #555555;
                border-radius: 5px;
                background-color: transparent;
                color: #333333;
            }
            QPushButton:hover {
                border-color: #04AA6D;
                color: #04AA6D;
            }
        """)
        ok_button.clicked.connect(self.apply_labels)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(75, 30)  # Increased width 1.5x (50 -> 75)
        cancel_button.setFont(QFont("Arial", 10))
        cancel_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #555555;
                border-radius: 5px;
                background-color: transparent;
                color: #333333;
            }
            QPushButton:hover {
                border-color: #f44336;
                color: #f44336;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)
        
        return layout
        
    def get_brighter_color(self, hex_color):
        """Generate a brighter version of the given hex color"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Brighten by 20%
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def on_field_selected(self, field_name):
        if field_name in self.selected_fields:
            self.selected_fields.remove(field_name)
        else:
            if len(self.selected_fields) < 3:
                self.selected_fields.append(field_name)
            else:
                # Show error - max 3 fields
                iface.messageBar().pushMessage(
                    "Error", "Maximum 3 fields can be selected!", 
                    level=Qgis.Critical, duration=5
                )
                return
        
        # Update button states
        for button in self.field_buttons:
            button.setChecked(button.text() in self.selected_fields)
            
    def on_text_size_selected(self, size):
        self.selected_text_size = size
        # Update button states (single selection)
        for button in self.text_size_buttons:
            button.setChecked(int(button.text()) == size)
            
    def on_color_selected(self, color):
        if color in self.selected_colors:
            self.selected_colors.remove(color)
        else:
            if len(self.selected_colors) < 3:
                self.selected_colors.append(color)
            else:
                # Replace oldest color if 3 already selected
                self.selected_colors.pop(0)
                self.selected_colors.append(color)
        
        # Update button states
        self.update_color_buttons()
            
    def validate_selection(self):
        """Validate the current selection"""
        if not self.selected_fields:
            iface.messageBar().pushMessage(
                "Error", "At least 1 field must be selected!", 
                level=Qgis.Critical, duration=5
            )
            return False
            
        return True
        
    def apply_labels(self):
        """Apply labels to the layer"""
        if not self.validate_selection():
            return
            
        try:
            # Save current selections for this layer (current project only)
            self.save_layer_settings()
            
            if len(self.selected_fields) == 1:
                self.apply_simple_labeling()
            else:
                self.apply_rule_based_labeling()
                
            # Refresh map
            iface.mapCanvas().refresh()
            
            # Show success message
            iface.messageBar().pushMessage(
                "Success", "Labels applied successfully!", 
                level=Qgis.Success, duration=5
            )
            
            self.accept()
            
        except Exception as e:
            iface.messageBar().pushMessage(
                "Error", f"Failed to apply labels: {str(e)}", 
                level=Qgis.Critical, duration=5
            )
            
    def apply_simple_labeling(self):
        """Apply simple labeling with one field"""
        field = self.selected_fields[0]
        color = self.selected_colors[0] if self.selected_colors else '#ffa500'  # Default to orange
        
        # Create label settings
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = field
        label_settings.enabled = True
        
        # Set text format
        text_format = QgsTextFormat()
        text_format.setFont(QFont("Arial"))
        text_format.setSize(self.selected_text_size)
        text_format.setSizeUnit(QgsUnitTypes.RenderPoints)
        text_format.setColor(self.hex_to_qcolor(color))
        
        label_settings.setFormat(text_format)
        
        # Set placement based on geometry type
        geom_type = self.layer.geometryType()
        if geom_type == 0:  # Point
            label_settings.placement = QgsPalLayerSettings.Placement.OverPoint
            label_settings.xOffset = 0
            label_settings.yOffset = 15
            label_settings.offsetUnits = QgsUnitTypes.RenderPoints
        elif geom_type == 1:  # Line
            label_settings.placement = QgsPalLayerSettings.Placement.Line
        elif geom_type == 2:  # Polygon
            label_settings.placement = QgsPalLayerSettings.Placement.OverPoint
            
        # Apply simple labeling
        simple_labeling = QgsVectorLayerSimpleLabeling(label_settings)
        self.layer.setLabeling(simple_labeling)
        self.layer.setLabelsEnabled(True)
        
    def apply_rule_based_labeling(self):
        """Apply rule-based labeling with multiple fields - each on separate rows (max 3)"""
        rules = QgsRuleBasedLabeling.Rule(QgsPalLayerSettings())
        
        for i, field in enumerate(self.selected_fields):
            # Determine color for this field
            if i < len(self.selected_colors):
                color = self.selected_colors[i]
            else:
                color = '#ffa500'  # Default to orange
                
            # Create label settings for this field
            label_settings = QgsPalLayerSettings()
            label_settings.fieldName = field
            label_settings.enabled = True
            
            # Set text format
            text_format = QgsTextFormat()
            text_format.setFont(QFont("Arial"))
            text_format.setSize(self.selected_text_size)
            text_format.setSizeUnit(QgsUnitTypes.RenderPoints)
            text_format.setColor(self.hex_to_qcolor(color))
            
            label_settings.setFormat(text_format)
            
            # Set placement based on geometry type with offsets
            geom_type = self.layer.geometryType()
            if geom_type == 0:  # Point
                label_settings.placement = QgsPalLayerSettings.Placement.OverPoint
                label_settings.xOffset = 0
                label_settings.yOffset = 15 + (i * 15)  # 15, 30, 45 points
                label_settings.offsetUnits = QgsUnitTypes.RenderPoints
            elif geom_type == 1:  # Line
                label_settings.placement = QgsPalLayerSettings.Placement.Line
                label_settings.yOffset = i * (self.selected_text_size + 2)
                label_settings.offsetUnits = QgsUnitTypes.RenderPoints
            elif geom_type == 2:  # Polygon
                label_settings.placement = QgsPalLayerSettings.Placement.OverPoint
                label_settings.yOffset = i * (self.selected_text_size + 2)
                label_settings.offsetUnits = QgsUnitTypes.RenderPoints
                
            # Create rule for this field
            rule = QgsRuleBasedLabeling.Rule(label_settings)
            rule.setDescription(f"Label {field}")
            rules.appendChild(rule)
            
        # Apply rule-based labeling
        rule_based_labeling = QgsRuleBasedLabeling(rules)
        self.layer.setLabeling(rule_based_labeling)
        self.layer.setLabelsEnabled(True)
        
    def hex_to_qcolor(self, hex_color):
        """Convert hex color to QColor"""
        return QColor(hex_color)