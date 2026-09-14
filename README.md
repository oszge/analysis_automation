# Sales Intelligence dashboard

## Node-RED automatizálás

A napi riport minden nap 08:00-kor fut, budapesti idő szerint, ha a gép ébren van
és a Node-RED fut. Node-RED és Streamlit bejelentkezéskor elindul.
Szerkesztő: http://127.0.0.1:1880. Részletek: [node_red/README.md](node_red/README.md).

A meglévő elemzési projekt Streamlit felülete. A dashboard csak adatot olvas:
nem importálja a `data_manipulation.py` fájlt, nem ír az adatbázisba és nem hív AI API-t.

## Indítás

A projekt könyvtárában, az aktivált Python-környezetben:

```powershell
python -m pip install -r requirements-dashboard.txt
python -m streamlit run streamlit_app.py
```

A felület a http://localhost:8501 címen érhető el. Az alapértelmezett forrás Neon
PostgreSQL, a meglévő `.env` `DATABASE_URL` beállításával. Helyi kipróbáláshoz
válaszd az oldalsávban a **CSV** opciót: ez a projekt `sales_data` fájlját olvassa.
Adatbázishiba esetén nincs automatikus átváltás más adatokra.

## Nézetek

- Áttekintés: időszak-, ország- és kategóriaszűrők, KPI-k, napi/heti/havi bevétel,
  kategóriák, országok, termékek, tranzakciók és szűrt CSV letöltése.
- Összehasonlítás: a kiválasztott záródátumig tartó 7 nap és a megelőző 7 nap,
  vagy a záródátum hónapja és a teljes előző hónap. A kezdődátum nem korlátozza
  az összehasonlítást. A havi logika megegyezik a meglévő Python-riportéval;
  részleges hónapnál a felület figyelmeztet. Nulla bázisnál nincs százalék.
- AI-értékelés: a korábbi `ai_response.json` és Markdown-riport. Ezek nem a
  szűrt nézethez tartoznak; forrásadat-egyezésük a jelenlegi fájlokból nem igazolható.

A teljes adatforrás pénzneme EUR (euró). A bevételek és abszolút pénzügyi változások euróban értendők; átváltás nem történik. A CSV-export currency oszlopa EUR. A tranzakciószám a sorok száma, ahogy a
meglévő elemzésben. Az adatgyorsítótár 5 percig érvényes; új adatot a következő
felületi művelet vagy az **Adatok újratöltése** gomb tölt be. Ez még nem időzített
háttérfeldolgozás. A Node-RED ütemezés és az AI-értékelés adatverzióhoz kötése
a következő fejlesztési lépés.

API- és tesztreferencia: https://docs.streamlit.io/develop/api-reference
