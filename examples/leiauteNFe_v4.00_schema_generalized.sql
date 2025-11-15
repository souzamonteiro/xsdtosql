-- SQL DDL from XSD Schema (Domain: nfe)
-- Generated with generalized XSD to SQL converter
-- Fixed version: Proper field overrides and FK validation

CREATE TABLE TNFe (
    id SERIAL NOT NULL PRIMARY KEY
);

CREATE TABLE infNFe (
    id SERIAL NOT NULL PRIMARY KEY,
    tnfe_id INTEGER NOT NULL,
    retirada VARCHAR(255),
    entrega VARCHAR(255),
    infRespTec VARCHAR(255)
);

CREATE TABLE ide (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    cUF CHAR(2) NOT NULL,
    cNF VARCHAR(8) NOT NULL,
    natOp VARCHAR(60) NOT NULL,
    mod CHAR(2) NOT NULL,
    serie SMALLINT NOT NULL,
    nNF INTEGER NOT NULL,
    dhEmi TIMESTAMP NOT NULL,
    dhSaiEnt TIMESTAMP,
    tpNF VARCHAR(255) NOT NULL,
    idDest VARCHAR(255) NOT NULL,
    cMunFG CHAR(7) NOT NULL,
    tpImp VARCHAR(255) NOT NULL,
    tpEmis VARCHAR(255) NOT NULL,
    cDV VARCHAR(1) NOT NULL,
    tpAmb CHAR(1) NOT NULL,
    finNFe VARCHAR(255) NOT NULL,
    indFinal VARCHAR(255) NOT NULL,
    indPres VARCHAR(255) NOT NULL,
    indIntermed VARCHAR(255),
    procEmi VARCHAR(255) NOT NULL,
    verProc VARCHAR(20) NOT NULL
);

CREATE TABLE NFref (
    id SERIAL NOT NULL PRIMARY KEY,
    ide_id INTEGER NOT NULL,
    AAMM VARCHAR(2) NOT NULL,
    CNPJ CHAR(14) NOT NULL,
    refNFe CHAR(44),
    refNFeSig CHAR(44),
    refCTe CHAR(44)
);

CREATE TABLE refNFP (
    id SERIAL NOT NULL PRIMARY KEY,
    nfref_id INTEGER NOT NULL,
    IE VARCHAR(14) NOT NULL,
    CPF CHAR(11)
);

CREATE TABLE refECF (
    id SERIAL NOT NULL PRIMARY KEY,
    nfref_id INTEGER NOT NULL,
    nECF VARCHAR(255) NOT NULL,
    nCOO VARCHAR(255) NOT NULL
);

CREATE TABLE emit (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    CPF CHAR(11),
    CNPJ CHAR(14),
    xNome VARCHAR(60) NOT NULL,
    xFant VARCHAR(60),
    enderEmit VARCHAR(255) NOT NULL,
    IEST VARCHAR(14),
    CRT VARCHAR(255) NOT NULL
);

CREATE TABLE avulsa (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    xOrgao VARCHAR(60) NOT NULL,
    matr VARCHAR(60) NOT NULL,
    xAgente VARCHAR(60) NOT NULL,
    fone VARCHAR(255),
    UF CHAR(2) NOT NULL,
    nDAR VARCHAR(60),
    dEmi DATE,
    vDAR NUMERIC(15,2),
    repEmi VARCHAR(60) NOT NULL,
    dPag DATE
);

CREATE TABLE dest (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    idEstrangeiro VARCHAR(20),
    CPF CHAR(11),
    CNPJ CHAR(14),
    enderDest VARCHAR(255),
    indIEDest VARCHAR(255) NOT NULL,
    ISUF VARCHAR(255),
    IM VARCHAR(15),
    email VARCHAR(60),
    idEstrangeiro VARCHAR(20)
);

CREATE TABLE autXML (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    CPF CHAR(11),
    CNPJ CHAR(14)
);

CREATE TABLE det (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    infAdProd VARCHAR(500)
);

CREATE TABLE prod (
    id SERIAL NOT NULL PRIMARY KEY,
    det_id INTEGER NOT NULL,
    cProd VARCHAR(60) NOT NULL,
    cEAN VARCHAR(14) NOT NULL,
    cBarra VARCHAR(30),
    xProd VARCHAR(120) NOT NULL,
    NCM VARCHAR(8) NOT NULL,
    NVE VARCHAR(2),
    cBenef VARCHAR(8),
    EXTIPI VARCHAR(255),
    CFOP CHAR(4) NOT NULL,
    uCom VARCHAR(6) NOT NULL,
    qCom NUMERIC(15,4) NOT NULL,
    vUnCom NUMERIC(21,10) NOT NULL,
    vProd NUMERIC(15,2) NOT NULL,
    cEANTrib VARCHAR(14) NOT NULL,
    cBarraTrib VARCHAR(30),
    uTrib VARCHAR(6) NOT NULL,
    qTrib NUMERIC(15,4) NOT NULL,
    vUnTrib NUMERIC(21,10) NOT NULL,
    vFrete NUMERIC(15,2),
    vSeg NUMERIC(15,2),
    vDesc NUMERIC(15,2),
    vOutro NUMERIC(15,2),
    indTot VARCHAR(255) NOT NULL,
    xPed VARCHAR(15),
    nItemPed VARCHAR(255),
    nFCI UUID,
    nRECOPI VARCHAR(20)
);

CREATE TABLE DI (
    id SERIAL NOT NULL PRIMARY KEY,
    prod_id INTEGER NOT NULL,
    nDI VARCHAR(15) NOT NULL,
    dDI DATE NOT NULL,
    xLocDesemb VARCHAR(60) NOT NULL,
    UFDesemb CHAR(2) NOT NULL,
    dDesemb DATE NOT NULL,
    tpViaTransp VARCHAR(255) NOT NULL,
    vAFRMM NUMERIC(15,2),
    tpIntermedio VARCHAR(255) NOT NULL,
    UFTerceiro CHAR(2),
    cExportador VARCHAR(60) NOT NULL
);

CREATE TABLE adi (
    id SERIAL NOT NULL PRIMARY KEY,
    di_id INTEGER NOT NULL,
    nAdicao VARCHAR(1),
    nSeqAdic VARCHAR(1) NOT NULL,
    cFabricante VARCHAR(60) NOT NULL,
    vDescDI NUMERIC(15,2),
    nDraw VARCHAR(20)
);

CREATE TABLE detExport (
    id SERIAL NOT NULL PRIMARY KEY,
    prod_id INTEGER NOT NULL
);

CREATE TABLE exportInd (
    id SERIAL NOT NULL PRIMARY KEY,
    detexport_id INTEGER NOT NULL,
    nRE VARCHAR(255) NOT NULL,
    chNFe CHAR(44) NOT NULL,
    qExport NUMERIC(15,4) NOT NULL
);

CREATE TABLE rastro (
    id SERIAL NOT NULL PRIMARY KEY,
    prod_id INTEGER NOT NULL,
    nLote VARCHAR(20) NOT NULL,
    qLote NUMERIC(11,3) NOT NULL,
    dFab DATE NOT NULL,
    dVal DATE NOT NULL,
    cAgreg VARCHAR(20)
);

CREATE TABLE infProdNFF (
    id SERIAL NOT NULL PRIMARY KEY,
    prod_id INTEGER NOT NULL,
    cProdFisco VARCHAR(255) NOT NULL,
    cOperNFF VARCHAR(255) NOT NULL
);

CREATE TABLE infProdEmb (
    id SERIAL NOT NULL PRIMARY KEY,
    prod_id INTEGER NOT NULL,
    xEmb VARCHAR(8) NOT NULL,
    qVolEmb NUMERIC(11,3) NOT NULL,
    uEmb VARCHAR(8) NOT NULL
);

CREATE TABLE veicProd (
    id SERIAL NOT NULL PRIMARY KEY,
    prod_id INTEGER NOT NULL,
    tpOp VARCHAR(255) NOT NULL,
    chassi VARCHAR(255) NOT NULL,
    cCor VARCHAR(4) NOT NULL,
    xCor VARCHAR(40) NOT NULL,
    pot VARCHAR(4) NOT NULL,
    cilin VARCHAR(4) NOT NULL,
    pesoL VARCHAR(9) NOT NULL,
    pesoB VARCHAR(9) NOT NULL,
    nSerie VARCHAR(9) NOT NULL,
    tpComb VARCHAR(2) NOT NULL,
    nMotor VARCHAR(21) NOT NULL,
    CMT VARCHAR(9) NOT NULL,
    dist VARCHAR(4) NOT NULL,
    anoMod VARCHAR(4) NOT NULL,
    anoFab VARCHAR(4) NOT NULL,
    tpPint VARCHAR(255) NOT NULL,
    tpVeic VARCHAR(255) NOT NULL,
    espVeic VARCHAR(1) NOT NULL,
    VIN VARCHAR(255) NOT NULL,
    condVeic VARCHAR(255) NOT NULL,
    cMod VARCHAR(255) NOT NULL,
    cCorDENATRAN VARCHAR(2) NOT NULL,
    lota VARCHAR(3) NOT NULL,
    tpRest VARCHAR(255) NOT NULL
);

CREATE TABLE med (
    id SERIAL NOT NULL PRIMARY KEY,
    prod_id INTEGER NOT NULL,
    cProdANVISA VARCHAR(11) NOT NULL,
    xMotivoIsencao VARCHAR(255),
    vPMC NUMERIC(15,2) NOT NULL
);

CREATE TABLE arma (
    id SERIAL NOT NULL PRIMARY KEY,
    prod_id INTEGER NOT NULL,
    tpArma VARCHAR(255) NOT NULL,
    nCano VARCHAR(15) NOT NULL,
    descr VARCHAR(256) NOT NULL
);

CREATE TABLE comb (
    id SERIAL NOT NULL PRIMARY KEY,
    prod_id INTEGER NOT NULL,
    cProdANP VARCHAR(9) NOT NULL,
    descANP VARCHAR(95) NOT NULL,
    pGLP NUMERIC(5,4),
    pGNn NUMERIC(5,4),
    pGNi NUMERIC(5,4),
    vPart NUMERIC(15,2),
    CODIF VARCHAR(255),
    qTemp NUMERIC(16,4),
    UFCons CHAR(2) NOT NULL,
    pBio NUMERIC(15,2)
);

CREATE TABLE CIDE (
    id SERIAL NOT NULL PRIMARY KEY,
    comb_id INTEGER NOT NULL,
    qBCProd NUMERIC(16,4) NOT NULL,
    vAliqProd NUMERIC(15,4) NOT NULL,
    vCIDE NUMERIC(15,2) NOT NULL
);

CREATE TABLE encerrante (
    id SERIAL NOT NULL PRIMARY KEY,
    comb_id INTEGER NOT NULL,
    nBico VARCHAR(255) NOT NULL,
    nBomba VARCHAR(255),
    nTanque VARCHAR(255) NOT NULL,
    vEncIni NUMERIC(15,3) NOT NULL,
    vEncFin NUMERIC(15,3) NOT NULL
);

CREATE TABLE origComb (
    id SERIAL NOT NULL PRIMARY KEY,
    comb_id INTEGER NOT NULL,
    indImport VARCHAR(255) NOT NULL,
    cUFOrig CHAR(2) NOT NULL,
    pOrig NUMERIC(15,2) NOT NULL
);

CREATE TABLE imposto (
    id SERIAL NOT NULL PRIMARY KEY,
    det_id INTEGER NOT NULL,
    vTotTrib NUMERIC(15,2)
);

CREATE TABLE PIS (
    id SERIAL NOT NULL PRIMARY KEY,
    imposto_id INTEGER NOT NULL,
    CST VARCHAR(255) NOT NULL,
    vBC NUMERIC(15,2) NOT NULL,
    pPIS NUMERIC(5,4) NOT NULL,
    vPIS NUMERIC(15,2) NOT NULL
);

CREATE TABLE PISST (
    id SERIAL NOT NULL PRIMARY KEY,
    imposto_id INTEGER NOT NULL,
    indSomaPISST VARCHAR(255)
);

CREATE TABLE COFINS (
    id SERIAL NOT NULL PRIMARY KEY,
    imposto_id INTEGER NOT NULL,
    pCOFINS NUMERIC(5,4) NOT NULL,
    vCOFINS NUMERIC(15,2) NOT NULL
);

CREATE TABLE COFINSST (
    id SERIAL NOT NULL PRIMARY KEY,
    imposto_id INTEGER NOT NULL,
    indSomaCOFINSST VARCHAR(255)
);

CREATE TABLE ICMSUFDest (
    id SERIAL NOT NULL PRIMARY KEY,
    imposto_id INTEGER NOT NULL,
    vBCUFDest NUMERIC(15,2) NOT NULL,
    vBCFCPUFDest NUMERIC(15,2),
    pFCPUFDest NUMERIC(5,4),
    pICMSUFDest NUMERIC(5,4) NOT NULL,
    pICMSInter VARCHAR(255) NOT NULL,
    pICMSInterPart NUMERIC(5,4) NOT NULL,
    vFCPUFDest NUMERIC(15,2),
    vICMSUFDest NUMERIC(15,2) NOT NULL,
    vICMSUFRemet NUMERIC(15,2) NOT NULL
);

CREATE TABLE impostoDevol (
    id SERIAL NOT NULL PRIMARY KEY,
    det_id INTEGER NOT NULL,
    pDevol NUMERIC(5,2) NOT NULL
);

CREATE TABLE IPI (
    id SERIAL NOT NULL PRIMARY KEY,
    impostodevol_id INTEGER NOT NULL,
    vIPIDevol NUMERIC(15,2) NOT NULL
);

CREATE TABLE obsItem (
    id SERIAL NOT NULL PRIMARY KEY,
    det_id INTEGER NOT NULL
);

CREATE TABLE obsCont (
    id SERIAL NOT NULL PRIMARY KEY,
    obsitem_id INTEGER NOT NULL,
    xTexto VARCHAR(60) NOT NULL
);

CREATE TABLE total (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL
);

CREATE TABLE ICMSTot (
    id SERIAL NOT NULL PRIMARY KEY,
    total_id INTEGER NOT NULL,
    vICMS NUMERIC(15,2) NOT NULL,
    vICMSDeson NUMERIC(15,2) NOT NULL,
    vFCP NUMERIC(15,2) NOT NULL,
    vBCST NUMERIC(15,2) NOT NULL,
    vST NUMERIC(15,2) NOT NULL,
    vFCPST NUMERIC(15,2) NOT NULL,
    vFCPSTRet NUMERIC(15,2) NOT NULL,
    qBCMono NUMERIC(15,2),
    vICMSMono NUMERIC(15,2),
    qBCMonoReten NUMERIC(15,2),
    vICMSMonoReten NUMERIC(15,2),
    qBCMonoRet NUMERIC(15,2),
    vICMSMonoRet NUMERIC(15,2),
    vII NUMERIC(15,2) NOT NULL,
    vIPI NUMERIC(15,2) NOT NULL,
    vNF NUMERIC(15,2) NOT NULL
);

CREATE TABLE ISSQNtot (
    id SERIAL NOT NULL PRIMARY KEY,
    total_id INTEGER NOT NULL,
    vServ NUMERIC(15,2),
    vISS NUMERIC(15,2),
    dCompet DATE NOT NULL,
    vDeducao NUMERIC(15,2),
    vDescIncond NUMERIC(15,2),
    vDescCond NUMERIC(15,2),
    vISSRet NUMERIC(15,2),
    cRegTrib VARCHAR(255)
);

CREATE TABLE retTrib (
    id SERIAL NOT NULL PRIMARY KEY,
    total_id INTEGER NOT NULL,
    vRetPIS NUMERIC(15,2),
    vRetCOFINS NUMERIC(15,2),
    vRetCSLL NUMERIC(15,2),
    vBCIRRF NUMERIC(15,2),
    vIRRF NUMERIC(15,2),
    vBCRetPrev NUMERIC(15,2),
    vRetPrev NUMERIC(15,2)
);

CREATE TABLE transp (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    modFrete VARCHAR(255) NOT NULL
);

CREATE TABLE transporta (
    id SERIAL NOT NULL PRIMARY KEY,
    transp_id INTEGER NOT NULL,
    CPF CHAR(11),
    CNPJ CHAR(14),
    xEnder VARCHAR(60),
    xMun VARCHAR(60)
);

CREATE TABLE retTransp (
    id SERIAL NOT NULL PRIMARY KEY,
    transp_id INTEGER NOT NULL,
    vBCRet NUMERIC(15,2) NOT NULL,
    pICMSRet NUMERIC(5,4) NOT NULL,
    vICMSRet NUMERIC(15,2) NOT NULL
);

CREATE TABLE vol (
    id SERIAL NOT NULL PRIMARY KEY,
    transp_id INTEGER NOT NULL,
    qVol VARCHAR(255),
    esp VARCHAR(60),
    marca VARCHAR(60),
    nVol VARCHAR(60)
);

CREATE TABLE lacres (
    id SERIAL NOT NULL PRIMARY KEY,
    vol_id INTEGER NOT NULL,
    nLacre VARCHAR(60) NOT NULL
);

CREATE TABLE cobr (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL
);

CREATE TABLE fat (
    id SERIAL NOT NULL PRIMARY KEY,
    cobr_id INTEGER NOT NULL,
    nFat VARCHAR(60),
    vOrig NUMERIC(15,2),
    vLiq NUMERIC(15,2)
);

CREATE TABLE dup (
    id SERIAL NOT NULL PRIMARY KEY,
    cobr_id INTEGER NOT NULL,
    nDup VARCHAR(60),
    dVenc DATE,
    vDup NUMERIC(15,2) NOT NULL
);

CREATE TABLE pag (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    vTroco NUMERIC(15,2)
);

CREATE TABLE detPag (
    id SERIAL NOT NULL PRIMARY KEY,
    pag_id INTEGER NOT NULL,
    indPag VARCHAR(255),
    tPag VARCHAR(2) NOT NULL,
    xPag VARCHAR(60),
    vPag NUMERIC(15,2) NOT NULL
);

CREATE TABLE card (
    id SERIAL NOT NULL PRIMARY KEY,
    detpag_id INTEGER NOT NULL,
    tpIntegra VARCHAR(255) NOT NULL,
    tBand VARCHAR(2),
    cAut VARCHAR(20)
);

CREATE TABLE infIntermed (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    idCadIntTran VARCHAR(60) NOT NULL
);

CREATE TABLE infAdic (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    infAdFisco VARCHAR(2000),
    infCpl VARCHAR(5000)
);

CREATE TABLE procRef (
    id SERIAL NOT NULL PRIMARY KEY,
    infadic_id INTEGER NOT NULL,
    nProc VARCHAR(60) NOT NULL,
    indProc VARCHAR(255) NOT NULL,
    tpAto VARCHAR(255)
);

CREATE TABLE exporta (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    UFSaidaPais CHAR(2) NOT NULL,
    xLocExporta VARCHAR(60) NOT NULL,
    xLocDespacho VARCHAR(60)
);

CREATE TABLE compra (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    xNEmp VARCHAR(22),
    xCont VARCHAR(60)
);

CREATE TABLE cana (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    safra VARCHAR(9) NOT NULL,
    ref VARCHAR(255) NOT NULL,
    qTotMes NUMERIC(21,10) NOT NULL,
    qTotAnt NUMERIC(21,10) NOT NULL,
    qTotGer NUMERIC(21,10) NOT NULL,
    vFor NUMERIC(15,2) NOT NULL,
    vTotDed NUMERIC(15,2) NOT NULL,
    vLiqFor NUMERIC(15,2) NOT NULL
);

CREATE TABLE forDia (
    id SERIAL NOT NULL PRIMARY KEY,
    cana_id INTEGER NOT NULL,
    qtde NUMERIC(21,10) NOT NULL
);

CREATE TABLE deduc (
    id SERIAL NOT NULL PRIMARY KEY,
    cana_id INTEGER NOT NULL,
    xDed VARCHAR(60) NOT NULL,
    vDed NUMERIC(15,2) NOT NULL
);

CREATE TABLE infSolicNFF (
    id SERIAL NOT NULL PRIMARY KEY,
    infnfe_id INTEGER NOT NULL,
    xSolic VARCHAR(5000) NOT NULL
);

CREATE TABLE infNFeSupl (
    id SERIAL NOT NULL PRIMARY KEY,
    tnfe_id INTEGER NOT NULL,
    qrCode VARCHAR(600) NOT NULL,
    urlChave VARCHAR(85) NOT NULL
);

CREATE TABLE TProtNFe (
    id SERIAL NOT NULL PRIMARY KEY
);

CREATE TABLE infProt (
    id SERIAL NOT NULL PRIMARY KEY,
    tprotnfe_id INTEGER NOT NULL,
    verAplic VARCHAR(255) NOT NULL,
    dhRecbto TIMESTAMP NOT NULL,
    nProt CHAR(15),
    digVal VARCHAR(255),
    cStat CHAR(3) NOT NULL,
    xMotivo VARCHAR(255) NOT NULL
);

CREATE TABLE TEnviNFe (
    id SERIAL NOT NULL PRIMARY KEY,
    idLote VARCHAR(255) NOT NULL,
    indSinc VARCHAR(255) NOT NULL,
    NFe VARCHAR(255) NOT NULL
);

CREATE TABLE TRetEnviNFe (
    id SERIAL NOT NULL PRIMARY KEY,
    protNFe VARCHAR(255)
);

CREATE TABLE infRec (
    id SERIAL NOT NULL PRIMARY KEY,
    tretenvinfe_id INTEGER NOT NULL,
    nRec CHAR(15) NOT NULL,
    tMed VARCHAR(255) NOT NULL
);

CREATE TABLE TEndereco (
    id SERIAL NOT NULL PRIMARY KEY,
    xLgr VARCHAR(60) NOT NULL,
    nro VARCHAR(60) NOT NULL,
    xCpl VARCHAR(60),
    xBairro VARCHAR(60) NOT NULL,
    cMun CHAR(7) NOT NULL,
    CEP VARCHAR(8),
    cPais VARCHAR(255),
    xPais VARCHAR(60)
);

CREATE TABLE TInfRespTec (
    id SERIAL NOT NULL PRIMARY KEY,
    xContato VARCHAR(60) NOT NULL
);

CREATE TABLE TVeiculo (
    id SERIAL NOT NULL PRIMARY KEY,
    placa VARCHAR(7) NOT NULL,
    RNTC VARCHAR(20)
);

CREATE TABLE TIpi (
    id SERIAL NOT NULL PRIMARY KEY,
    CNPJProd CHAR(14),
    cSelo VARCHAR(60),
    qSelo VARCHAR(255),
    cEnq VARCHAR(3) NOT NULL
);


-- Foreign Key Constraints (Validated)
ALTER TABLE ide ADD CONSTRAINT fk_ide_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE NFref ADD CONSTRAINT fk_NFref_ide_id FOREIGN KEY (ide_id) REFERENCES ide(id);
ALTER TABLE refNFP ADD CONSTRAINT fk_refNFP_nfref_id FOREIGN KEY (nfref_id) REFERENCES NFref(id);
ALTER TABLE refECF ADD CONSTRAINT fk_refECF_nfref_id FOREIGN KEY (nfref_id) REFERENCES NFref(id);
ALTER TABLE emit ADD CONSTRAINT fk_emit_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE avulsa ADD CONSTRAINT fk_avulsa_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE dest ADD CONSTRAINT fk_dest_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE autXML ADD CONSTRAINT fk_autXML_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE det ADD CONSTRAINT fk_det_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE prod ADD CONSTRAINT fk_prod_det_id FOREIGN KEY (det_id) REFERENCES det(id);
ALTER TABLE DI ADD CONSTRAINT fk_DI_prod_id FOREIGN KEY (prod_id) REFERENCES prod(id);
ALTER TABLE adi ADD CONSTRAINT fk_adi_di_id FOREIGN KEY (di_id) REFERENCES DI(id);
ALTER TABLE detExport ADD CONSTRAINT fk_detExport_prod_id FOREIGN KEY (prod_id) REFERENCES prod(id);
ALTER TABLE rastro ADD CONSTRAINT fk_rastro_prod_id FOREIGN KEY (prod_id) REFERENCES prod(id);
ALTER TABLE infProdNFF ADD CONSTRAINT fk_infProdNFF_prod_id FOREIGN KEY (prod_id) REFERENCES prod(id);
ALTER TABLE infProdEmb ADD CONSTRAINT fk_infProdEmb_prod_id FOREIGN KEY (prod_id) REFERENCES prod(id);
ALTER TABLE veicProd ADD CONSTRAINT fk_veicProd_prod_id FOREIGN KEY (prod_id) REFERENCES prod(id);
ALTER TABLE med ADD CONSTRAINT fk_med_prod_id FOREIGN KEY (prod_id) REFERENCES prod(id);
ALTER TABLE arma ADD CONSTRAINT fk_arma_prod_id FOREIGN KEY (prod_id) REFERENCES prod(id);
ALTER TABLE comb ADD CONSTRAINT fk_comb_prod_id FOREIGN KEY (prod_id) REFERENCES prod(id);
ALTER TABLE CIDE ADD CONSTRAINT fk_CIDE_comb_id FOREIGN KEY (comb_id) REFERENCES comb(id);
ALTER TABLE encerrante ADD CONSTRAINT fk_encerrante_comb_id FOREIGN KEY (comb_id) REFERENCES comb(id);
ALTER TABLE origComb ADD CONSTRAINT fk_origComb_comb_id FOREIGN KEY (comb_id) REFERENCES comb(id);
ALTER TABLE imposto ADD CONSTRAINT fk_imposto_det_id FOREIGN KEY (det_id) REFERENCES det(id);
ALTER TABLE PIS ADD CONSTRAINT fk_PIS_imposto_id FOREIGN KEY (imposto_id) REFERENCES imposto(id);
ALTER TABLE PISST ADD CONSTRAINT fk_PISST_imposto_id FOREIGN KEY (imposto_id) REFERENCES imposto(id);
ALTER TABLE COFINS ADD CONSTRAINT fk_COFINS_imposto_id FOREIGN KEY (imposto_id) REFERENCES imposto(id);
ALTER TABLE COFINSST ADD CONSTRAINT fk_COFINSST_imposto_id FOREIGN KEY (imposto_id) REFERENCES imposto(id);
ALTER TABLE ICMSUFDest ADD CONSTRAINT fk_ICMSUFDest_imposto_id FOREIGN KEY (imposto_id) REFERENCES imposto(id);
ALTER TABLE impostoDevol ADD CONSTRAINT fk_impostoDevol_det_id FOREIGN KEY (det_id) REFERENCES det(id);
ALTER TABLE IPI ADD CONSTRAINT fk_IPI_impostodevol_id FOREIGN KEY (impostodevol_id) REFERENCES impostoDevol(id);
ALTER TABLE obsItem ADD CONSTRAINT fk_obsItem_det_id FOREIGN KEY (det_id) REFERENCES det(id);
ALTER TABLE total ADD CONSTRAINT fk_total_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE transp ADD CONSTRAINT fk_transp_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE transporta ADD CONSTRAINT fk_transporta_transp_id FOREIGN KEY (transp_id) REFERENCES transp(id);
ALTER TABLE retTransp ADD CONSTRAINT fk_retTransp_transp_id FOREIGN KEY (transp_id) REFERENCES transp(id);
ALTER TABLE vol ADD CONSTRAINT fk_vol_transp_id FOREIGN KEY (transp_id) REFERENCES transp(id);
ALTER TABLE lacres ADD CONSTRAINT fk_lacres_vol_id FOREIGN KEY (vol_id) REFERENCES vol(id);
ALTER TABLE cobr ADD CONSTRAINT fk_cobr_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE pag ADD CONSTRAINT fk_pag_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE detPag ADD CONSTRAINT fk_detPag_pag_id FOREIGN KEY (pag_id) REFERENCES pag(id);
ALTER TABLE card ADD CONSTRAINT fk_card_detpag_id FOREIGN KEY (detpag_id) REFERENCES detPag(id);
ALTER TABLE infIntermed ADD CONSTRAINT fk_infIntermed_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE infAdic ADD CONSTRAINT fk_infAdic_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE procRef ADD CONSTRAINT fk_procRef_infadic_id FOREIGN KEY (infadic_id) REFERENCES infAdic(id);
ALTER TABLE exporta ADD CONSTRAINT fk_exporta_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE compra ADD CONSTRAINT fk_compra_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE cana ADD CONSTRAINT fk_cana_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE forDia ADD CONSTRAINT fk_forDia_cana_id FOREIGN KEY (cana_id) REFERENCES cana(id);
ALTER TABLE deduc ADD CONSTRAINT fk_deduc_cana_id FOREIGN KEY (cana_id) REFERENCES cana(id);
ALTER TABLE infSolicNFF ADD CONSTRAINT fk_infSolicNFF_infnfe_id FOREIGN KEY (infnfe_id) REFERENCES infNFe(id);
ALTER TABLE infRec ADD CONSTRAINT fk_infRec_tretenvinfe_id FOREIGN KEY (tretenvinfe_id) REFERENCES TRetEnviNFe(id);
-- Generated 52 valid foreign key constraints

-- Choice Groups (mutually exclusive elements)
-- Table refNFP: Only one of ['CNPJ', 'CPF'] should be populated
-- Table NFref: Only one of ['refNFe', 'refNFeSig', 'refNF', 'refNFP', 'refCTe', 'refECF'] should be populated
-- Table ide: Only one of ['refNFe', 'refNFeSig', 'refNF', 'refNFP', 'refCTe', 'refECF'] should be populated
-- Table emit: Only one of ['CNPJ', 'CPF'] should be populated
-- Table dest: Only one of ['CNPJ', 'CPF', 'idEstrangeiro'] should be populated
-- Table autXML: Only one of ['CNPJ', 'CPF'] should be populated
-- Table prod: Only one of ['veicProd', 'med', 'arma', 'comb', 'nRECOPI'] should be populated
-- Table PIS: Only one of ['PISAliq', 'PISQtde', 'PISNT', 'PISOutr'] should be populated
-- Table COFINS: Only one of ['COFINSAliq', 'COFINSQtde', 'COFINSNT', 'COFINSOutr'] should be populated
-- Table det: Only one of ['veicProd', 'med', 'arma', 'comb', 'nRECOPI'] should be populated
-- Table transporta: Only one of ['CNPJ', 'CPF'] should be populated
-- Table transp: Only one of ['CNPJ', 'CPF'] should be populated
-- Table infNFe: Only one of ['refNFe', 'refNFeSig', 'refNF', 'refNFP', 'refCTe', 'refECF'] should be populated
-- Table TNFe: Only one of ['refNFe', 'refNFeSig', 'refNF', 'refNFP', 'refCTe', 'refECF'] should be populated
-- Table TRetEnviNFe: Only one of ['infRec', 'protNFe'] should be populated
-- Table TLocal: Only one of ['CNPJ', 'CPF'] should be populated
-- Table TIpi: Only one of ['IPITrib', 'IPINT'] should be populated
