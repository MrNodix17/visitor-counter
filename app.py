import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template_string
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/visitordb")

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL PRIMARY KEY,
                    visited_at TIMESTAMP DEFAULT NOW()
                )
            """)
            conn.commit()
            logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Init DB error: {e}")
        conn.rollback()
    finally:
        conn.close()

def record_visit():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO visits (visited_at) VALUES (NOW()) RETURNING id")
            result = cur.fetchone()
            conn.commit()
            return result["id"]
    except Exception as e:
        logger.error(f"Record visit error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_visit_count():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM visits")
            return conn.cursor().fetchone()["total"] if False else cur.fetchone()["total"]
    except Exception as e:
        logger.error(f"Get count error: {e}")
        return 0
    finally:
        conn.close()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pl" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visitor Counter</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Work+Sans:wght@300..700&display=swap" rel="stylesheet">
    <style>
        :root,[data-theme="light"]{--bg:#f7f6f2;--surface:#f9f8f5;--surface2:#fbfbf9;--offset:#f3f0ec;--divider:#dcd9d5;--border:#d4d1ca;--text:#28251d;--muted:#7a7974;--faint:#bab9b4;--primary:#01696f;--primary-h:#0c4e54;--primary-hl:#cedcd8;--shadow-sm:0 1px 2px oklch(0.2 0.01 80/0.06);--shadow-md:0 4px 12px oklch(0.2 0.01 80/0.08);--shadow-lg:0 12px 32px oklch(0.2 0.01 80/0.12)}
        [data-theme="dark"]{--bg:#171614;--surface:#1c1b19;--surface2:#201f1d;--offset:#1d1c1a;--divider:#262523;--border:#393836;--text:#cdccca;--muted:#797876;--faint:#5a5957;--primary:#4f98a3;--primary-h:#227f8b;--primary-hl:#313b3b;--shadow-sm:0 1px 2px oklch(0 0 0/0.2);--shadow-md:0 4px 12px oklch(0 0 0/0.3);--shadow-lg:0 12px 32px oklch(0 0 0/0.4)}
        @media(prefers-color-scheme:dark){:root:not([data-theme]){--bg:#171614;--surface:#1c1b19;--surface2:#201f1d;--offset:#1d1c1a;--divider:#262523;--border:#393836;--text:#cdccca;--muted:#797876;--faint:#5a5957;--primary:#4f98a3;--primary-h:#227f8b;--primary-hl:#313b3b}}
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
        html{-webkit-font-smoothing:antialiased;scroll-behavior:smooth}
        body{min-height:100dvh;font-family:'Work Sans','Helvetica Neue',sans-serif;font-size:clamp(1rem,.95rem + .25vw,1.125rem);color:var(--text);background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center}
        header{position:fixed;top:0;left:0;right:0;display:flex;justify-content:space-between;align-items:center;padding:1rem 2rem;background:color-mix(in oklch,var(--bg) 80%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid oklch(from var(--text) l c h/.08);z-index:100}
        .logo{display:flex;align-items:center;gap:.5rem;font-family:'Instrument Serif',Georgia,serif;font-size:clamp(1.125rem,1rem + .75vw,1.5rem);color:var(--text);text-decoration:none}
        .logo svg{color:var(--primary)}
        .theme-btn{padding:.5rem;border-radius:.5rem;color:var(--muted);background:none;border:none;cursor:pointer;transition:color 180ms cubic-bezier(.16,1,.3,1),background 180ms cubic-bezier(.16,1,.3,1)}
        .theme-btn:hover{color:var(--text);background:var(--offset)}
        main{text-align:center;padding:6rem 2rem 2rem;max-width:600px;width:100%}
        .badge{display:inline-flex;align-items:center;gap:.25rem;padding:.25rem .75rem;background:var(--primary-hl);color:var(--primary);border-radius:9999px;font-size:clamp(.75rem,.7rem + .25vw,.875rem);font-weight:500;margin-bottom:1.5rem}
        .badge-dot{width:8px;height:8px;border-radius:50%;background:var(--primary);animation:pulse 2s ease-in-out infinite}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
        .card{background:var(--surface);border:1px solid oklch(from var(--text) l c h/.08);border-radius:1rem;padding:3rem 2rem;box-shadow:var(--shadow-lg)}
        .number{font-family:'Instrument Serif',Georgia,serif;font-size:clamp(2rem,1.2rem + 2.5vw,3.5rem);font-style:italic;color:var(--primary);line-height:1;margin-bottom:1rem;animation:fadeUp .6s cubic-bezier(.16,1,.3,1)}
        @keyframes fadeUp{from{opacity:0;transform:translateY(16px) scale(.95)}to{opacity:1;transform:none}}
        h1{font-family:'Instrument Serif',Georgia,serif;font-size:clamp(1.5rem,1.2rem + 1.25vw,2.25rem);line-height:1.2;color:var(--text);margin-bottom:.5rem}
        .sub{color:var(--muted);margin-bottom:2rem;font-size:clamp(1rem,.95rem + .25vw,1.125rem)}
        hr{border:none;border-top:1px solid var(--divider);margin:1.5rem 0}
        .stats{display:flex;justify-content:center;gap:3rem;flex-wrap:wrap}
        .stat-label{font-size:clamp(.75rem,.7rem + .25vw,.875rem);color:var(--faint);text-transform:uppercase;letter-spacing:.08em}
        .stat-value{font-size:clamp(1.125rem,1rem + .75vw,1.5rem);font-weight:600;color:var(--muted);margin-top:.25rem}
        footer{position:fixed;bottom:0;left:0;right:0;text-align:center;padding:.75rem;font-size:clamp(.75rem,.7rem + .25vw,.875rem);color:var(--faint);border-top:1px solid var(--divider);background:var(--bg)}
        @media(max-width:480px){.card{padding:2rem 1.25rem}.stats{gap:1.5rem}}
    </style>
</head>
<body>
<header>
  <a href="/" class="logo">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
    Visitor Counter
  </a>
  <button class="theme-btn" data-theme-toggle aria-label="Przełącz motyw">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
  </button>
</header>

<main>
  <div class="badge">
    <span class="badge-dot" aria-hidden="true"></span>
    Licznik na żywo
  </div>
  <div class="card">
    <div class="number" aria-label="Numer wizyty: {{ visit_number }}">{{ visit_number }}</div>
    <h1>Cześć! Jesteś <em>{{ visit_number }}.</em> osobą&nbsp;odwiedzającą tę stronę.</h1>
    <p class="sub">Twoja wizyta została zapisana w bazie danych PostgreSQL.</p>
    <hr>
    <div class="stats">
      <div>
        <div class="stat-label">Łączna liczba wizyt</div>
        <div class="stat-value">{{ total_visits }}</div>
      </div>
      <div>
        <div class="stat-label">ID tej wizyty</div>
        <div class="stat-value">#{{ visit_id }}</div>
      </div>
    </div>
  </div>
</main>

<footer>Flask · PostgreSQL · Docker · Coolify</footer>

<script>
(function(){
  const t=document.querySelector('[data-theme-toggle]'),r=document.documentElement;
  let d=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';
  r.setAttribute('data-theme',d);
  const sun='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
  const moon='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  t.innerHTML=d==='dark'?sun:moon;
  t.addEventListener('click',()=>{d=d==='dark'?'light':'dark';r.setAttribute('data-theme',d);t.setAttribute('aria-label','Przełącz motyw');t.innerHTML=d==='dark'?sun:moon});
})();
</script>
</body>
</html>"""

@app.route("/", methods=["GET"])
def index():
    visit_id = record_visit()
    total_visits = get_visit_count()
    return render_template_string(
        HTML_TEMPLATE,
        visit_number=total_visits,
        visit_id=visit_id or "–",
        total_visits=total_visits,
    )

@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db()
        conn.close()
        return {"status": "ok", "db": "connected"}, 200
    except Exception as e:
        return {"status": "error", "db": str(e)}, 500

with app.app_context():
    init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
