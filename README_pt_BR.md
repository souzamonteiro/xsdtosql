# XSD to SQL Database Schema Converter

Um conversor avançado de esquema XSD para SQL com sistema de plugins e configuração externa para suporte a múltiplos domínios.

## 📋 Visão Geral

Este programa converte arquivos de esquema XML (XSD) em scripts SQL DDL (Data Definition Language) para criação de banco de dados. A ferramenta é especialmente útil para:

- **Integração de sistemas** que utilizam XSD para definição de dados
- **Migração de dados** de formatos XML para bancos de dados relacionais
- **Geração automática** de esquemas de banco de dados a partir de especificações XSD
- **Suporte multi-domínio** com plugins especializados (ex: NF-e, documentos fiscais)

## ✨ Características Principais

### 🎯 Sistema de Plugins
- **Plugins específicos por domínio** (NF-e, genérico, etc.)
- **Detecção automática de domínio** baseada em namespaces e elementos
- **Configuração externa** via arquivos YAML
- **Extensibilidade** para novos domínios

### 🔧 Funcionalidades Avançadas
- **Mapeamento inteligente** de tipos XSD para tipos SQL
- **Suporte a grupos de choice** (elementos mutualmente exclusivos)
- **Detecção de chaves estrangeiras** e relacionamentos
- **Validação de constraints** e integridade referencial
- **Posicionamento otimizado** de campos essenciais

### 📊 Suporte a Tipos de Dados
- **Strings**: VARCHAR com tamanho automático
- **Números**: NUMERIC com precisão configurável
- **Datas**: DATE, TIMESTAMP
- **Padrões personalizados** via configuração
- **Mapeamento baseado em regex**

## 🚀 Instalação

### Pré-requisitos
- Python 3.7+
- Dependências: PyYAML

### Configuração
```bash
# Clone o repositório
git clone <repository-url>
cd xsd-to-sql-converter

# Instale as dependências
pip install pyyaml

# Estrutura de diretórios
mkdir -p config/domains plugins
```

## 📁 Estrutura do Projeto

```
xsd-to-sql-converter/
├── main.py                 # Script principal
├── plugins/               # Diretório de plugins
│   ├── base_plugin.py    # Classe base para plugins
│   ├── nfe_plugin.py     # Plugin específico para NF-e
│   └── generic_plugin.py # Plugin genérico
├── config/
│   └── domains/          # Configurações por domínio
│       ├── nfe.yaml      # Configuração NF-e
│       └── generic.yaml  # Configuração genérica
└── examples/             # Exemplos de uso
```

## 🛠 Uso

### Linha de Comando
```bash
# Conversão básica com detecção automática
python main.py schema.xsd

# Especificando domínio
python main.py schema.xsd --domain nfe

# Múltiplos arquivos XSD
python main.py main.xsd types1.xsd types2.xsd --domain generic
```

### Parâmetros
- `<main_xsd_file>`: Arquivo XSD principal (obrigatório)
- `[type_xsd_files]`: Arquivos XSD adicionais com definições de tipo
- `--domain`: Domínio específico (nfe, generic). Auto-detectado se omitido

### Exemplo de Uso Programático
```python
from main import GeneralizedXSDToSQLConverter

# Inicializar conversor
converter = GeneralizedXSDToSQLConverter(config_dir="config/domains")

# Executar conversão
sql_ddl = converter.convert(
    main_xsd_file="meu_esquema.xsd",
    type_xsd_files=["tipos.xsd"],
    domain="nfe"  # Opcional
)

# Salvar resultado
with open("schema.sql", "w") as f:
    f.write(sql_ddl)
```

## 🔌 Sistema de Plugins

### Plugins Disponíveis

#### NF-e Plugin
Especializado em schemas de Nota Fiscal Eletrônica brasileira:
- Mapeamento de tipos fiscais específicos (TDec, TString)
- Tratamento de elementos NF-e
- Configurações otimizadas para documentos fiscais

#### Generic Plugin
Plugin de uso geral para schemas XSD padrão:
- Suporte a namespaces XSD comuns
- Mapeamento básico de tipos
- Configurável via YAML

### Criando um Novo Plugin

1. **Estender a classe base**:
```python
from plugins.base_plugin import BaseDomainPlugin

class MeuPlugin(BaseDomainPlugin):
    def get_domain_name(self):
        return "meu_dominio"
    
    def should_create_table(self, element, parent_table):
        # Lógica personalizada para criação de tabelas
        pass
```

2. **Criar configuração YAML** em `config/domains/meu_dominio.yaml`

3. **Registrar o plugin** no método `_load_plugins()`

## ⚙️ Configuração

### Arquivo de Configuração YAML
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

## 📊 Saída

### Exemplo de SQL Gerado
```sql
-- SQL DDL from XSD Schema (Domain: nfe)
-- Generated with generalized XSD to SQL converter

CREATE TABLE TNFe (
    id SERIAL PRIMARY KEY,
    ide_id INTEGER NOT NULL,
    emit_id INTEGER NOT NULL,
    -- ... outras colunas
);

CREATE TABLE TIde (
    id SERIAL PRIMARY KEY,
    cUF VARCHAR(2) NOT NULL,
    cNF VARCHAR(8) NOT NULL,
    -- ... outras colunas
);

-- Foreign Key Constraints
ALTER TABLE TNFe ADD CONSTRAINT fk_TNFe_ide_id FOREIGN KEY (ide_id) REFERENCES TIde(id);
ALTER TABLE TNFe ADD CONSTRAINT fk_TNFe_emit_id FOREIGN KEY (emit_id) REFERENCES TEmit(id);

-- Choice Groups (mutually exclusive elements)
-- Table TEndereco: Only one of ['xLgr', 'xNome'] should be populated
```

## 🐛 Solução de Problemas

### Problemas Comuns

1. **Domínio não detectado**
   - Verifique os indicadores no arquivo de configuração
   - Use `--domain` para forçar um domínio específico

2. **Arquivo XSD não encontrado**
   - Verifique o caminho do arquivo
   - Certifique-se de que tem permissões de leitura

3. **Erro de parsing XSD**
   - Valide o arquivo XSD
   - Verifique namespaces e encoding

### Modo Debug
Execute com informações detalhadas:
```bash
python main.py schema.xsd --domain nfe 2>&1 | tee conversion.log
```

## 📝 Log de Alterações

### Versão 1.0
- ✅ Sistema de plugins multi-domínio
- ✅ Configuração externa via YAML
- ✅ Detecção automática de domínio
- ✅ Suporte a grupos de choice
- ✅ Geração de constraints de FK validadas
- ✅ Mapeamento inteligente de tipos

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Distribuído sob a licença Apache 2.0. Veja `LICENSE` para mais informações.

## 🆕 Próximas Versões

- [ ] Suporte a mais bancos de dados (MySQL, PostgreSQL, SQL Server)
- [ ] Geração de índices automáticos
- [ ] Interface gráfica web
- [ ] Análise de performance do schema gerado
- [ ] Export para formatos adicionais (JSON Schema, etc.)

---

**Desenvolvido para simplificar a integração entre sistemas XML e bancos de dados relacionais.**