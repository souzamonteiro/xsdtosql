#!/usr/bin/env python3
"""
XSD to SQL Database Schema Converter - Practical Version
Converts XML Schema Definition (XSD) files to SQL DDL scripts
Usage: python xsd_to_sql.py <main_xsd_file> [<type_xsd_file1> ...]
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

@dataclass
class Table:
    """Represents a database table"""
    name: str
    columns: List[Column]
    primary_key: str = "id"
    parent_table: Optional[str] = None

class XSDToSQLConverter:
    """
    Converts XSD schema files to SQL DDL statements
    """
    
    def __init__(self):
        # XSD to SQL type mapping
        self.type_mapping = {
            # String types
            'TString': 'VARCHAR',
            'xs:string': 'VARCHAR',
            'TGuid': 'UUID',
            
            # Numeric types
            'TCodUfIBGE': 'CHAR(2)',
            'TCodMunIBGE': 'CHAR(7)',
            'TCnpj': 'CHAR(14)',
            'TCpf': 'CHAR(11)',
            'TNF': 'INTEGER',
            'TSerie': 'INTEGER',
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
            
            # Special types
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
        
    def parse_xsd_file(self, file_path: str) -> ET.ElementTree:
        """Parse XSD file and return ElementTree"""
        try:
            tree = ET.parse(file_path)
            return tree
        except ET.ParseError as e:
            print(f"Error parsing XSD file {file_path}: {e}")
            raise
    
    def extract_simple_type_info(self, simple_type_element: ET.Element) -> Tuple[str, Optional[int]]:
        """
        Extract data type and max length from simpleType element
        """
        data_type = "VARCHAR"
        max_length = None
        
        # Check for restrictions
        restriction = simple_type_element.find(".//{http://www.w3.org/2001/XMLSchema}restriction")
        if restriction is not None:
            base_type = restriction.get("base", "")
            
            # Map base type to SQL
            if base_type in self.type_mapping:
                data_type = self.type_mapping[base_type]
            elif "string" in base_type:
                data_type = "VARCHAR"
            elif "decimal" in base_type or "TDec" in base_type:
                data_type = "NUMERIC(15,2)"  # Default decimal
            
            # Extract maxLength
            max_length_elem = restriction.find(".//{http://www.w3.org/2001/XMLSchema}maxLength")
            if max_length_elem is not None:
                try:
                    max_length = int(max_length_elem.get("value", "255"))
                except ValueError:
                    max_length = 255
            
            # Extract length from pattern
            pattern_elem = restriction.find(".//{http://www.w3.org/2001/XMLSchema}pattern")
            if pattern_elem is not None and max_length is None:
                pattern = pattern_elem.get("value", "")
                # Try to extract length from pattern like [0-9]{n}
                length_match = re.search(r'\{(\d+)\}', pattern)
                if length_match:
                    try:
                        max_length = int(length_match.group(1))
                    except ValueError:
                        pass
        
        return data_type, max_length
    
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
        if max_occurs and (max_occurs == "unbounded" or int(max_occurs) > 1):
            return True
        
        return False
    
    def process_element(self, element: ET.Element, parent_table: str = None) -> None:
        """Process an XSD element and create corresponding table/column"""
        element_name = element.get("name")
        if not element_name:
            return
        
        self.current_path.append(element_name)
        
        if self.is_complex_element(element):
            # Create new table for complex element
            self.create_table_from_complex_element(element, element_name, parent_table)
        else:
            # Add column to parent table
            self.add_column_to_table(element, element_name, parent_table)
        
        self.current_path.pop()
    
    def create_table_from_complex_element(self, element: ET.Element, table_name: str, parent_table: str = None) -> None:
        """Create a new table from complex XSD element"""
        print(f"Creating table: {table_name} (parent: {parent_table})")
        
        # Initialize table with ID column
        columns = [Column("id", "SERIAL", True, is_primary_key=True)]
        
        # Add foreign key to parent table if exists
        if parent_table:
            fk_column = Column(f"{parent_table.lower()}_id", "INTEGER", True, is_foreign_key=True, references=parent_table)
            columns.append(fk_column)
        
        table = Table(name=table_name, columns=columns, parent_table=parent_table)
        self.tables[table_name] = table
        
        # Process child elements
        complex_type = element.find(".//{http://www.w3.org/2001/XMLSchema}complexType")
        if complex_type is not None:
            self.process_complex_type(complex_type, table_name)
    
    def add_column_to_table(self, element: ET.Element, column_name: str, table_name: str) -> None:
        """Add a column to an existing table"""
        if table_name not in self.tables:
            print(f"Warning: Table {table_name} not found for column {column_name}")
            return
        
        data_type = "VARCHAR"
        max_length = 255
        is_required = element.get("minOccurs") != "0"
        
        # Get type information
        element_type = element.get("type")
        if element_type:
            if element_type in self.type_mapping:
                data_type = self.type_mapping[element_type]
            elif "TDec" in element_type:
                data_type = "NUMERIC(15,2)"
            elif "TString" in element_type or "xs:string" in element_type:
                data_type = "VARCHAR"
        
        # Check for simpleType definition
        simple_type = element.find(".//{http://www.w3.org/2001/XMLSchema}simpleType")
        if simple_type is not None:
            data_type, max_length = self.extract_simple_type_info(simple_type)
        
        # Adjust VARCHAR with max length
        if data_type == "VARCHAR" and max_length:
            data_type = f"VARCHAR({max_length})"
        
        column = Column(
            name=column_name,
            data_type=data_type,
            is_required=is_required,
            max_length=max_length
        )
        
        self.tables[table_name].columns.append(column)
        print(f"  Added column: {column_name} {data_type} {'NOT NULL' if is_required else 'NULL'}")
    
    def process_complex_type(self, complex_type: ET.Element, table_name: str) -> None:
        """Process complexType element and its children"""
        # Process sequence
        sequence = complex_type.find(".//{http://www.w3.org/2001/XMLSchema}sequence")
        if sequence is not None:
            for child in sequence:
                self.process_element(child, table_name)
        
        # Process choice
        choice = complex_type.find(".//{http://www.w3.org/2001/XMLSchema}choice")
        if choice is not None:
            for child in choice:
                self.process_element(child, table_name)
        
        # Process simple content
        simple_content = complex_type.find(".//{http://www.w3.org/2001/XMLSchema}simpleContent")
        if simple_content is not None:
            extension = simple_content.find(".//{http://www.w3.org/2001/XMLSchema}extension")
            if extension is not None:
                base_type = extension.get("base", "VARCHAR")
                data_type = self.type_mapping.get(base_type, "VARCHAR")
                column = Column("value", data_type, True)
                self.tables[table_name].columns.append(column)
    
    def generate_sql_ddl(self) -> str:
        """Generate SQL DDL statements from parsed tables"""
        sql_script = "-- Generated SQL DDL from XSD Schema\n\n"
        
        # Create tables
        for table_name, table in self.tables.items():
            sql_script += self.generate_table_ddl(table)
        
        # Add foreign key constraints
        sql_script += "\n-- Foreign Key Constraints\n"
        for table_name, table in self.tables.items():
            for column in table.columns:
                if column.is_foreign_key and column.references:
                    sql_script += self.generate_foreign_key_constraint(table, column)
        
        return sql_script
    
    def generate_table_ddl(self, table: Table) -> str:
        """Generate CREATE TABLE statement for a table"""
        sql = f"CREATE TABLE {table.name} (\n"
        
        column_definitions = []
        for column in table.columns:
            col_def = f"    {column.name} {column.data_type}"
            if column.is_required:
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
    
    def convert(self, main_xsd_file: str, type_xsd_files: List[str] = None) -> str:
        """
        Main conversion method
        """
        print("Starting XSD to SQL conversion...")
        
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
                if type_name and type_name.startswith('T'):  # Typically root types start with T
                    print(f"Creating root table from complexType: {type_name}")
                    # Create mock element for this complexType
                    mock_element = ET.Element('xs:element')
                    mock_element.set('name', type_name)
                    mock_element.append(complex_type)
                    self.process_element(mock_element)

# Test function to verify the converter
def test_converter():
    """Test the XSD to SQL converter with sample data"""
    converter = XSDToSQLConverter()
    
    # Test with a mock XSD structure (simulating the NFe structure)
    test_xsd = '''
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
        <xs:element name="TNFe">
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="infNFe">
                        <xs:complexType>
                            <xs:sequence>
                                <xs:element name="ide">
                                    <xs:complexType>
                                        <xs:sequence>
                                            <xs:element name="cUF" type="TCodUfIBGE"/>
                                            <xs:element name="cNF" type="xs:string"/>
                                            <xs:element name="natOp" type="TString"/>
                                            <xs:element name="mod" type="TMod"/>
                                        </xs:sequence>
                                    </xs:complexType>
                                </xs:element>
                                <xs:element name="emit">
                                    <xs:complexType>
                                        <xs:sequence>
                                            <xs:choice>
                                                <xs:element name="CNPJ" type="TCnpj"/>
                                                <xs:element name="CPF" type="TCpf"/>
                                            </xs:choice>
                                            <xs:element name="xNome" type="TString"/>
                                        </xs:sequence>
                                    </xs:complexType>
                                </xs:element>
                                <xs:element name="det" maxOccurs="990">
                                    <xs:complexType>
                                        <xs:sequence>
                                            <xs:element name="prod">
                                                <xs:complexType>
                                                    <xs:sequence>
                                                        <xs:element name="cProd" type="TString"/>
                                                        <xs:element name="cEAN" type="xs:string"/>
                                                        <xs:element name="xProd" type="TString"/>
                                                        <xs:element name="NCM" type="xs:string"/>
                                                    </xs:sequence>
                                                </xs:complexType>
                                            </xs:element>
                                        </xs:sequence>
                                        <xs:attribute name="nItem" type="xs:string" use="required"/>
                                    </xs:complexType>
                                </xs:element>
                            </xs:sequence>
                        </xs:complexType>
                    </xs:element>
                </xs:sequence>
            </xs:complexType>
        </xs:element>
    </xs:schema>
    '''
    
    # Write test XSD to file
    with open('test_schema.xsd', 'w', encoding='utf-8') as f:
        f.write(test_xsd)
    
    # Convert test schema
    try:
        sql_result = converter.convert('test_schema.xsd')
        print("=== GENERATED SQL DDL ===")
        print(sql_result)
        
        # Verify results
        expected_tables = ['TNFe', 'infNFe', 'ide', 'emit', 'det', 'prod']
        generated_tables = list(converter.tables.keys())
        
        print(f"\n=== VERIFICATION ===")
        print(f"Expected tables: {expected_tables}")
        print(f"Generated tables: {generated_tables}")
        
        missing_tables = set(expected_tables) - set(generated_tables)
        if missing_tables:
            print(f"WARNING: Missing tables: {missing_tables}")
        else:
            print("✓ All expected tables were created")
        
        # Check column counts
        for table_name, table in converter.tables.items():
            print(f"Table {table_name}: {len(table.columns)} columns")
            for col in table.columns:
                print(f"  - {col.name} {col.data_type}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python xsd_to_sql.py <main_xsd_file> [<type_xsd_file1> ...]")
        print("\nExamples:")
        print("  python xsd_to_sql.py leiauteNFe_v4.00.xsd")
        print("  python xsd_to_sql.py leiauteNFe_v4.00.xsd tiposBasico_v4.00.xsd xmldsig-core-schema_v1.01.xsd")
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
    
    print("XSD to SQL Converter - Practical Version")
    print("========================================")
    print(f"Main XSD: {main_xsd_file}")
    if type_xsd_files:
        print(f"Type XSDs: {', '.join(type_xsd_files)}")
    print()
    
    try:
        converter = XSDToSQLConverter()
        
        # Perform conversion
        sql_ddl = converter.convert(main_xsd_file, type_xsd_files)
        
        # Generate output filename
        base_name = os.path.splitext(main_xsd_file)[0]
        output_file = f"{base_name}_schema.sql"
        
        # Write SQL to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql_ddl)
        
        print(f"✓ Conversion completed successfully!")
        print(f"✓ Generated {len(converter.tables)} tables")
        print(f"✓ SQL schema written to: {output_file}")
        
        # Show table summary
        print(f"\nGenerated Tables:")
        for table_name in sorted(converter.tables.keys()):
            table = converter.tables[table_name]
            print(f"  - {table_name} ({len(table.columns)} columns)")
            
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def interactive_mode():
    """Interactive mode for user-friendly operation"""
    print("\nInteractive Mode")
    print("================")
    
    main_xsd = input("Enter main XSD file path: ").strip()
    if not os.path.exists(main_xsd):
        print("File not found!")
        return
    
    type_files = []
    print("\nEnter additional type XSD files (press Enter to skip):")
    while True:
        file_path = input("Type XSD file: ").strip()
        if not file_path:
            break
        if os.path.exists(file_path):
            type_files.append(file_path)
        else:
            print("File not found! Skipping...")
    
    # Use the same conversion logic as main()
    converter = XSDToSQLConverter()
    sql_ddl = converter.convert(main_xsd, type_files)
    
    output_file = input("\nOutput SQL file [auto-generate]: ").strip()
    if not output_file:
        base_name = os.path.splitext(main_xsd)[0]
        output_file = f"{base_name}_schema.sql"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_ddl)
    
    print(f"\n✓ Conversion completed!")
    print(f"✓ Output: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - offer interactive mode
        response = input("No files specified. Use interactive mode? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_mode()
        else:
            print("Usage: python xsd_to_sql.py <main_xsd_file> [<type_xsd_file1> ...]")
    else:
        # Command line mode
        main()
