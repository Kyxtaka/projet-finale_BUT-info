-- Generated by Mocodo 4.2.11

CREATE TABLE AVIS (
  PRIMARY KEY (IDAVIS),
  IDAVIS      VARCHAR(42) NOT NULL,
  DESCRIPTION VARCHAR(42)
);

CREATE TABLE AVOIR (
  PRIMARY KEY (IDLOGEMENT, IDPROPRIO),
  IDLOGEMENT VARCHAR(42) NOT NULL,
  IDPROPRIO  VARCHAR(42) NOT NULL
);

CREATE TABLE BIEN (
  PRIMARY KEY (IDBIEN),
  IDBIEN    VARCHAR(42) NOT NULL,
  NOMB      VARCHAR(42),
  DATEACHAT VARCHAR(42),
  PRIX      VARCHAR(42),
  IDPROPRIO VARCHAR(42) NOT NULL,
  IDCAT     VARCHAR(42) NOT NULL,
  IDTYPE    VARCHAR(42) NOT NULL,
  IDPIECE   VARCHAR(42) NOT NULL
);

CREATE TABLE CATEGORIE (
  PRIMARY KEY (IDCAT),
  IDCAT  VARCHAR(42) NOT NULL,
  NOMCAT VARCHAR(42)
);

CREATE TABLE JUSTIFICATIF (
  PRIMARY KEY (IDJUSTIF),
  IDJUSTIF  VARCHAR(42) NOT NULL,
  NOMJUSTIF VARCHAR(42),
  DATEAJOUT VARCHAR(42),
  URL       VARCHAR(42)
);

CREATE TABLE LOGEMENT (
  PRIMARY KEY (IDLOGEMENT),
  IDLOGEMENT   VARCHAR(42) NOT NULL,
  NOM_LOGEMENT VARCHAR(42),
  TYPEL        VARCHAR(42),
  ADRESSE      VARCHAR(42),
  DESCRIPTION  VARCHAR(42)
);

CREATE TABLE PIECE (
  PRIMARY KEY (IDPIECE),
  IDPIECE     VARCHAR(42) NOT NULL,
  NOMPIECE    VARCHAR(42),
  DESCRIPTION VARCHAR(42)
);

CREATE TABLE PROPRIETAIRE (
  PRIMARY KEY (IDPROPRIO),
  IDPROPRIO  VARCHAR(42) NOT NULL,
  NOMPROPRIO VARCHAR(42),
  PRENOM     VARCHAR(42),
  EMAIL      VARCHAR(42),
  PASSWORD   VARCHAR(42)
);

CREATE TABLE TYPEBIEN (
  PRIMARY KEY (IDTYPE),
  IDTYPE  VARCHAR(42) NOT NULL,
  NOMTYPE VARCHAR(42)
);

ALTER TABLE AVOIR ADD FOREIGN KEY (IDPROPRIO) REFERENCES PROPRIETAIRE (IDPROPRIO);
ALTER TABLE AVOIR ADD FOREIGN KEY (IDLOGEMENT) REFERENCES LOGEMENT (IDLOGEMENT);

ALTER TABLE BIEN ADD FOREIGN KEY (IDPIECE) REFERENCES PIECE (IDPIECE);
ALTER TABLE BIEN ADD FOREIGN KEY (IDTYPE) REFERENCES TYPEBIEN (IDTYPE);
ALTER TABLE BIEN ADD FOREIGN KEY (IDCAT) REFERENCES CATEGORIE (IDCAT);
ALTER TABLE BIEN ADD FOREIGN KEY (IDPROPRIO) REFERENCES PROPRIETAIRE (IDPROPRIO);
