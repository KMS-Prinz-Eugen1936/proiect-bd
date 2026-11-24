CREATE TYPE rol_utilizator AS ENUM ('Admin', 'Operator', 'Tehnician');

CREATE TABLE IF NOT EXISTS utilizator (
    id_utilizator INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nume VARCHAR(150) NOT NULL,
    rol rol_utilizator NOT NULL
);

CREATE TABLE IF NOT EXISTS client (
    id_client INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nume VARCHAR(150) NOT NULL,
    adresa TEXT,
    telefon VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bon_reparatie (
    id_bon INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_client INT NOT NULL REFERENCES client(id_client) ON DELETE CASCADE,
    id_operator INT REFERENCES utilizator(id_utilizator) ON DELETE SET NULL,
    id_tehnician INT REFERENCES utilizator(id_utilizator) ON DELETE SET NULL,
    este_in_garantie BOOLEAN NOT NULL DEFAULT FALSE,
    data_intrarii TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Introdus in sistem',
    defect TEXT NOT NULL,
    reparatie_efectuata TEXT,
    observatii TEXT
);

CREATE TABLE IF NOT EXISTS piesa (
    id_piesa INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cod_piesa VARCHAR(80) NOT NULL UNIQUE,
    denumire VARCHAR(200) NOT NULL,
    brand_compatibil VARCHAR(120),
    pret_unitar DECIMAL(10, 2) NOT NULL CHECK (pret_unitar >= 0),
    stoc_disponibil INT NOT NULL DEFAULT 0 CHECK (stoc_disponibil >= 0)
);

CREATE TABLE IF NOT EXISTS piese_utilizate (
    id_utilizare INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_bon INT NOT NULL REFERENCES bon_reparatie(id_bon) ON DELETE CASCADE,
    id_piesa INT NOT NULL REFERENCES piesa(id_piesa) ON DELETE RESTRICT,
    cantitate INT NOT NULL CHECK (cantitate > 0),
    pret_la_momentul_reparatiei DECIMAL(10, 2) NOT NULL CHECK (pret_la_momentul_reparatiei >= 0)
);

CREATE TABLE IF NOT EXISTS aparat_post_garantie (
    id_aparat INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_bon INT NOT NULL UNIQUE REFERENCES bon_reparatie(id_bon) ON DELETE CASCADE,
    denumire_aparat VARCHAR(200) NOT NULL,
    accesorii TEXT
);

CREATE TABLE IF NOT EXISTS garantie_producator (
    id_garantie INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_bon INT NOT NULL UNIQUE REFERENCES bon_reparatie(id_bon) ON DELETE CASCADE,
    data_achizitiei DATE NOT NULL,
    loc_achizitie VARCHAR(150),
    nr_factura VARCHAR(100),
    nr_certificat_garantie VARCHAR(100),
    nr_fisa VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS detalii_bosch_siemens_neff (
    id_detaliu INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_garantie INT NOT NULL UNIQUE REFERENCES garantie_producator(id_garantie) ON DELETE CASCADE,
    denumire VARCHAR(200),
    e_nr VARCHAR(100),
    fd VARCHAR(100),
    z_nr VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS detalii_electrolux_aeg (
    id_detaliu INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_garantie INT NOT NULL UNIQUE REFERENCES garantie_producator(id_garantie) ON DELETE CASCADE,
    denumire VARCHAR(200),
    model VARCHAR(120),
    pnc VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS detalii_miele (
    id_detaliu INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_garantie INT NOT NULL UNIQUE REFERENCES garantie_producator(id_garantie) ON DELETE CASCADE,
    denumire VARCHAR(200),
    campuri_specifice TEXT
);

CREATE TABLE IF NOT EXISTS detalii_teka (
    id_detaliu INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_garantie INT NOT NULL UNIQUE REFERENCES garantie_producator(id_garantie) ON DELETE CASCADE,
    denumire VARCHAR(200),
    campuri_specifice TEXT
);

CREATE TABLE IF NOT EXISTS detalii_samus_albatros (
    id_detaliu INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_garantie INT NOT NULL UNIQUE REFERENCES garantie_producator(id_garantie) ON DELETE CASCADE,
    denumire VARCHAR(200),
    campuri_specifice TEXT
);

INSERT INTO utilizator (nume, rol) VALUES
    ('Admin Principal', 'Admin'),
    ('Operator Receptie', 'Operator'),
    ('Tehnician 1', 'Tehnician'),
    ('Tehnician 2', 'Tehnician'),
    ('Tehnician 3', 'Tehnician');

INSERT INTO client (nume, adresa, telefon) VALUES
    ('Popescu Ion', 'Str. Victoriei nr. 12', '0740111222'),
    ('Ionescu Maria', 'Bd. Unirii nr. 45', '0740333444');

INSERT INTO piesa (cod_piesa, denumire, brand_compatibil, pret_unitar, stoc_disponibil) VALUES
    ('P-100', 'Rezistenta cuptor', 'Bosch', 145.00, 6),
    ('P-204', 'Pompa evacuare', 'Electrolux / AEG', 90.00, 12);

INSERT INTO bon_reparatie (
    id_client, id_operator, id_tehnician, este_in_garantie, status, defect, observatii
) VALUES
    (1, 2, 3, TRUE, 'In reparatie', 'Nu incalzeste', 'Are certificat original'),
    (2, 2, 4, FALSE, 'Piese comandate', 'Nu evacueaza apa', 'Fara accesorii suplimentare');

INSERT INTO garantie_producator (
    id_bon, data_achizitiei, loc_achizitie, nr_factura, nr_certificat_garantie, nr_fisa
) VALUES
    (1, '2025-05-10', 'Altex', 'FAC-2025-1001', 'CG-5521', 'FS-001');

INSERT INTO detalii_bosch_siemens_neff (
    id_garantie, denumire, e_nr, fd, z_nr
) VALUES
    (1, 'Cuptor incorporabil Bosch', 'HBG5780S6/01', '0505', '00120');

INSERT INTO aparat_post_garantie (
    id_bon, denumire_aparat, accesorii
) VALUES
    (2, 'Masina de spalat rufe', 'Furtun alimentare');