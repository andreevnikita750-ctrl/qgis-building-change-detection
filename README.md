# QGIS Building Change Detection Plugin

An automated QGIS plugin for detecting and marking building changes by comparing current building layers with historical analog documentation overlays. Identifies moved, removed, and added buildings with visual feedback and detailed statistics.

## Features

- **Intelligent Building Matching**: Uses spatial proximity and confidence scoring to match buildings between layers
- **Change Classification**: Automatically categorizes buildings as:
  - 🟢 **UNCHANGED**: Buildings present in both layers within threshold
  - 🟠 **MOVED**: Buildings displaced beyond threshold distance
  - 🔴 **REMOVED**: Buildings only in historical layer
  - 🔵 **ADDED**: Buildings only in current layer

- **Visual Results**: Color-coded output layer with distance measurements for moved buildings
- **Configurable Analysis**: Adjustable distance and confidence thresholds
- **QGIS Processing Integration**: Full compatibility with QGIS Processing Framework for batch operations
- **Performance Optimized**: Spatial indexing for efficient analysis of large datasets

## Installation

### Requirements
- QGIS 3.16+
- Python 3.6+

### Setup

1. Clone the repository:
```bash
git clone https://github.com/andreevnikita750-ctrl/qgis-building-change-detection.git
cd qgis-building-change-detection
```

2. Install in QGIS plugins directory:
```bash
# Linux/macOS
cp -r src/building_change_detection ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

# Windows
xcopy src\building_change_detection %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
```

3. Restart QGIS and enable the plugin in **Plugins > Manage and Install Plugins**

## Usage

### Basic Workflow

1. **Prepare Data**:
   - Load current buildings layer (polygon layer in QGIS)
   - Load historical buildings layer (from analog documentation, georeferenced)
   - Ensure both layers are in the same coordinate system

2. **Run Analysis**:
   - Go to **Plugins > Building Change Detection > Detect Building Changes**
   - Select current and historical building layers
   - Set distance threshold (default: 50m) - distance considered "moved"
   - Set confidence threshold (default: 0.7) - match quality threshold
   - Click **Analyze**

3. **Interpret Results**:
   - New layer created with color-coded buildings
   - Attributes table shows change type, distances, and confidence scores
   - Use the provided statistics to understand extent of changes

### Advanced: Processing Framework

Use in QGIS Processing for batch operations:

```python
processing.run("building_change_detection:detect_building_changes", {
    'current_layer': current_layer,
    'historical_layer': historical_layer,
    'distance_threshold': 50,
    'confidence_threshold': 0.7,
    'output': 'memory:'
})
```

## Project Structure

```
qgis-building-change-detection/
├── README.md                              # This file
├── requirements.txt                       # Python dependencies
├── metadata.txt                           # QGIS plugin metadata
├── src/building_change_detection/
│   ├── __init__.py                       # Plugin initialization
│   ├── plugin.py                         # Main plugin class
│   ├── core/
│   │   ├── __init__.py
│   │   ├── matcher.py                    # Spatial matching algorithm
│   │   └── analyzer.py                   # Change analysis & classification
│   ├── gui/
│   │   ├── __init__.py
│   │   └── dialog.py                     # User interface dialog
│   └── processing/
│       ├── __init__.py
│       └── provider.py                   # QGIS Processing provider
├── tests/
│   ├── __init__.py
│   ├── test_matcher.py                   # Unit tests for matcher
│   └── test_analyzer.py                  # Unit tests for analyzer
└── examples/
    └── sample_workflow.py                # Example usage script
```

## Algorithm Details

### Building Matching (`matcher.py`)

The matching algorithm uses spatial proximity and confidence scoring:

1. **Spatial Indexing**: Creates spatial index for efficient nearest-neighbor queries
2. **Proximity Matching**: For each building in the current layer, finds nearest building(s) in historical layer
3. **Confidence Scoring**: Calculates confidence based on distance using exponential decay:
   ```
   confidence = exp(-distance² / (2 * threshold²))
   ```
4. **Ambiguity Resolution**: Handles cases where multiple buildings could match

### Change Analysis (`analyzer.py`)

Classification based on matching results:

- **MOVED**: Matched buildings with distance > threshold
- **REMOVED**: Historical buildings with no match in current layer
- **ADDED**: Current buildings with no match in historical layer
- **UNCHANGED**: Matched buildings with distance ≤ threshold

## Configuration

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `distance_threshold` | meters | 50 | Maximum distance for buildings to be considered unchanged |
| `confidence_threshold` | 0.0-1.0 | 0.7 | Minimum confidence score for accepting a match |

### Output Layer Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `change_type` | string | UNCHANGED, MOVED, REMOVED, or ADDED |
| `distance_moved` | float | Distance moved (meters) - only for MOVED |
| `confidence` | float | Match confidence score |
| `old_fid` | integer | Feature ID in historical layer |
| `new_fid` | integer | Feature ID in current layer |

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Building Documentation

```bash
pip install sphinx
cd docs
make html
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on [GitHub Issues](https://github.com/andreevnikita750-ctrl/qgis-building-change-detection/issues)
- Check existing documentation and examples
- Review the [QGIS Plugin Development Guide](https://docs.qgis.org/3.28/en/docs/pyqgis_developer_cookbook/)

## Acknowledgments

Built for automated conversion of analog design documentation into enterprise geographic information systems.

---

**Version**: 1.0.0  
**Author**: Development Team  
**Last Updated**: 2026-05-06
