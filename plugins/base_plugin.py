"""
Base plugin class for domain-specific XSD to SQL conversion rules.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET


class BaseDomainPlugin(ABC):
    """Abstract base class for domain-specific plugins."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.domain = config.get('domain', 'generic')
    
    @abstractmethod
    def get_domain_name(self) -> str:
        """Return the domain name this plugin handles."""
        pass
    
    def pre_process_element(self, element: ET.Element, context: Dict[str, Any]) -> Optional[ET.Element]:
        """
        Pre-process element before standard conversion.
        Return modified element or None to skip processing.
        """
        return element
    
    def post_process_element(self, element: ET.Element, table_name: str, context: Dict[str, Any]) -> None:
        """
        Post-process element after standard conversion.
        Add domain-specific columns or modifications.
        """
        pass
    
    def get_custom_type_mapping(self, xsd_type: str) -> Optional[str]:
        """Get custom SQL type mapping for XSD type."""
        custom_types = self.config.get('custom_types', {})
        return custom_types.get(xsd_type)
    
    def get_field_override(self, field_name: str) -> Optional[str]:
        """Get field-specific type override with pattern matching."""
        field_overrides = self.config.get('field_overrides', {})
        
        # Direct match
        if field_name in field_overrides:
            return field_overrides[field_name]
        
        # Pattern-based matching for common field types
        field_lower = field_name.lower()
        
        # CNPJ/CPF patterns
        if 'cnpj' in field_lower:
            return "CHAR(14)"
        elif 'cpf' in field_lower:
            return "CHAR(11)"
        elif 'ie' in field_lower:  # Inscrição Estadual
            return "VARCHAR(14)"
        elif 'cmun' in field_lower:  # Código Município
            return "CHAR(7)"
        elif 'cuf' in field_lower:  # Código UF
            return "CHAR(2)"
        elif 'cep' in field_lower:  # CEP
            return "CHAR(8)"
        elif 'fone' in field_lower or 'telefone' in field_lower:  # Phone
            return "VARCHAR(20)"
        elif 'email' in field_lower:
            return "VARCHAR(60)"
        
        return None

    
    def get_essential_fields(self, table_name: str) -> List[Dict[str, Any]]:
        """Get essential fields to add to specific tables."""
        essential_fields = self.config.get('essential_fields', {})
        return essential_fields.get(table_name, [])
    
    def should_create_table(self, element: ET.Element, parent_table: Optional[str] = None) -> bool:
        """
        Determine if element should become a table.
        Override for domain-specific table creation rules.
        """
        # Default implementation - use complex element detection
        return self._is_complex_element(element)
    
    def _is_complex_element(self, element: ET.Element) -> bool:
        """Enhanced complex element detection with NF-e specific rules."""
        xsd_ns = self.config.get('xsd_namespace', 'http://www.w3.org/2001/XMLSchema')
        
        # Elements with complexType are always complex
        if element.find(f".//{{{xsd_ns}}}complexType") is not None:
            return True
        
        # Elements with sequence, choice, or all are complex
        if (element.find(f".//{{{xsd_ns}}}sequence") is not None or
            element.find(f".//{{{xsd_ns}}}choice") is not None or
            element.find(f".//{{{xsd_ns}}}all") is not None):
            return True
        
        # Elements with attributes and simple content might still be columns
        has_attributes = len(element.attrib) > 0
        if has_attributes:
            # For NF-e, elements with attributes but simple content are usually columns
            return False
        
        # Elements that can occur multiple times are usually tables
        max_occurs = element.get("maxOccurs")
        if max_occurs and (max_occurs == "unbounded" or max_occurs.isdigit() and int(max_occurs) > 1):
            return True
        
        return False
    
    def get_root_complex_type_prefixes(self) -> List[str]:
        """Get prefixes for complex types that should be root tables."""
        return self.config.get('root_complex_type_prefixes', ['T'])