#!/bin/bash

DIRNAME="$(dirname "$0")"

# Auto-detect domain
$DIRNAME/xsd_to_sql.sh examples/leiauteNFe_v4.00.xsd examples/tiposBasico_v4.00.xsd examples/xmldsig-core-schema_v1.01.xsd

# Force NF-e domain
#$DIRNAME/xsd_to_sql.sh leiauteNFe_v4.00.xsd --domain nfe
