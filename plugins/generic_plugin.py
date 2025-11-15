"""
Generic plugin for unknown XSD schemas.
"""
from typing import Dict, Any, Optional, List
import xml.etree.ElementTree as ET
from .base_plugin import BaseDomainPlugin


class GenericPlugin(BaseDomainPlugin):
    """Generic plugin for unknown XSD schemas."""
    
    def get_domain_name(self) -> str:
        return "generic"
    
    def pre_process_element(self, element: ET.Element, context: Dict[str, Any]) -> Optional[ET.Element]:
        # Generic preprocessing - no modifications
        return element
    
    def post_process_element(self, element: ET.Element, table_name: str, context: Dict[str, Any]) -> None:
        # Generic post-processing - add essential fields if configured
        essential_fields = self.get_essential_fields(table_name)
        if essential_fields:
            self._add_essential_fields(table_name, essential_fields, context)
    
    def _add_essential_fields(self, table_name: str, essential_fields: List[Dict[str, Any]], context: Dict[str, Any]) -> None:
        """Add essential fields to table."""
        tables = context.get('tables', {})
        converter = context.get('converter')
        
        if table_name not in tables or not converter:
            return
        
        table = tables[table_name]
        existing_columns = {col.name for col in table.columns}
        
        for field_def in essential_fields:
            field_name = field_def['name']
            if field_name not in existing_columns:
                converter.add_column_to_table_from_definition(table_name, field_def)
                print(f"  [Generic] Added essential field {field_name} to {table_name}")