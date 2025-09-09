# QuickStyle QGIS Plugin

QuickStyle is a QGIS plugin that simplifies common styling and layer management tasks. It makes actions easier and faster than QGIS native procedures by reducing unnecessary steps. The plugin combines essential tools for CRS settings, symbology, labeling, categorization, and attribute management, helping GIS professionals save time and work more efficiently.

![QuickStyle Cover](/docs/images/1.%20Cover%20Page.png)

---

## Features

![Key Features](/docs/images/2.%20Key%20Features.png)


![CRS Tool](/docs/images/3.%20CRS%20Tool.png)

---


![Add Field Tool](/docs/images/4.%20Add%20Field%20Tool.png)

---


![Open Attribute Table Tool](/docs/images/5.%20Open%20Attribute%20Table%20Tool.png)

---


![Show Selected Features Tool](/docs/images/6.%20Show%20Selected%20Features%20Tool.png)

---


![Symbology Tool for Point Layers](/docs/images/7.a%20Symbology%20Tool%20For%20Point%20Layers.png)

---


![Symbology Tool for Line & Polygon Layers](/docs/images/7.b%20Symbology%20Tool%20For%20Line%20&%20Polygon%20Layers.png)

---


![Labeling Tool](/docs/images/8.%20Labeling%20Tool.png)

---


![Categorize Layer Tool](/docs/images/9.%20Categorize%20Layer%20Tool.png)

---


![Rule-Based Categorize Tool](/docs/images/10.%20Rule-Based%20Categorize%20Tool.png)

---


![Color Palette](/docs/images/11.%20Color%20palette.png)

---

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

---

## Usage

1.  **Select a vector layer** in the QGIS Layers Panel.
2.  **Click on any tool** in the QuickStyle toolbar to apply its function.
3.  Use the intuitive dialogs to configure symbology, labels, or categories to your liking.

---

## Author

**MD Moinul Mobin**  
[mdmoinulmobin@gmail.com](mailto:mdmoinulmobin@gmail.com)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

📄 [Download Full User Guide (PDF)](/docs/QuickStyle_v1.0.pdf)
