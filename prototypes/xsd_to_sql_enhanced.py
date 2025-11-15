#!/usr/bin/env python3
"""
Enhanced XSD to SQL Database Schema Converter - CORRIGIDO
Correções para problemas críticos identificados
"""

import xml.etree.ElementTree as ET
import re
import sys
import os
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

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

class EnhancedXSDToSQLConverter:
    """
    Enhanced converter with improved type mapping and choice detection
    """
    
    def __init__(self):
        # Enhanced type mapping with better precision
        self.type_mapping = {
            # String types
            'TString': 'VARCHAR(255)',
            'xs:string': 'VARCHAR(255)',
            'TGuid': 'UUID',
            
            # Numeric types
            'TCodUfIBGE': 'CHAR(2)',
            'TCodMunIBGE': 'CHAR(7)',
            'TCnpj': 'CHAR(14)',
            'TCpf': 'CHAR(11)',
            'TNF': 'INTEGER',
            'TSerie': 'SMALLINT',
            'TProt': 'CHAR(15)',
            'TRec': 'CHAR(15)',
            'TStat': 'CHAR(3)',
            
            # Decimal types
            'TDec_1302': 'NUMERIC(15,2)',
            'TDec_1302Opc': 'NUMERIC(15,2)',
            'TDec_0302a04': 'NUMERIC(5,4)',
            'TDec_0302a04Opc': 'NUMERIC(5,4)',
            'TDec_0302Max100': 'NUMERIC(5,2)',
            'TDec_0302a04Max100': 'NUMERIC(5,4)',
            'TDec_0803v': 'NUMERIC(11,3)',
            'TDec_1104': 'NUMERIC(15,4)',
            'TDec_1104v': 'NUMERIC(15,4)',
            'TDec_1110v': 'NUMERIC(21,10)',
            'TDec_1203': 'NUMERIC(15,3)',
            'TDec_1204': 'NUMERIC(16,4)',
            'TDec_1204v': 'NUMERIC(16,4)',
            'TDec_1204temperatura': 'NUMERIC(16,4)',
            
            # Date/Time types
            'TData': 'DATE',
            'TDateTimeUTC': 'TIMESTAMP',
            'TTime': 'TIME',
            
            # Special types with improved mapping
            'TChNFe': 'CHAR(44)',
            'TIe': 'VARCHAR(14)',
            'TIeDest': 'VARCHAR(14)',
            'TIeST': 'VARCHAR(14)',
            'TMod': 'CHAR(2)',
            'TPlaca': 'VARCHAR(7)',
            'TUf': 'CHAR(2)',
            'TUfEmi': 'CHAR(2)',
            'TAmb': 'CHAR(1)',
        }
        
        self.tables: Dict[str, Table] = {}
        self.current_path: List[str] = []
        self.complex_types: Set[str] = set()
        self.processed_elements: Set[str] = set()
        self.parent_map: Dict[ET.Element, ET.Element] = {}
        self.choice_groups: Dict[str, List[str]] = {}
        self.required_tables: Set[str] = set()  # Tabelas que devem ser criadas mesmo sem colunas
        
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
        parent = self.get_parent(element)
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
        data_type = "VARCHAR(255)"
        max_length = 255
        patterns = []
        
        restriction = simple_type_element.find(".//{http://www.w3.org/2001/XMLSchema}restriction")
        if restriction is not None:
            base_type = restriction.get("base", "")
            
            # Map base type to SQL
            if base_type in self.type_mapping:
                data_type = self.type_mapping[base_type]
            elif "string" in base_type:
                data_type = "VARCHAR(255)"
            elif "decimal" in base_type or "TDec" in base_type:
                data_type = "NUMERIC(15,2)"
            
            # Extract maxLength
            max_length_elem = restriction.find(".//{http://www.w3.org/2001/XMLSchema}maxLength")
            if max_length_elem is not None:
                try:
                    max_length = int(max_length_elem.get("value", "255"))
                    if data_type.startswith("VARCHAR"):
                        data_type = f"VARCHAR({max_length})"
                except ValueError:
                    pass
            
            # Extract patterns for enhanced type detection
            pattern_elems = restriction.findall(".//{http://www.w3.org/2001/XMLSchema}pattern")
            for pattern_elem in pattern_elems:
                pattern = pattern_elem.get("value", "")
                patterns.append(pattern)
                
                # Use pattern-based mapping for common patterns
                if re.search(r'\[0-9\]\{4\}', pattern):
                    data_type = 'CHAR(4)'
                elif re.search(r'\[0-9\]\{8\}', pattern):
                    data_type = 'VARCHAR(8)'
                elif re.search(r'\[0-9\]\{7\}', pattern):
                    data_type = 'CHAR(7)'
                elif re.search(r'\[0-9\]\{14\}', pattern):
                    data_type = 'CHAR(14)'
                elif re.search(r'\[0-9\]\{11\}', pattern):
                    data_type = 'CHAR(11)'
            
            # Extract length from pattern if max_length not set
            if max_length == 255 and patterns:
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
        
        # Garantir que nunca tenha VARCHAR(0)
        if data_type == "VARCHAR(0)":
            data_type = "VARCHAR(255)"
        
        return data_type, max_length, patterns
    
    def is_complex_element(self, element: ET.Element) -> bool:
        """Check if element is complex (should become a table)"""
        # Elements with complexType or containing other elements are complex
        if element.find(".//{http://www.w3.org/2001/XMLSchema}complexType") is not None:
            return True
        
        # Elements with sequence, choice, or multiple occurrences
        if (element.find(".//{http://www.w3.org/2001/XMLSchema}sequence") is not None or
            element.find(".//{http://www.w3.org/2001/XMLSchema}choice") is not None):
            return True
        
        # Elements that can occur multiple times
        max_occurs = element.get("maxOccurs")
        if max_occurs and (max_occurs == "unbounded" or max_occurs.isdigit() and int(max_occurs) > 1):
            return True
        
        return False
    
    def get_element_context(self, element: ET.Element, current_path: List[str]) -> str:
        """Get context path for element to avoid duplicates"""
        return '_'.join(current_path)
    
    def should_create_table_for_element(self, element: ET.Element) -> bool:
        """Determine if we should create a table for this element"""
        element_name = element.get("name", "")
        
        # Skip very simple elements that should be columns
        if not self.is_complex_element(element):
            return False
            
        # Always create tables for known complex structures
        complex_indicators = [
            element.find(".//{http://www.w3.org/2001/XMLSchema}sequence"),
            element.find(".//{http://www.w3.org/2001/XMLSchema}choice"),
            element.find(".//{http://www.w3.org/2001/XMLSchema}complexType")
        ]
        
        return any(indicator is not None for indicator in complex_indicators)
    
    def add_essential_columns(self, table_name: str, element: ET.Element):
        """Add essential columns like CNPJ/CPF to key tables"""
        table = self.tables.get(table_name)
        if not table:
            return
            
        # Adicionar campos CNPJ/CPF para tabelas que precisam
        if table_name in ["emit", "dest", "autXML", "transporta"]:
            # Verificar se já existem esses campos
            existing_columns = {col.name for col in table.columns}
            
            if "CNPJ" not in existing_columns:
                table.columns.append(Column("CNPJ", "CHAR(14)", False))
                print(f"  [ADDED] Essential column CNPJ to {table_name}")
            
            if "CPF" not in existing_columns:
                table.columns.append(Column("CPF", "CHAR(11)", False))
                print(f"  [ADDED] Essential column CPF to {table_name}")
        
        # Para tabela dest, adicionar idEstrangeiro se não existir
        if table_name == "dest" and "idEstrangeiro" not in {col.name for col in table.columns}:
            table.columns.append(Column("idEstrangeiro", "VARCHAR(20)", False))
            print(f"  [ADDED] Essential column idEstrangeiro to {table_name}")
    
    def process_element(self, element: ET.Element, parent_table: str = None, current_path: List[str] = None) -> None:
        """Process an XSD element and create corresponding table/column"""
        if current_path is None:
            current_path = []
            
        element_name = element.get("name")
        if not element_name:
            return
        
        # Create unique identifier for this element in its context
        element_context = self.get_element_context(element, current_path)
        element_id = f"{element_name}|{element_context}"
        
        # Avoid processing the same element multiple times in different contexts
        if element_id in self.processed_elements:
            return
        
        self.processed_elements.add(element_id)
        current_path.append(element_name)
        
        if self.should_create_table_for_element(element):
            self.create_table_from_complex_element(element, element_name, parent_table, element_context)
        else:
            self.add_column_to_table(element, element_name, parent_table)
        
        current_path.pop()
    
    def create_table_from_complex_element(self, element: ET.Element, table_name: str, 
                                        parent_table: str = None, context: str = "") -> None:
        """Create a new table from complex XSD element with context awareness"""
        
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
        complex_type = element.find(".//{http://www.w3.org/2001/XMLSchema}complexType")
        if complex_type is not None:
            self.process_complex_type(complex_type, final_table_name)
        else:
            # Process direct children for elements without explicit complexType
            self.process_element_children(element, final_table_name)
        
        # Add essential columns após processar todos os elementos filhos
        self.add_essential_columns(final_table_name, element)
    
    def process_element_children(self, element: ET.Element, table_name: str) -> None:
        """Process direct children of an element"""
        # Process sequence
        sequence = element.find(".//{http://www.w3.org/2001/XMLSchema}sequence")
        if sequence is not None:
            for child in sequence:
                if child.tag.endswith('element'):
                    self.process_element(child, table_name)
        
        # Process choice
        choice = element.find(".//{http://www.w3.org/2001/XMLSchema}choice")
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
        """Add a column to an existing table with enhanced type detection"""
        if table_name not in self.tables:
            print(f"Warning: Table {table_name} not found for column {column_name}")
            return
        
        data_type = "VARCHAR(255)"
        max_length = 255
        patterns = []
        
        # Enhanced choice detection
        is_choice = self.is_choice_element(element)
        
        # Choice elements are never required (mutually exclusive)
        if is_choice:
            is_required = False
            choice_siblings = self.get_choice_siblings(element)
            print(f"  [CHOICE] Column {column_name} (siblings: {choice_siblings})")
        else:
            is_required = element.get("minOccurs") != "0"
        
        # Get type information
        element_type = element.get("type")
        if element_type:
            if element_type in self.type_mapping:
                data_type = self.type_mapping[element_type]
            elif "TDec" in element_type:
                data_type = "NUMERIC(15,2)"
            elif "TString" in element_type or "xs:string" in element_type:
                data_type = "VARCHAR(255)"
        
        # Check for simpleType definition
        simple_type = element.find(".//{http://www.w3.org/2001/XMLSchema}simpleType")
        if simple_type is not None:
            data_type, max_length, patterns = self.extract_simple_type_info(simple_type)
        
        # Special case handling for known field types
        if column_name == "CFOP":
            data_type = "CHAR(4)"
        elif column_name == "NCM":
            data_type = "VARCHAR(8)"
        elif column_name in ["cEAN", "cEANTrib"]:
            data_type = "VARCHAR(14)"  # Código EAN padrão
        elif column_name == "idEstrangeiro":
            data_type = "VARCHAR(20)"
        
        # Garantir que nunca tenha VARCHAR(0)
        if data_type == "VARCHAR(0)":
            data_type = "VARCHAR(255)"
        
        column = Column(
            name=column_name,
            data_type=data_type,
            is_required=is_required,
            max_length=max_length,
            is_choice_element=is_choice
        )
        
        self.tables[table_name].columns.append(column)
        
        requirement_status = "NOT NULL" if is_required else "NULL"
        choice_status = " [CHOICE]" if is_choice else ""
        print(f"  Added column: {column_name} {data_type} {requirement_status}{choice_status}")
    
    def process_complex_type(self, complex_type: ET.Element, table_name: str) -> None:
        """Process complexType element and its children"""
        # Process sequence
        sequence = complex_type.find(".//{http://www.w3.org/2001/XMLSchema}sequence")
        if sequence is not None:
            for child in sequence:
                if child.tag.endswith('element'):
                    self.process_element(child, table_name)
        
        # Process choice
        choice = complex_type.find(".//{http://www.w3.org/2001/XMLSchema}choice")
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
        simple_content = complex_type.find(".//{http://www.w3.org/2001/XMLSchema}simpleContent")
        if simple_content is not None:
            extension = simple_content.find(".//{http://www.w3.org/2001/XMLSchema}extension")
            if extension is not None:
                base_type = extension.get("base", "VARCHAR(255)")
                data_type = self.type_mapping.get(base_type, "VARCHAR(255)")
                column = Column("value", data_type, True)
                self.tables[table_name].columns.append(column)
        
        # Process complex content
        complex_content = complex_type.find(".//{http://www.w3.org/2001/XMLSchema}complexContent")
        if complex_content is not None:
            extension = complex_content.find(".//{http://www.w3.org/2001/XMLSchema}extension")
            if extension is not None:
                # Process extension base attributes
                for child in extension:
                    if child.tag.endswith('element'):
                        self.process_element(child, table_name)
    
    def generate_sql_ddl(self) -> str:
        """Generate SQL DDL statements from parsed tables"""
        sql_script = "-- Enhanced SQL DDL from XSD Schema\n"
        sql_script += "-- Generated with improved type mapping and choice detection\n\n"
        
        # Identificar tabelas que devem ser criadas mesmo sem colunas significativas
        # (tabelas que são referenciadas por outras)
        referenced_tables = set()
        for table in self.tables.values():
            for column in table.columns:
                if column.is_foreign_key and column.references:
                    referenced_tables.add(column.references)
        
        # Create tables
        for table_name, table in self.tables.items():
            # Skip tables with only ID and foreign key (no meaningful columns)
            # exceto se forem referenciadas por outras tabelas
            meaningful_columns = [col for col in table.columns 
                                if not (col.is_primary_key or col.is_foreign_key)]
            
            if not meaningful_columns and table_name not in referenced_tables:
                print(f"  [SKIP] Table {table.name} has no meaningful columns")
                continue
            
            sql_script += self.generate_table_ddl(table)
        
        # Add foreign key constraints apenas para tabelas que existem
        sql_script += "\n-- Foreign Key Constraints\n"
        for table_name, table in self.tables.items():
            for column in table.columns:
                if (column.is_foreign_key and column.references and 
                    column.references in self.tables and
                    any(col for col in self.tables[column.references].columns 
                        if not (col.is_primary_key or col.is_foreign_key))):
                    sql_script += self.generate_foreign_key_constraint(table, column)
        
        # Add comments for choice groups
        sql_script += self.generate_choice_comments()
        
        return sql_script
    
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
    
    def convert(self, main_xsd_file: str, type_xsd_files: List[str] = None) -> str:
        """
        Main conversion method
        """
        print("Starting Enhanced XSD to SQL conversion...")
        print("Features: Choice detection, Improved type mapping, Context awareness")
        
        # Reset state for new conversion
        self.tables.clear()
        self.processed_elements.clear()
        self.parent_map.clear()
        self.current_path.clear()
        self.choice_groups.clear()
        self.required_tables.clear()
        
        # Parse main XSD file
        main_tree = self.parse_xsd_file(main_xsd_file)
        root = main_tree.getroot()
        
        # Parse type definitions first
        if type_xsd_files:
            for type_file in type_xsd_files:
                type_tree = self.parse_xsd_file(type_file)
                self.process_type_definitions(type_tree)
        
        # Process main schema
        self.process_schema(root)
        
        # Generate SQL
        sql_ddl = self.generate_sql_ddl()
        
        print(f"Conversion completed. Generated {len(self.tables)} tables.")
        print(f"Processed {len(self.processed_elements)} unique elements.")
        return sql_ddl
    
    def process_type_definitions(self, type_tree: ET.ElementTree) -> None:
        """Process type definition files"""
        root = type_tree.getroot()
        for elem in root.iter():
            if elem.tag.endswith("simpleType"):
                type_name = elem.get("name")
                if type_name:
                    self.complex_types.add(type_name)
    
    def process_schema(self, schema_element: ET.Element) -> None:
        """Process the main schema element"""
        ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
        
        # Method 1: Look for global elements
        elements = schema_element.findall('xs:element', ns)
        print(f"Found {len(elements)} global elements")
        
        for element in elements:
            self.process_element(element)
        
        # Method 2: If no elements found, look for complexTypes as root elements
        if not elements:
            complex_types = schema_element.findall('xs:complexType', ns)
            print(f"No global elements found. Processing {len(complex_types)} complexTypes as root elements")
            
            for complex_type in complex_types:
                type_name = complex_type.get('name')
                if type_name and type_name.startswith('T'):
                    print(f"Creating root table from complexType: {type_name}")
                    # Create mock element for this complexType
                    mock_element = ET.Element('xs:element')
                    mock_element.set('name', type_name)
                    mock_element.append(complex_type)
                    self.process_element(mock_element)

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Enhanced XSD to SQL Converter")
        print("Usage: python xsd_to_sql_enhanced.py <main_xsd_file> [<type_xsd_file1> ...]")
        sys.exit(1)
    
    main_xsd_file = sys.argv[1]
    type_xsd_files = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Verify files exist
    if not os.path.exists(main_xsd_file):
        print(f"Error: Main XSD file '{main_xsd_file}' not found")
        sys.exit(1)
    
    for type_file in type_xsd_files:
        if not os.path.exists(type_file):
            print(f"Error: Type XSD file '{type_file}' not found")
            sys.exit(1)
    
    print("Enhanced XSD to SQL Converter")
    print("=============================")
    print(f"Main XSD: {main_xsd_file}")
    if type_xsd_files:
        print(f"Type XSDs: {', '.join(type_xsd_files)}")
    print()
    
    try:
        converter = EnhancedXSDToSQLConverter()
        
        # Perform conversion
        sql_ddl = converter.convert(main_xsd_file, type_xsd_files)
        
        # Generate output filename
        base_name = os.path.splitext(main_xsd_file)[0]
        output_file = f"{base_name}_schema_enhanced.sql"
        
        # Write SQL to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql_ddl)
        
        print(f"✓ Enhanced conversion completed successfully!")
        print(f"✓ Generated {len(converter.tables)} tables")
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
