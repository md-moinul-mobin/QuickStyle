# QuickStyle QGIS Plugin

A powerful and user-friendly QGIS plugin for quick styling and management of vector layers. Streamline your workflow with dozens of easy, time-saving features accessible from a dedicated toolbar.

![QuickStyle Toolbar](img/toolbar_preview.png) <!-- Consider adding a screenshot of your toolbar later -->

## Features

### 1. CRS Tool
*   **Easy Dropdown Menu**: Set the map projection for any layer (vector or raster) with a single click.
*   **Quick Buttons**: Instantly apply common projections like EPSG:28992 (RD New), EPSG:2154 (Lambert-93), EPSG:31370 (Belgian Lambert 72), and EPSG:3857 (Pseudo-Mercator).
*   **Full Flexibility**: Use the "Choose Other" button to select any projection from the native QGIS CRS dialog.

### 2. Add Field Tool
*   **Two-Click Workflow**: Add a new field to your layer's attribute table faster than ever.
*   **Smart Dialog**: Choose the field name, type (Text, Integer, Decimal, Date), and length.
*   **Auto-Save**: Changes are committed and saved automatically.

### 3. Open Attribute Table Tool
*   **One-Click Access**: Open the selected layer's attribute table instantly.
*   **View All Data**: Quickly see and manage all the information for your features.

### 4. Show Selected Features Tool
*   **Instant Filtering**: Filter the attribute table to show only your selected features with a single click.
*   **Focus on Data**: It instantly hides all unselected records, allowing you to focus on your area of interest.

### 5. Symbology Tool
*   **For Point Layers**:
    *   Choose from 8 different and attractive SVG shapes.
    *   Set the marker size with options from 6mm to 12mm.
    *   Apply a color from the 16-color palette.
*   **For Line & Polygon Layers**:
    *   Adjust the stroke thickness from a fine 0.3mm up to a bold 4.0mm.
    *   Apply a color from the 16-color palette.
    *   Polygons are automatically styled with a clean outline for better visualization and cartography.

### 6. Labeling Tool
*   **Multi-Field Labels**: Show labels from up to three different fields at once, each in a different color.
*   **Full Control**: Set the text size from 10 to 15 points.
*   **Visual Appeal**: Choose colors from the standard 16-color palette to make your map clear and informative.

### 7. Categorize Layer Tool
*   **Two-Click Categorization**: Automatically style a layer based on a chosen field value with just two clicks.
    *   **1.** Click the tool.
    *   **2.** Click the field.
*   **Automatic Styling**: Each unique value is assigned a unique color from the 16-color palette.
*   **Smart Defaults**: It automatically shows the feature count for each category directly in the QGIS Layers Panel.

### 8. Rule-Based Categorize Tool
*   **Advanced Grouping**: Create complex categories by combining values from up to three different fields.
*   **Informed Decisions**: See a live preview of all unique combinations and their counts in the dialog before applying.
*   **Clear Visualization**: Each unique combination automatically receives a distinct color.
*   **Detailed Legends**: Feature counts for all combinations are automatically displayed in the Layers Panel.

## Installation

### For Users (Install from ZIP)
1.  Download the latest `QuickStyle.zip` release from the [Releases](../../releases) page.
2.  In QGIS, go to `Plugins` > `Manage and Install Plugins...` > `Install from ZIP`.
3.  Select the downloaded `.zip` file and click **Install Plugin**.
4.  The `QuickStyle` toolbar will appear. Enable it from `Plugins` > `QuickStyle` if it's not visible.

### For Developers (Clone Repository)
1.  Clone this repository directly into your QGIS plugins directory:
    ```bash
    # On Windows:
    cd %APPDATA%/QGIS/QGIS3/profiles/default/python/plugins
    git clone https://github.com/YourUserName/QuickStyle-QGIS-Plugin.git QuickStyle
    ```
    ```bash
    # On Linux/macOS:
    cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
    git clone https://github.com/YourUserName/QuickStyle-QGIS-Plugin.git QuickStyle
    ```
2.  Restart QGIS.
3.  Enable the plugin in the plugin manager: `Plugins` > `Manage and Install Plugins...` > `Installed` > Check `QuickStyle`.

## Usage

1.  **Select a vector layer** in the QGIS Layers Panel.
2.  **Click on any tool** in the QuickStyle toolbar to apply its function.
3.  Use the intuitive dialogs to configure symbology, labels, or categories to your liking.

## Author

**MD Moinul Mobin**  
[mdmoinulmobin@gmail.com](mailto:mdmoinulmobin@gmail.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
