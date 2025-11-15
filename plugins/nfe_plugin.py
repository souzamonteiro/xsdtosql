"""
NF-e (Brazilian Electronic Invoice) specific plugin.
Completely fixed implementation with proper field handling.
"""
from typing import Dict, Any, Optional, List
import xml.etree.ElementTree as ET
import re
from .base_plugin import BaseDomainPlugin


class NFePlugin(BaseDomainPlugin):
    """NF-e specific plugin with Brazilian tax document rules."""
    
    def get_domain_name(self) -> str:
        return "nfe"
    
    def pre_process_element(self, element: ET.Element, context: Dict[str, Any]) -> Optional[ET.Element]:
        """Pre-process element before standard conversion."""
        element_name = element.get("name")
        
        # NF-e specific element filtering
        if element_name in ["Signature", "SignedInfo", "SignatureValue"]:
            # Skip XML signature elements for NF-e
            return None
        
        return element
    
    def post_process_element(self, element: ET.Element, table_name: str, context: Dict[str, Any]) -> None:
        """Add NF-e specific essential fields with proper handling."""
        essential_fields = self.get_essential_fields(table_name)
        if essential_fields:
            self._add_nfe_essential_fields(table_name, essential_fields, context)
    
    def _add_nfe_essential_fields(self, table_name: str, essential_fields: List[Dict[str, Any]], context: Dict[str, Any]) -> None:
        """Add NF-e essential fields like CNPJ/CPF with duplicate prevention and proper ordering."""
        tables = context.get('tables', {})
        converter = context.get('converter')
        
        if table_name not in tables or not converter:
            return
        
        table = tables[table_name]
        
        # Create a set of existing column names for duplicate checking
        existing_columns = {col.name for col in table.columns}
        
        for field_def in essential_fields:
            field_name = field_def['name']
            
            # Check if field already exists (from XSD or previous addition)
            if field_name in existing_columns:
                # Field already exists, ensure it has the correct type from override
                self._ensure_correct_field_type(table, field_name, field_def)
                print(f"  [NF-e] Field {field_name} already exists in {table_name}, type verified")
            else:
                # Field doesn't exist, add it with proper positioning
                self._add_essential_field_with_ordering(table, field_def, table_name)
                print(f"  [NF-e] Added essential field {field_name} to {table_name}")
    
    def _ensure_correct_field_type(self, table: Any, field_name: str, field_def: Dict[str, Any]) -> None:
        """Ensure existing field has the correct type from field overrides."""
        correct_type = field_def['type']
        
        # Find the existing column and update its type if needed
        for column in table.columns:
            if column.name == field_name and column.data_type != correct_type:
                print(f"  [NF-e] Correcting {field_name} type from {column.data_type} to {correct_type}")
                column.data_type = correct_type
    
    def _add_essential_field_with_ordering(self, table: Any, field_def: Dict[str, Any], table_name: str) -> None:
        """Add essential field with proper ordering (after ID and FK, before regular columns)."""
        from main import Column  # Import here to avoid circular dependency
        
        column = Column(
            name=field_def['name'],
            data_type=field_def['type'],
            is_required=field_def.get('required', False),
            is_choice_element=False
        )
        
        # Calculate insertion position: after ID and FKs, before regular columns
        insert_position = self._calculate_insert_position(table)
        
        # Insert the essential field at the calculated position
        table.columns.insert(insert_position, column)
    
    def _calculate_insert_position(self, table: Any) -> int:
        """Calculate the correct position to insert essential fields."""
        # Start after ID (position 1)
        position = 1
        
        # Move past any foreign key columns
        for i, column in enumerate(table.columns[1:], start=1):
            if column.is_foreign_key:
                position = i + 1
            else:
                # Stop at first non-FK column
                break
        
        return position
    
    def get_custom_type_mapping(self, xsd_type: str) -> Optional[str]:
        """NF-e specific type mappings with comprehensive coverage."""
        # First try the configured custom types
        custom_type = super().get_custom_type_mapping(xsd_type)
        if custom_type:
            return custom_type
        
        # Additional NF-e type inference rules
        if "TDec" in xsd_type:
            # Handle different decimal precisions
            if "0302" in xsd_type or "0504" in xsd_type:
                return "NUMERIC(5,4)"
            elif "0803" in xsd_type:
                return "NUMERIC(11,3)"
            elif "1104" in xsd_type:
                return "NUMERIC(15,4)"
            elif "1110" in xsd_type:
                return "NUMERIC(21,10)"
            elif "1204" in xsd_type:
                return "NUMERIC(16,4)"
            else:
                return "NUMERIC(15,2)"
        elif "TString" in xsd_type or "xs:string" in xsd_type:
            return "VARCHAR(255)"
        
        return None
    
    def get_field_override(self, field_name: str) -> Optional[str]:
        """Get field-specific type override with comprehensive coverage."""
        field_overrides = self.config.get('field_overrides', {})
        
        # Direct override from config
        if field_name in field_overrides:
            return field_overrides[field_name]
        
        # Additional programmatic overrides based on field name patterns
        if field_name == "NCM":
            return "VARCHAR(8)"
        elif field_name in ["cEAN", "cEANTrib"]:
            return "VARCHAR(14)"
        elif field_name == "CFOP":
            return "CHAR(4)"
        elif field_name == "idEstrangeiro":
            return "VARCHAR(20)"
        elif field_name == "placa":
            return "VARCHAR(7)"  # Brazilian license plates can have 7 chars
        
        return None
    
    def should_create_table(self, element: ET.Element, parent_table: Optional[str] = None) -> bool:
        """NF-e specific table creation rules."""
        element_name = element.get("name")
        
        # NF-e specific: some simple elements should be columns even if they have attributes
        simple_elements = ["CPF", "CNPJ", "IE", "email", "fone", "CEP"]
        if element_name in simple_elements:
            return False
        
        return super().should_create_table(element, parent_table)