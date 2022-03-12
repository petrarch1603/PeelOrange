import os
import configparser
from qgis.PyQt.QtCore import Qt
from qgis.core import Qgis, \
                      QgsClassificationQuantile, \
                      QgsRendererRangeLabelFormat, \
                      QgsStyle, \
                      QgsGraduatedSymbolRenderer, \
                      QgsClassificationEqualInterval, \
                      QgsMessageLog, \
                      QgsProperty, \
                      QgsLayerMetadata, \
                      QgsSymbol


def resolve_path(name, basepath=None):
    if not basepath:
      basepath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basepath, name)


def get_file_path(filename: str) -> str:
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        filename))


def read_metadata_txt(filename: str) -> dict:
    metadata = []
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(get_file_path(filename))
    metadata.extend(parser.items('general'))
    return dict(metadata)


def exclude_degrees_layers(layers: list) -> list:
    excluded_list = []
    for l in layers:
        if l.crs().mapUnits() == 6:  # 6 is the unit type for degrees
            excluded_list.append(l)
    return excluded_list


def set_graduated_symbol(lyr, num_classes=15) -> QgsGraduatedSymbolRenderer:
    ramp_name = 'Greys' # This is a QGIS standard color ramp name
    value_field = 'abs_delta'
    classification_method = QgsClassificationQuantile()
    # Set up label format
    my_format = QgsRendererRangeLabelFormat()
    my_format.setFormat("%1 - %2")
    my_format.setPrecision(3)
    my_format.setTrimTrailingZeroes(True)

    # Set up the base symbol
    default_style = QgsStyle().defaultStyle()
    color_ramp = default_style.colorRamp(ramp_name)
    base_symbol = QgsSymbol.defaultSymbol(lyr.geometryType())
    base_symbol_layer = base_symbol.symbolLayer(0)
    base_symbol_layer.setStrokeWidth(0.4)
    ddp = QgsProperty.fromExpression("@symbol_color")  # This matches the pen color to the fill color (seamless)
    base_symbol_layer.setDataDefinedProperty(base_symbol_layer.PropertyStrokeColor, ddp)

    # Set up renderer
    renderer = QgsGraduatedSymbolRenderer()
    renderer.setSourceSymbol(base_symbol)
    renderer.setClassAttribute(value_field)
    renderer.setClassificationMethod(classification_method)
    renderer.setLabelFormat(my_format)
    renderer.updateColorRamp(color_ramp)
    renderer.updateClasses(vlayer=lyr,
                           mode=QgsGraduatedSymbolRenderer.Quantile,
                           nclasses=num_classes)
    return renderer


def post_log_message(msg: str) -> None:
    QgsMessageLog.logMessage(f"{msg}",
                             "Peel_Orange",
                             level=Qgis.Info)


def add_metadata_to_layer(lyr, meta_str: str):
    m = QgsLayerMetadata()
    my_str = 'Created with Peel Orange\nhttps://github.com/petrarch1603/PeelOrange\n'
    my_str += meta_str
    m.setAbstract(my_str)
    lyr.setMetadata(m)
