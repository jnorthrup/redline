import logging
from ..line_chopping_refactor import render_mermaid_diagram, scan_code


def dsl_visualization_visitor_before(code: str, flavor: str):
    """
    Performs DSL visualization before transformations.
    """
    logging.debug("Executing DSLVisualizationVisitor (Before)")
    mermaid_diagram = render_mermaid_diagram(scan_code(code, flavor))
    print("Mermaid Diagram Before Refactoring:")
    print(mermaid_diagram)


def dsl_visualization_visitor_after(code: str, flavor: str):
    """
    Performs DSL visualization after transformations.
    """
    logging.debug("Executing DSLVisualizationVisitor (After)")
    mermaid_diagram = render_mermaid_diagram(scan_code(code, flavor))
    print("Mermaid Diagram After Refactoring:")
    print(mermaid_diagram)
