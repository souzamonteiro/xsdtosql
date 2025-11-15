#!/usr/bin/env python3
"""
Generalized XSD to SQL Database Schema Converter
Supports multiple domains via plugins and external configuration
"""
import xml.etree.ElementTree as ET
import re
import sys
import os
import yaml
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

# Import plugins and configuration
from plugins.nfe_plugin import NFePlugin
from plugins.generic_plugin import GenericPlugin
from plugins.base_plugin import BaseDomainPlugin


@dataclass
class Column:
    """Represents a database column"""
    name: str
    data_type: str
    is_required: bool
    max_length: Optional[int] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: Optional[str] = None
    is_choice_element: bool = False


@dataclass
class Table:
    """Represents a database table"""
    name: str
    columns: List[Column]
    primary_key: str = "id"
    parent_table: Optional[str] = None


class GeneralizedXSDToSQLConverter:
    """
    Generalized converter with plugin system and external configuration
    """
    
    def __init__(self, config_dir: str = "config/domains"):
        self.config_dir = config_dir
        self.tables: Dict[str, Table] = {}
        self.current_path: List[str] = []
        self.processed_elements: Set[str] = set()
        self.parent_map: Dict[ET.Element, ET.Element] = {}
        self.choice_groups: Dict[str, List[str]] = {}
        
        # Plugin system
        self.plugins: Dict[str, BaseDomainPlugin] = {}
        self.current_plugin: Optional[BaseDomainPlugin] = None
        self.current_config: Dict[str, Any] = {}
        
        # Load available plugins
        self._load_plugins()
    
    def _load_plugins(self) -> None:
        """Load all available domain plugins."""
        # Load configurations first
        configs = self._load_domain_configs()
        print(f"Debug: Loaded configurations for domains: {list(configs.keys())}")
        
        # Register plugins
        for domain, config in configs.items():
            if domain == "nfe":
                self.plugins[domain] = NFePlugin(config)
                print(f"Debug: Registered NF-e plugin")
            else:
                self.plugins[domain] = GenericPlugin(config)
        
        print(f"Loaded plugins for domains: {list(self.plugins.keys())}")
    
    def _load_domain_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load all domain configurations from YAML files."""
        configs = {}
        
        try:
            config_files = [f for f in os.listdir(self.config_dir) 
                        if f.endswith('.yaml') and not f.startswith('_')]
            
            for config_file in config_files:
                domain = config_file.replace('.yaml', '')
                config_path = os.path.join(self.config_dir, config_file)
                
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                configs[domain] = config
            
        except Exception as e:
            print(f"Warning: Could not load domain configurations: {e}")
            # Fallback to built-in generic config
            configs['generic'] = self._get_default_generic_config()
        
        return configs
    
    def _load_single_config(self, domain: str) -> Optional[Dict[str, Any]]:
        """Load single domain configuration."""
        config_path = os.path.join(self.config_dir, f"{domain}.yaml")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return None
    
    def _get_default_generic_config(self) -> Dict[str, Any]:
        """Get default generic configuration."""
        return {
            'domain': 'generic',
            'defaults': {
                'string_size': 255,
                'numeric_precision': 15,
                'numeric_scale': 2
            },
            'pattern_mappings': [
                {'pattern': r'\[0-9\]\{4\}', 'sql_type': 'CHAR(4)'},
                {'pattern': r'\[0-9\]\{14\}', 'sql_type': 'CHAR(14)'}
            ],
            'root_complex_type_prefixes': ['T'],
            'xsd_namespace': 'http://www.w3.org/2001/XMLSchema'
        }
    
    def detect_domain(self, xsd_root: ET.Element) -> str:
        """Detect the domain of the XSD schema automatically."""
        # Convert root to string for pattern matching
        root_str = ET.tostring(xsd_root, encoding='unicode')
        
        print(f"Debug: Analyzing schema for domain detection...")
        
        # Check each plugin's namespace indicators
        for domain, plugin in self.plugins.items():
            config = plugin.config
            namespace_indicators = config.get('namespace_indicators', [])
            root_indicators = config.get('root_element_indicators', [])
            
            # Check namespace patterns
            for ns in namespace_indicators:
                if ns in root_str:
                    print(f"Detected domain '{domain}' by namespace: {ns}")
                    return domain
            
            # Check root element names in the entire tree
            for elem in xsd_root.iter():
                elem_name = elem.get('name')
                if elem_name and elem_name in root_indicators:
                    print(f"Detected domain '{domain}' by root element: {elem_name}")
                    return domain
            
            # Additional check: look for domain-specific complex types
            complex_types = xsd_root.findall(f".//{{{self.current_config.get('xsd_namespace', 'http://www.w3.org/2001/XMLSchema')}}}complexType")
            for ct in complex_types:
                ct_name = ct.get('name')
                if ct_name and ct_name in root_indicators:
                    print(f"Detected domain '{domain}' by complexType: {ct_name}")
                    return domain
        
        # Fallback: check for common NF-e patterns
        if any(indicator in root_str for indicator in ['TNFe', 'TEnviNFe', 'TProtNFe', 'infNFe']):
            print("Detected domain 'nfe' by common element patterns")
            return "nfe"
        
        # Fallback to generic
        print("No specific domain detected, using 'generic'")
        return "generic"
    
    def build_parent_map(self, element: ET.Element) -> None:
        """Build a parent map for the XML tree"""
        for child in element:
            self.parent_map[child] = element
            self.build_parent_map(child)
    
    def get_parent(self, element: ET.Element) -> Optional[ET.Element]:
        """Get parent element using the parent map"""
        return self.parent_map.get(element)
    
    def parse_xsd_file(self, file_path: str) -> ET.ElementTree:
        """Parse XSD file and return ElementTree"""
        try:
            tree = ET.parse(file_path)
            self.build_parent_map(tree.getroot())
            return tree
        except ET.ParseError as e:
            print(f"Error parsing XSD file {file_path}: {e}")
            raise
    
    def is_choice_element(self, element: ET.Element) -> bool:
        """Check if element is part of a choice group"""
        if not self.current_plugin:
            return False
            
        parent = self.get_parent(element)
        xsd_ns = self.current_config.get('xsd_namespace', 'http://www.w3.org/2001/XMLSchema')
        return parent is not None and parent.tag.endswith('choice')
    
    def get_choice_siblings(self, element: ET.Element) -> List[str]:
        """Get names of sibling elements in a choice group"""
        parent = self.get_parent(element)
        if parent is None or not parent.tag.endswith('choice'):
            return []
        
        return [child.get('name') for child in parent 
                if child.tag.endswith('element') and child.get('name')]
    
    def extract_simple_type_info(self, simple_type_element: ET.Element) -> Tuple[str, Optional[int], List[str]]:
        """
        Extract data type, max length, and patterns from simpleType element
        """
        if not self.current_plugin:
            return "VARCHAR(255)", 255, []
        
        defaults = self.current_config.get('defaults', {})
        data_type = f"VARCHAR({defaults.get('string_size', 255)})"
        max_length = defaults.get('string_size', 255)
        patterns = []
        
        xsd_ns = self.current_config.get('xsd_namespace', 'http://www.w3.org/2001/XMLSchema')
        restriction = simple_type_element.find(f".//{{{xsd_ns}}}restriction")
        
        if restriction is not None:
            base_type = restriction.get("base", "")
            
            # Try plugin-specific type mapping first
            if self.current_plugin:
                custom_type = self.current_plugin.get_custom_type_mapping(base_type)
                if custom_type:
                    data_type = custom_type
            
            # Extract maxLength
            max_length_elem = restriction.find(f".//{{{xsd_ns}}}maxLength")
            if max_length_elem is not None:
                try:
                    max_length = int(max_length_elem.get("value", str(max_length)))
                    if data_type.startswith("VARCHAR"):
                        data_type = f"VARCHAR({max_length})"
                except ValueError:
                    pass
            
            # Extract patterns for enhanced type detection
            pattern_elems = restriction.findall(f".//{{{xsd_ns}}}pattern")
            for pattern_elem in pattern_elems:
                pattern = pattern_elem.get("value", "")
                patterns.append(pattern)
                
                # Use pattern-based mapping from configuration
                pattern_mappings = self.current_config.get('pattern_mappings', [])
                for pattern_map in pattern_mappings:
                    if re.search(pattern_map['pattern'], pattern):
                        data_type = pattern_map['sql_type']
                        break
            
            # Extract length from pattern if max_length not set
            if max_length == defaults.get('string_size', 255) and patterns:
                for pattern in patterns:
                    length_match = re.search(r'\{(\d+)\}', pattern)
                    if length_match:
                        try:
                            max_length = int(length_match.group(1))
                            if data_type.startswith("VARCHAR"):
                                data_type = f"VARCHAR({max_length})"
                            break
                        except ValueError:
                            pass
        
        # Ensure valid data type
        if data_type == "VARCHAR(0)":
            data_type = f"VARCHAR({defaults.get('string_size', 255)})"
        
        return data_type, max_length, patterns
    
    def get_element_context(self, element: ET.Element, current_path: List[str]) -> str:
        """Get context path for element to avoid duplicates"""
        return '_'.join(current_path)
    
    def process_element(self, element: ET.Element, parent_table: str = None, current_path: List[str] = None) -> None:
        """Process an XSD element and create corresponding table/column"""
        if current_path is None:
            current_path = []
        
        if not self.current_plugin:
            return
            
        element_name = element.get("name")
        if not element_name:
            return
        
        # Let plugin pre-process the element
        context = {
            'tables': self.tables,
            'current_path': current_path,
            'parent_table': parent_table,
            'converter': self
        }
        
        processed_element = self.current_plugin.pre_process_element(element, context)
        if processed_element is None:
            return  # Plugin decided to skip this element
        
        element = processed_element
        
        # Create unique identifier for this element in its context
        element_context = self.get_element_context(element, current_path)
        element_id = f"{element_name}|{element_context}"
        
        # Avoid processing the same element multiple times in different contexts
        if element_id in self.processed_elements:
            return
        
        self.processed_elements.add(element_id)
        current_path.append(element_name)
        
        # Let plugin decide if this should be a table
        if self.current_plugin.should_create_table(element, parent_table):
            self.create_table_from_complex_element(element, element_name, parent_table, element_context)
        else:
            self.add_column_to_table(element, element_name, parent_table)
        
        # Let plugin post-process the element
        table_name = parent_table if not self.current_plugin.should_create_table(element, parent_table) else element_name
        self.current_plugin.post_process_element(element, table_name, context)
        
        current_path.pop()
    
    def create_table_from_complex_element(self, element: ET.Element, table_name: str, 
                                        parent_table: str = None, context: str = "") -> None:
        """Create a new table from complex XSD element"""
        
        # Handle duplicate table names in different contexts
        final_table_name = table_name
        if table_name in self.tables:
            context_suffix = f"_{parent_table}" if parent_table else "_root"
            final_table_name = f"{table_name}{context_suffix}"
        
        print(f"Creating table: {final_table_name} (parent: {parent_table})")
        
        # Initialize table with ID column
        columns = [Column("id", "SERIAL", True, is_primary_key=True)]
        
        # Add foreign key to parent table if exists
        if parent_table:
            fk_column = Column(f"{parent_table.lower()}_id", "INTEGER", True, 
                             is_foreign_key=True, references=parent_table)
            columns.append(fk_column)
        
        table = Table(name=final_table_name, columns=columns, parent_table=parent_table)
        self.tables[final_table_name] = table
        
        # Process child elements
        xsd_ns = self.current_config.get('xsd_namespace', 'http://www.w3.org/2001/XMLSchema')
        complex_type = element.find(f".//{{{xsd_ns}}}complexType")
        
        if complex_type is not None:
            self.process_complex_type(complex_type, final_table_name)
        else:
            # Process direct children for elements without explicit complexType
            self.process_element_children(element, final_table_name)
    
    def process_element_children(self, element: ET.Element, table_name: str) -> None:
        """Process direct children of an element"""
        xsd_ns = self.current_config.get('xsd_namespace', 'http://www.w3.org/2001/XMLSchema')
        
        # Process sequence
        sequence = element.find(f".//{{{xsd_ns}}}sequence")
        if sequence is not None:
            for child in sequence:
                if child.tag.endswith('element'):
                    self.process_element(child, table_name)
        
        # Process choice
        choice = element.find(f".//{{{xsd_ns}}}choice")
        if choice is not None:
            choice_elements = []
            for child in choice:
                if child.tag.endswith('element'):
                    choice_elements.append(child.get('name'))
                    self.process_element(child, table_name)
            
            # Store choice group information
            if choice_elements:
                self.choice_groups[table_name] = choice_elements
    
    def add_column_to_table(self, element: ET.Element, column_name: str, table_name: str) -> None:
        """Add a column to an existing table with proper field override handling."""
        if table_name not in self.tables:
            print(f"Warning: Table {table_name} not found for column {column_name}")
            return
        
        if not self.current_plugin:
            return
        
        defaults = self.current_config.get('defaults', {})
        
        # STEP 1: Apply field overrides FIRST (highest priority)
        data_type = None
        field_override = self.current_plugin.get_field_override(column_name)
        if field_override:
            data_type = field_override
            print(f"  [FIELD OVERRIDE] {column_name} -> {data_type}")
        
        # STEP 2: If no override, determine data type from element
        if not data_type:
            data_type = self._determine_data_type_from_element(element, defaults)
        
        # STEP 3: Enhanced choice detection
        is_choice = self.is_choice_element(element)
        
        # Choice elements are never required (mutually exclusive)
        if is_choice:
            is_required = False
            choice_siblings = self.get_choice_siblings(element)
            print(f"  [CHOICE] Column {column_name} (siblings: {choice_siblings})")
        else:
            is_required = element.get("minOccurs") != "0"
        
        # STEP 4: Ensure valid data type
        if data_type == "VARCHAR(0)":
            data_type = f"VARCHAR({defaults.get('string_size', 255)})"
        
        # STEP 5: Create and add column
        column = Column(
            name=column_name,
            data_type=data_type,
            is_required=is_required,
            max_length=self._extract_max_length(data_type),
            is_choice_element=is_choice
        )
        
        self.tables[table_name].columns.append(column)
        
        # STEP 6: Log the addition
        requirement_status = "NOT NULL" if is_required else "NULL"
        choice_status = " [CHOICE]" if is_choice else ""
        print(f"  Added column: {column_name} {data_type} {requirement_status}{choice_status}")
    
    def _extract_max_length(self, data_type: str) -> Optional[int]:
        """Extract max length from data type string."""
        match = re.search(r'\((\d+)\)', data_type)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return None
        
    def _determine_data_type_from_element(self, element: ET.Element, defaults: Dict[str, Any]) -> str:
        """Determine the appropriate data type from XSD element."""
        data_type = f"VARCHAR({defaults.get('string_size', 255)})"
        element_type = element.get("type")
        
        # Try plugin-specific type mapping first
        if self.current_plugin and element_type:
            custom_type = self.current_plugin.get_custom_type_mapping(element_type)
            if custom_type:
                return custom_type
        
        # Type-based inference
        if element_type:
            if "TDec" in element_type:
                return f"NUMERIC({defaults.get('numeric_precision', 15)},{defaults.get('numeric_scale', 2)})"
            elif "TString" in element_type or "xs:string" in element_type:
                return f"VARCHAR({defaults.get('string_size', 255)})"
            elif "integer" in element_type.lower():
                return "INTEGER"
            elif "date" in element_type.lower():
                return "DATE"
            elif "timestamp" in element_type.lower() or "datetime" in element_type.lower():
                return "TIMESTAMP"
        
        # Check for simpleType definition for more precise typing
        xsd_ns = self.current_config.get('xsd_namespace', 'http://www.w3.org/2001/XMLSchema')
        simple_type = element.find(f".//{{{xsd_ns}}}simpleType")
        if simple_type is not None:
            simple_type_info, _, _ = self.extract_simple_type_info(simple_type)
            if simple_type_info and simple_type_info != "VARCHAR(255)":
                return simple_type_info
        
        return data_type

    def add_column_to_table_from_definition(self, table_name: str, field_def: Dict[str, Any]) -> None:
        """Add a column to table from field definition with proper positioning."""
        if table_name not in self.tables:
            return
        
        # Create the column
        column = Column(
            name=field_def['name'],
            data_type=field_def['type'],
            is_required=field_def.get('required', False),
            is_choice_element=False
        )
        
        table = self.tables[table_name]
        
        # Insert at the correct position (after ID and FKs, before regular columns)
        insert_position = self._calculate_essential_field_position(table)
        table.columns.insert(insert_position, column)

    def _calculate_essential_field_position(self, table: Table) -> int:
        """Calculate the optimal position for essential fields."""
        # Start after ID column (position 1)
        position = 1
        
        # Find the last foreign key column
        for i, column in enumerate(table.columns[1:], start=1):
            if column.is_foreign_key:
                position = i + 1
            else:
                # Stop at first non-FK, non-ID column
                break
        
        return position
    
    def process_complex_type(self, complex_type: ET.Element, table_name: str) -> None:
        """Process complexType element and its children"""
        xsd_ns = self.current_config.get('xsd_namespace', 'http://www.w3.org/2001/XMLSchema')
        
        # Process sequence
        sequence = complex_type.find(f".//{{{xsd_ns}}}sequence")
        if sequence is not None:
            for child in sequence:
                if child.tag.endswith('element'):
                    self.process_element(child, table_name)
        
        # Process choice
        choice = complex_type.find(f".//{{{xsd_ns}}}choice")
        if choice is not None:
            choice_elements = []
            for child in choice:
                if child.tag.endswith('element'):
                    choice_elements.append(child.get('name'))
                    self.process_element(child, table_name)
            
            # Store choice group information
            if choice_elements:
                self.choice_groups[table_name] = choice_elements
        
        # Process simple content
        simple_content = complex_type.find(f".//{{{xsd_ns}}}simpleContent")
        if simple_content is not None:
            extension = simple_content.find(f".//{{{xsd_ns}}}extension")
            if extension is not None:
                base_type = extension.get("base", f"VARCHAR({self.current_config.get('defaults', {}).get('string_size', 255)})")
                data_type = self.current_plugin.get_custom_type_mapping(base_type) if self.current_plugin else f"VARCHAR(255)"
                column = Column("value", data_type, True)
                self.tables[table_name].columns.append(column)
    
    def generate_sql_ddl(self) -> str:
        """Generate SQL DDL statements with validation of foreign key constraints."""
        sql_script = f"-- SQL DDL from XSD Schema (Domain: {self.current_config.get('domain', 'unknown')})\n"
        sql_script += f"-- Generated with generalized XSD to SQL converter\n"
        sql_script += f"-- Fixed version: Proper field overrides and FK validation\n\n"
        
        # Identify tables that should be created
        created_tables = self._get_tables_to_create()
        
        # Create tables
        for table_name, table in self.tables.items():
            if table_name in created_tables:
                sql_script += self.generate_table_ddl(table)
        
        # Add foreign key constraints only for valid tables
        sql_script += self._generate_valid_foreign_key_constraints(created_tables)
        
        # Add comments for choice groups
        sql_script += self.generate_choice_comments()
        
        return sql_script
    
    def _get_tables_to_create(self) -> Set[str]:
        """Get set of table names that should be created."""
        tables_to_create = set()
        
        # Identify referenced tables (for FK constraints)
        referenced_tables = set()
        for table in self.tables.values():
            for column in table.columns:
                if column.is_foreign_key and column.references:
                    referenced_tables.add(column.references)
        
        # Determine which tables to create
        for table_name, table in self.tables.items():
            meaningful_columns = [col for col in table.columns 
                                if not (col.is_primary_key or col.is_foreign_key)]
            
            # Create table if it has meaningful columns OR is referenced by other tables
            if meaningful_columns or table_name in referenced_tables:
                tables_to_create.add(table_name)
            else:
                print(f"  [SKIP] Table {table.name} has no meaningful columns and is not referenced")
        
        return tables_to_create

    def _generate_valid_foreign_key_constraints(self, valid_tables: Set[str]) -> str:
        """Generate only valid foreign key constraints."""
        sql = "\n-- Foreign Key Constraints (Validated)\n"
        
        constraint_count = 0
        for table_name, table in self.tables.items():
            if table_name not in valid_tables:
                continue
                
            for column in table.columns:
                if (column.is_foreign_key and column.references and 
                    column.references in valid_tables):
                    
                    # Verify the referenced table has meaningful content
                    referenced_table = self.tables[column.references]
                    has_meaningful_columns = any(
                        col for col in referenced_table.columns 
                        if not (col.is_primary_key or col.is_foreign_key)
                    )
                    
                    if has_meaningful_columns:
                        sql += self.generate_foreign_key_constraint(table, column)
                        constraint_count += 1
        
        if constraint_count == 0:
            sql += "-- No valid foreign key constraints generated\n"
        else:
            sql += f"-- Generated {constraint_count} valid foreign key constraints\n"
        
        return sql
        
    def generate_table_ddl(self, table: Table) -> str:
        """Generate CREATE TABLE statement for a table"""
        sql = f"CREATE TABLE {table.name} (\n"
        
        column_definitions = []
        for column in table.columns:
            col_def = f"    {column.name} {column.data_type}"
            if column.is_required and not column.is_choice_element:
                col_def += " NOT NULL"
            if column.is_primary_key:
                col_def += " PRIMARY KEY"
            column_definitions.append(col_def)
        
        sql += ",\n".join(column_definitions)
        sql += "\n);\n\n"
        
        return sql
    
    def generate_foreign_key_constraint(self, table: Table, column: Column) -> str:
        """Generate ALTER TABLE ADD CONSTRAINT for foreign key"""
        return f"ALTER TABLE {table.name} ADD CONSTRAINT fk_{table.name}_{column.name} FOREIGN KEY ({column.name}) REFERENCES {column.references}(id);\n"
    
    def generate_choice_comments(self) -> str:
        """Generate comments explaining choice groups"""
        if not self.choice_groups:
            return ""
        
        comments = "\n-- Choice Groups (mutually exclusive elements)\n"
        for table_name, choices in self.choice_groups.items():
            if table_name in self.tables:
                comments += f"-- Table {table_name}: Only one of {choices} should be populated\n"
        
        return comments
    
    def convert(self, main_xsd_file: str, type_xsd_files: List[str] = None, domain: str = None) -> str:
        """
        Main conversion method
        """
        print("Starting Generalized XSD to SQL conversion...")
        
        # Reset state for new conversion
        self.tables.clear()
        self.processed_elements.clear()
        self.parent_map.clear()
        self.current_path.clear()
        self.choice_groups.clear()
        
        # Parse main XSD file
        main_tree = self.parse_xsd_file(main_xsd_file)
        root = main_tree.getroot()
        
        # Detect or use specified domain
        if domain and domain in self.plugins:
            detected_domain = domain
            print(f"Using specified domain: {domain}")
        else:
            detected_domain = self.detect_domain(root)
        
        # Set current plugin and config
        self.current_plugin = self.plugins.get(detected_domain, self.plugins.get('generic'))
        self.current_config = self.current_plugin.config if self.current_plugin else {}
        
        print(f"Active domain: {detected_domain}")
        print(f"Plugin: {self.current_plugin.get_domain_name() if self.current_plugin else 'None'}")
        
        # Parse type definitions first
        if type_xsd_files:
            for type_file in type_xsd_files:
                type_tree = self.parse_xsd_file(type_file)
                # Could add type-specific processing here
        
        # Process main schema
        self.process_schema(root)
        
        # Generate SQL
        sql_ddl = self.generate_sql_ddl()
        
        print(f"Conversion completed. Generated {len(self.tables)} tables.")
        print(f"Processed {len(self.processed_elements)} unique elements.")
        return sql_ddl
    
    def process_schema(self, schema_element: ET.Element) -> None:
        """Process the main schema element"""
        xsd_ns = self.current_config.get('xsd_namespace', 'http://www.w3.org/2001/XMLSchema')
        
        # Method 1: Look for global elements
        elements = schema_element.findall(f'{{{xsd_ns}}}element')
        print(f"Found {len(elements)} global elements")
        
        for element in elements:
            self.process_element(element)
        
        # Method 2: If no elements found, look for complexTypes as root elements
        if not elements:
            complex_types = schema_element.findall(f'{{{xsd_ns}}}complexType')
            print(f"No global elements found. Processing {len(complex_types)} complexTypes as root elements")
            
            root_prefixes = self.current_config.get('root_complex_type_prefixes', ['T'])
            
            for complex_type in complex_types:
                type_name = complex_type.get('name')
                if type_name and any(type_name.startswith(prefix) for prefix in root_prefixes):
                    print(f"Creating root table from complexType: {type_name}")
                    # Create mock element for this complexType
                    mock_element = ET.Element(f'{{{xsd_ns}}}element')
                    mock_element.set('name', type_name)
                    mock_element.append(complex_type)
                    self.process_element(mock_element)


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Generalized XSD to SQL Converter")
        print("Usage: python main.py <main_xsd_file> [<type_xsd_file1> ...] [--domain nfe|generic]")
        print("\nOptions:")
        print("  --domain: Specify domain (nfe, generic). Auto-detected if not specified.")
        sys.exit(1)
    
    main_xsd_file = sys.argv[1]
    type_xsd_files = []
    domain = None
    
    # Parse command line arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--domain" and i + 1 < len(sys.argv):
            domain = sys.argv[i + 1]
            i += 2
        else:
            type_xsd_files.append(sys.argv[i])
            i += 1
    
    # Verify files exist
    if not os.path.exists(main_xsd_file):
        print(f"Error: Main XSD file '{main_xsd_file}' not found")
        sys.exit(1)
    
    for type_file in type_xsd_files:
        if not os.path.exists(type_file):
            print(f"Error: Type XSD file '{type_file}' not found")
            sys.exit(1)
    
    print("Generalized XSD to SQL Converter")
    print("=================================")
    print(f"Main XSD: {main_xsd_file}")
    if type_xsd_files:
        print(f"Type XSDs: {', '.join(type_xsd_files)}")
    if domain:
        print(f"Domain: {domain} (specified)")
    else:
        print(f"Domain: auto-detection")
    print()
    
    try:
        converter = GeneralizedXSDToSQLConverter()
        
        # Perform conversion
        sql_ddl = converter.convert(main_xsd_file, type_xsd_files, domain)
        
        # Generate output filename
        base_name = os.path.splitext(main_xsd_file)[0]
        output_file = f"{base_name}_schema_generalized.sql"
        
        # Write SQL to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql_ddl)
        
        print(f"✓ Conversion completed successfully!")
        print(f"✓ Generated {len(converter.tables)} tables")
        print(f"✓ Active domain: {converter.current_config.get('domain', 'unknown')}")
        print(f"✓ SQL schema written to: {output_file}")
        
        # Show table summary
        print(f"\nGenerated Tables:")
        created_tables = [name for name, table in converter.tables.items() 
                         if any(col for col in table.columns 
                               if not (col.is_primary_key or col.is_foreign_key)) or
                         name in [t for t in converter.tables.keys() 
                                 if any(col.is_foreign_key and col.references == name 
                                       for table in converter.tables.values() 
                                       for col in table.columns)]]
        
        for table_name in sorted(created_tables):
            table = converter.tables[table_name]
            meaningful_columns = len([col for col in table.columns 
                                   if not (col.is_primary_key or col.is_foreign_key)])
            choice_columns = sum(1 for col in table.columns if col.is_choice_element)
            print(f"  - {table_name} ({meaningful_columns} meaningful columns, {choice_columns} choice columns)")
            
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()