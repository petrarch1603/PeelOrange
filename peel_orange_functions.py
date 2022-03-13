import os
import configparser
from qgis.PyQt.QtCore import Qt
from qgis.core import Qgis, \
                      QgsBlurEffect, \
                      QgsClassificationQuantile, \
                      QgsRendererRangeLabelFormat, \
                      QgsStyle, \
                      QgsGraduatedSymbolRenderer, \
                      QgsClassificationEqualInterval, \
                      QgsMessageLog, \
                      QgsRendererRange, \
                      QgsProperty, \
                      QgsLayerMetadata, \
                      QgsSymbol

print(f"Version: {Qgis.version()}")


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


def exclude_layers_from_box(layers: list, project_crs: object) -> list:
    excluded_list = []
    for l in layers:
        if l.crs().mapUnits() == 6:  # 6 is the unit type for degrees
            excluded_list.append(l)
        if l.crs() != project_crs:
            excluded_list.append(l)
    return excluded_list


def set_graduated_symbol(lyr, num_classes=15, threshold=0) -> QgsGraduatedSymbolRenderer:
    value_field = 'abs_delta'
    # Set up label format
    my_format = QgsRendererRangeLabelFormat()  # TODO Deprecation warning, need to update this code
    my_format.setFormat("%1 - %2")
    my_format.setPrecision(3)
    my_format.setTrimTrailingZeroes(True)

    # # Set up the base symbol
    # Set up color ramp
    ramp_name = 'Greys'  # This is a QGIS standard color ramp name
    default_style = QgsStyle().defaultStyle()
    color_ramp = default_style.colorRamp(ramp_name)

    # Set up base symbol
    base_symbol = QgsSymbol.defaultSymbol(lyr.geometryType())
    base_symbol_layer = base_symbol.symbolLayer(0)
    base_symbol_layer.setStrokeWidth(0.4)
    ddp = QgsProperty.fromExpression("@symbol_color")  # This matches the pen color to the fill color (seamless)
    base_symbol_layer.setDataDefinedProperty(base_symbol_layer.PropertyStrokeColor, ddp)

    # # Add blur effect (this will only work on the base symbol)
    # my_blur = QgsBlurEffect()
    # base_symbol_layer.setPaintEffect(my_blur)

    # Set up renderer
    classification_method = QgsClassificationQuantile()
    class_ranges_list = classification_method.classes(layer=lyr, expression=value_field, nclasses=num_classes)
    print(f"Class List: {class_ranges_list}")
    renderer = QgsGraduatedSymbolRenderer()
    # for i in class_ranges_list:  # See https://github.com/qgis/QGIS/issues/47761
    #     print(f"this range is {i}")
    #     try:
    #         j = QgsRendererRange(i)
    #         renderer.addClassRange(j)
    #     except TypeError:
    #         print(i.lowerBound())
    #         renderer.addClassLowerUpper(lower=float(i.lowerBound()), upper=float(i.upperBound()))

    renderer.setSourceSymbol(base_symbol)
    renderer.setClassAttribute(value_field)
    renderer.setClassificationMethod(classification_method)
    renderer.setLabelFormat(my_format)
    renderer.updateColorRamp(color_ramp)
    renderer.updateClasses(vlayer=lyr,
                           mode=QgsGraduatedSymbolRenderer.Quantile,
                           nclasses=num_classes)  # TODO Deprecation warning, need to update this code
    if threshold != 0:
        renderer = disable_ranges(renderer, threshold)
    # Disable values below threshold

    # TODO Set Blur Effect

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


def disable_ranges(renderer, threshold):
    my_delete_list = []
    for index, element in enumerate(renderer.ranges()):
        if element.upperValue() < threshold:
            # element.setRenderState(False)
            my_delete_list.append(index)

    for index in my_delete_list:
        renderer.updateRangeRenderState(index, False)
    if len(my_delete_list) > 1:
        renderer.updateRangeLowerValue((my_delete_list[-1]+1), threshold)
    return renderer
