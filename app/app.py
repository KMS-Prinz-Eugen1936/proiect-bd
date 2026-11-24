import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "service_db"),
        user=os.getenv("DB_USER", "service_user"),
        password=os.getenv("DB_PASSWORD", "service_password"),
    )


@app.route("/")
@app.route("/index.html")
def index():
    return render_template("index.html")


@app.route("/formular")
@app.route("/formular.html")
def formular():
    return render_template("formular.html")


@app.get("/api/tehnicieni")
def get_tehnicieni():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id_utilizator AS id, nume FROM utilizator WHERE rol = 'Tehnician' ORDER BY id_utilizator"
            )
            return jsonify(cur.fetchall())


@app.get("/api/bonuri")
def get_bonuri():
    sql = """
        SELECT
            b.id_bon,
            c.nume AS nume_client,
            c.telefon AS telefon_client,
            c.adresa AS adresa_client,
            b.este_in_garantie,
            b.data_intrarii,
            b.status,
            b.defect,
            b.reparatie_efectuata,
            b.observatii,
            b.id_tehnician,
            u.nume AS nume_tehnician,
            COALESCE(
                apg.denumire_aparat,
                bsn.denumire,
                elx.denumire,
                mie.denumire,
                tek.denumire,
                sam.denumire,
                '-'
            ) AS denumire_aparat,
            CASE
                WHEN NOT b.este_in_garantie THEN NULL
                WHEN bsn.id_detaliu IS NOT NULL THEN 'Bosch'
                WHEN elx.id_detaliu IS NOT NULL THEN 'Electrolux / AEG'
                WHEN mie.id_detaliu IS NOT NULL THEN 'Miele'
                WHEN tek.id_detaliu IS NOT NULL THEN 'Teka'
                WHEN sam.id_detaliu IS NOT NULL THEN 'Samus / Albatros'
                ELSE 'Producator'
            END AS brand
        FROM bon_reparatie b
        JOIN client c ON c.id_client = b.id_client
        LEFT JOIN utilizator u ON u.id_utilizator = b.id_tehnician
        LEFT JOIN aparat_post_garantie apg ON apg.id_bon = b.id_bon
        LEFT JOIN garantie_producator gp ON gp.id_bon = b.id_bon
        LEFT JOIN detalii_bosch_siemens_neff bsn ON bsn.id_garantie = gp.id_garantie
        LEFT JOIN detalii_electrolux_aeg elx ON elx.id_garantie = gp.id_garantie
        LEFT JOIN detalii_miele mie ON mie.id_garantie = gp.id_garantie
        LEFT JOIN detalii_teka tek ON tek.id_garantie = gp.id_garantie
        LEFT JOIN detalii_samus_albatros sam ON sam.id_garantie = gp.id_garantie
        ORDER BY b.id_bon DESC
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            for r in rows:
                if r.get("data_intrarii"):
                    r["data_intrarii"] = r["data_intrarii"].isoformat()
            return jsonify(rows)


@app.post("/api/bonuri")
def create_bon():
    data = request.get_json(force=True) or {}
    client_data = data.get("client") or {}
    bon_data = data.get("bon") or {}

    nume = (client_data.get("nume") or "").strip()
    telefon = (client_data.get("telefon") or "").strip()
    adresa = (client_data.get("adresa") or "").strip() or None
    defect = (bon_data.get("defect") or "").strip()
    observatii = (bon_data.get("observatii") or "").strip() or None
    este_in_garantie = bool(bon_data.get("este_in_garantie", False))
    id_tehnician = bon_data.get("id_tehnician") or None

    if not nume or not telefon or not defect:
        return jsonify({"error": "Numele clientului, telefonul și defectul sunt obligatorii."}), 400

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO client (nume, adresa, telefon)
                VALUES (%s, %s, %s)
                ON CONFLICT (telefon) DO UPDATE
                    SET nume = EXCLUDED.nume,
                        adresa = COALESCE(EXCLUDED.adresa, client.adresa)
                RETURNING id_client
                """,
                (nume, adresa, telefon),
            )
            id_client = cur.fetchone()["id_client"]

            cur.execute(
                """
                INSERT INTO bon_reparatie (
                    id_client, id_tehnician, este_in_garantie, status, defect, observatii
                )
                VALUES (%s, %s, %s, 'Introdus in sistem', %s, %s)
                RETURNING id_bon
                """,
                (id_client, id_tehnician, este_in_garantie, defect, observatii),
            )
            id_bon = cur.fetchone()["id_bon"]

            if not este_in_garantie:
                pg = data.get("post_garantie") or {}
                denumire_aparat = (pg.get("denumire_aparat") or "").strip()
                if not denumire_aparat:
                    conn.rollback()
                    return jsonify({"error": "Denumirea aparatului post-garanție este obligatorie."}), 400
                cur.execute(
                    """
                    INSERT INTO aparat_post_garantie (id_bon, denumire_aparat, accesorii)
                    VALUES (%s, %s, %s)
                    """,
                    (id_bon, denumire_aparat, pg.get("accesorii")),
                )
            else:
                gp = data.get("garantie") or {}
                det = data.get("detalii_brand") or {}
                brand_grup = (gp.get("brand_grup") or "bosch").strip().lower()

                cur.execute(
                    """
                    INSERT INTO garantie_producator (
                        id_bon, data_achizitiei, loc_achizitie, nr_factura, nr_certificat_garantie, nr_fisa
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_garantie
                    """,
                    (
                        id_bon,
                        gp.get("data_achizitiei"),
                        gp.get("loc_achizitie"),
                        gp.get("nr_factura"),
                        gp.get("nr_certificat_garantie"),
                        gp.get("nr_fisa"),
                    ),
                )
                id_garantie = cur.fetchone()["id_garantie"]

                if brand_grup in ("bosch", "siemens", "neff"):
                    cur.execute(
                        """
                        INSERT INTO detalii_bosch_siemens_neff (id_garantie, denumire, e_nr, fd, z_nr)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (id_garantie, det.get("denumire"), det.get("e_nr"), det.get("fd"), det.get("z_nr")),
                    )
                elif brand_grup in ("electrolux", "aeg"):
                    cur.execute(
                        """
                        INSERT INTO detalii_electrolux_aeg (id_garantie, denumire, model, pnc)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (id_garantie, det.get("denumire"), det.get("model"), det.get("pnc")),
                    )
                elif brand_grup == "miele":
                    cur.execute(
                        """
                        INSERT INTO detalii_miele (id_garantie, denumire, campuri_specifice)
                        VALUES (%s, %s, %s)
                        """,
                        (id_garantie, det.get("denumire"), det.get("campuri_specifice")),
                    )
                elif brand_grup == "teka":
                    cur.execute(
                        """
                        INSERT INTO detalii_teka (id_garantie, denumire, campuri_specifice)
                        VALUES (%s, %s, %s)
                        """,
                        (id_garantie, det.get("denumire"), det.get("campuri_specifice")),
                    )
                elif brand_grup in ("samus", "albatros"):
                    cur.execute(
                        """
                        INSERT INTO detalii_samus_albatros (id_garantie, denumire, campuri_specifice)
                        VALUES (%s, %s, %s)
                        """,
                        (id_garantie, det.get("denumire"), det.get("campuri_specifice")),
                    )

        conn.commit()
    return jsonify({"id_bon": id_bon}), 201


@app.put("/api/bonuri/<int:id_bon>")
def update_bon_status(id_bon):
    data = request.get_json(force=True) or {}
    status = (data.get("status") or "").strip()
    if not status:
        return jsonify({"error": "Statusul este obligatoriu."}), 400

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "UPDATE bon_reparatie SET status = %s WHERE id_bon = %s RETURNING id_bon, status",
                (status, id_bon),
            )
            updated = cur.fetchone()
        conn.commit()

    if not updated:
        return jsonify({"error": "Bonul nu a fost găsit."}), 404
    return jsonify(updated)


@app.delete("/api/bonuri/<int:id_bon>")
def delete_bon(id_bon):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM bon_reparatie WHERE id_bon = %s", (id_bon,))
            deleted = cur.rowcount
        conn.commit()

    if deleted == 0:
        return jsonify({"error": "Bonul nu a fost găsit."}), 404
    return jsonify({"deleted": True})


@app.get("/api/piese")
def get_piese():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id_piesa, cod_piesa, denumire, brand_compatibil,
                       pret_unitar::float AS pret_unitar, stoc_disponibil
                FROM piesa
                ORDER BY id_piesa DESC
                """
            )
            return jsonify(cur.fetchall())


@app.post("/api/piese")
def add_piesa():
    data = request.get_json(force=True) or {}
    cod_piesa = (data.get("cod_piesa") or "").strip()
    denumire = (data.get("denumire") or "").strip()
    brand_compatibil = (data.get("brand_compatibil") or "").strip()
    pret_unitar = data.get("pret_unitar")
    stoc_disponibil = data.get("stoc_disponibil")

    if not cod_piesa or not denumire or pret_unitar is None or stoc_disponibil is None:
        return jsonify({"error": "Completează toate câmpurile obligatorii ale piesei."}), 400

    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO piesa (cod_piesa, denumire, brand_compatibil, pret_unitar, stoc_disponibil)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_piesa, cod_piesa, denumire, brand_compatibil,
                              pret_unitar::float AS pret_unitar, stoc_disponibil
                    """,
                    (cod_piesa, denumire, brand_compatibil, pret_unitar, int(stoc_disponibil)),
                )
                piesa = cur.fetchone()
            conn.commit()
        return jsonify(piesa), 201
    except psycopg2.IntegrityError:
        return jsonify({"error": "Există deja o piesă cu acest cod."}), 409


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)