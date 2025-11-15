# XSD to SQL Database Schema Converter

An advanced XSD schema to SQL converter with plugin system and external configuration for multi-domain support.

## 📋 Overview

This program converts XML Schema Definition (XSD) files into SQL DDL (Data Definition Language) scripts for database creation. The tool is particularly useful for:

- **System integration** that uses XSD for data definition
- **Data migration** from XML formats to relational databases
- **Automatic generation** of database schemas from XSD specifications
- **Multi-domain support** with specialized plugins (e.g., NF-e, fiscal documents)

## ✨ Key Features

### 🎯 Plugin System
- **Domain-specific plugins** (NF-e, generic, etc.)
- **Automatic domain detection** based on namespaces and elements
- **External configuration** via YAML files
- **Extensibility** for new domains

### 🔧 Advanced Functionality
- **Intelligent mapping** of XSD types to SQL types
- **Choice group support** (mutually exclusive elements)
- **Foreign key detection** and relationships
- **Constraint validation** and referential integrity
- **Optimized positioning** of essential fields

### 📊 Data Type Support
- **Strings**: VARCHAR with automatic sizing
- **Numbers**: NUMERIC with configurable precision
- **Dates**: DATE, TIMESTAMP
- **Custom patterns** via configuration
- **Regex-based mapping**

## 🚀 Installation

### Prerequisites
- Python 3.7+
- Dependencies: PyYAML

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd xsd-to-sql-converter

# Install dependencies
pip install pyyaml

# Directory structure
mkdir -p config/domains plugins
```

## 📁 Project Structure

```
xsd-to-sql-converter/
├── main.py                 # Main script
├── plugins/               # Plugin directory
│   ├── base_plugin.py    # Base plugin class
│   ├── nfe_plugin.py     # NF-e specific plugin
│   └── generic_plugin.py # Generic plugin
├── config/
│   └── domains/          # Domain configurations
│       ├── nfe.yaml      # NF-e configuration
│       └── generic.yaml  # Generic configuration
└── examples/             # Usage examples
```

## 🛠 Usage

### Command Line
```bash
# Basic conversion with auto-detection
python main.py schema.xsd

# Specifying domain
python main.py schema.xsd --domain nfe

# Multiple XSD files
python main.py main.xsd types1.xsd types2.xsd --domain generic
```

### Parameters
- `<main_xsd_file>`: Main XSD file (required)
- `[type_xsd_files]`: Additional XSD files with type definitions
- `--domain`: Specific domain (nfe, generic). Auto-detected if omitted

### Programmatic Usage Example
```python
from main import GeneralizedXSDToSQLConverter

# Initialize converter
converter = GeneralizedXSDToSQLConverter(config_dir="config/domains")

# Execute conversion
sql_ddl = converter.convert(
    main_xsd_file="my_schema.xsd",
    type_xsd_files=["types.xsd"],
    domain="nfe"  # Optional
)

# Save result
with open("schema.sql", "w") as f:
    f.write(sql_ddl)
```

## 🔌 Plugin System

### Available Plugins

#### NF-e Plugin
Specialized for Brazilian Electronic Invoice schemas:
- Mapping of specific fiscal types (TDec, TString)
- NF-e element handling
- Optimized settings for fiscal documents

#### Generic Plugin
General-purpose plugin for standard XSD schemas:
- Common XSD namespace support
- Basic type mapping
- Configurable via YAML

### Creating a New Plugin

1. **Extend base class**:
```python
from plugins.base_plugin import BaseDomainPlugin

class MyPlugin(BaseDomainPlugin):
    def get_domain_name(self):
        return "my_domain"
    
    def should_create_table(self, element, parent_table):
        # Custom table creation logic
        pass
```

2. **Create YAML configuration** in `config/domains/my_domain.yaml`

3. **Register plugin** in the `_load_plugins()` method

## ⚙️ Configuration

### YAML Configuration File
```yaml
domain: "nfe"
defaults:
  string_size: 255
  numeric_precision: 15
  numeric_scale: 2
pattern_mappings:
  - pattern: "\[0-9\]\{4\}"
    sql_type: "CHAR(4)"
  - pattern: "\[0-9\]\{14\}"
    sql_type: "CHAR(14)"
namespace_indicators:
  - "http://www.portalfiscal.inf.br/nfe"
root_element_indicators:
  - "TNFe"
  - "TEnviNFe"
root_complex_type_prefixes: ["T"]
xsd_namespace: "http://www.w3.org/2001/XMLSchema"
```

## 📊 Output

### Generated SQL Example
```sql
-- SQL DDL from XSD Schema (Domain: nfe)
-- Generated with generalized XSD to SQL converter

CREATE TABLE TNFe (
    id SERIAL PRIMARY KEY,
    ide_id INTEGER NOT NULL,
    emit_id INTEGER NOT NULL,
    -- ... other columns
);

CREATE TABLE TIde (
    id SERIAL PRIMARY KEY,
    cUF VARCHAR(2) NOT NULL,
    cNF VARCHAR(8) NOT NULL,
    -- ... other columns
);

-- Foreign Key Constraints
ALTER TABLE TNFe ADD CONSTRAINT fk_TNFe_ide_id FOREIGN KEY (ide_id) REFERENCES TIde(id);
ALTER TABLE TNFe ADD CONSTRAINT fk_TNFe_emit_id FOREIGN KEY (emit_id) REFERENCES TEmit(id);

-- Choice Groups (mutually exclusive elements)
-- Table TEndereco: Only one of ['xLgr', 'xNome'] should be populated
```

## 🐛 Troubleshooting

### Common Issues

1. **Domain not detected**
   - Check indicators in configuration file
   - Use `--domain` to force specific domain

2. **XSD file not found**
   - Verify file path
   - Ensure read permissions

3. **XSD parsing error**
   - Validate XSD file
   - Check namespaces and encoding

### Debug Mode
Run with detailed information:
```bash
python main.py schema.xsd --domain nfe 2>&1 | tee conversion.log
```

## 📝 Changelog

### Version 1.0
- ✅ Multi-domain plugin system
- ✅ External YAML configuration
- ✅ Automatic domain detection
- ✅ Choice group support
- ✅ Validated FK constraint generation
- ✅ Intelligent type mapping

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.

## 🆕 Future Versions

- [ ] Support for more databases (MySQL, PostgreSQL, SQL Server)
- [ ] Automatic index generation
- [ ] Web graphical interface
- [ ] Generated schema performance analysis
- [ ] Export to additional formats (JSON Schema, etc.)

---

**Developed to simplify integration between XML systems and relational databases.**