from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'cun-devsecops-2026'

# ── USUARIOS ──────────────────────────────────────
admins = {
    "admin@cun.edu.co": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "nombre": "Hugo Mantilla",
        "rol": "Docente"
    }
}

usuarios = {
    "estudiante@cun.edu.co": {
        "password": hashlib.sha256("123456".encode()).hexdigest(),
        "nombre": "Wilmer Molano",
        "carrera": "Ingeniería de Sistemas",
        "semestre": 6,
        "materias": ["Programación Avanzada", "Base de Datos", "Redes", "Algoritmos"]
    },
    "nicolas@cun.edu.co": {
        "password": hashlib.sha256("123456".encode()).hexdigest(),
        "nombre": "Nicolás Fonseca",
        "carrera": "Ingeniería de Sistemas",
        "semestre": 6,
        "materias": ["Programación Avanzada", "Base de Datos", "Seguridad Informática"]
    }
}

notas = {
    "estudiante@cun.edu.co": [
        {"materia": "Programación Avanzada", "corte1": 4.2, "corte2": 3.8, "corte3": None},
        {"materia": "Base de Datos", "corte1": 3.5, "corte2": 4.0, "corte3": None},
        {"materia": "Redes", "corte1": 4.5, "corte2": 4.3, "corte3": None},
        {"materia": "Algoritmos", "corte1": 3.9, "corte2": None, "corte3": None},
    ],
    "nicolas@cun.edu.co": [
        {"materia": "Programación Avanzada", "corte1": 4.0, "corte2": 4.5, "corte3": None},
        {"materia": "Base de Datos", "corte1": 3.8, "corte2": 3.6, "corte3": None},
        {"materia": "Seguridad Informática", "corte1": 4.7, "corte2": 4.8, "corte3": None},
    ]
}

horarios = [
    {"dia": "Lunes", "hora": "07:00 - 09:00", "materia": "Programación Avanzada", "salon": "202", "profesor": "Hugo Mantilla"},
    {"dia": "Lunes", "hora": "09:00 - 11:00", "materia": "Base de Datos", "salon": "105", "profesor": "Carlos Ruiz"},
    {"dia": "Martes", "hora": "14:00 - 16:00", "materia": "Redes", "salon": "Lab 3", "profesor": "Ana Torres"},
    {"dia": "Miércoles", "hora": "07:00 - 09:00", "materia": "Algoritmos", "salon": "301", "profesor": "Pedro Gómez"},
    {"dia": "Jueves", "hora": "11:00 - 13:00", "materia": "Programación Avanzada", "salon": "202", "profesor": "Hugo Mantilla"},
    {"dia": "Viernes", "hora": "09:00 - 11:00", "materia": "Base de Datos", "salon": "105", "profesor": "Carlos Ruiz"},
]

noticias = [
    {"titulo": "Semana de Innovación CUN 2026", "fecha": "2026-05-10", "categoria": "Evento", "descripcion": "Participa en la semana de innovación tecnológica con talleres de IA, ciberseguridad y DevOps."},
    {"titulo": "Convocatoria Monitores Académicos", "fecha": "2026-05-05", "categoria": "Académico", "descripcion": "Abre convocatoria para monitores en las materias de Programación y Base de Datos. Aplica antes del 20 de mayo."},
    {"titulo": "Taller DevSecOps gratuito", "fecha": "2026-05-03", "categoria": "Capacitación", "descripcion": "El programa de Ingeniería ofrece taller gratuito de DevSecOps con certificado. Cupos limitados."},
    {"titulo": "Actualización pensum Ingeniería de Sistemas", "fecha": "2026-04-28", "categoria": "Académico", "descripcion": "Se actualiza el pensum con nuevas materias de Cloud Computing y Ciberseguridad para el próximo semestre."},
]

# ── HELPERS ───────────────────────────────────────
def calcular_promedio(notas_materia):
    valores = [n for n in [notas_materia["corte1"], notas_materia["corte2"], notas_materia["corte3"]] if n is not None]
    if not valores:
        return None
    return round(sum(valores) / len(valores), 1)

def es_admin():
    return session.get('rol') == 'admin'

# ── RUTAS COMUNES ─────────────────────────────────
@app.route('/')
def index():
    if 'usuario' in session:
        if es_admin():
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    hashed = hashlib.sha256(password.encode()).hexdigest()

    if email in admins and admins[email]['password'] == hashed:
        session['usuario'] = email
        session['nombre'] = admins[email]['nombre']
        session['rol'] = 'admin'
        flash('Bienvenido, ' + admins[email]['nombre'], 'success')
        return redirect(url_for('admin_dashboard'))
    elif email in usuarios and usuarios[email]['password'] == hashed:
        session['usuario'] = email
        session['nombre'] = usuarios[email]['nombre']
        session['rol'] = 'estudiante'
        flash('¡Bienvenido de vuelta!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Credenciales incorrectas. Intenta de nuevo.', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── RUTAS ESTUDIANTE ──────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session or es_admin():
        return redirect(url_for('index'))
    usuario = session['usuario']
    info = usuarios[usuario]
    mis_notas = notas.get(usuario, [])
    promedios = [calcular_promedio(n) for n in mis_notas if calcular_promedio(n) is not None]
    promedio_general = round(sum(promedios) / len(promedios), 2) if promedios else 0
    return render_template('dashboard.html',
                           info=info, notas=mis_notas,
                           horarios=horarios[:3], noticias=noticias[:2],
                           promedio_general=promedio_general,
                           calcular_promedio=calcular_promedio,
                           fecha_hoy=datetime.now().strftime("%d de %B, %Y"))

@app.route('/notas')
def ver_notas():
    if 'usuario' not in session or es_admin():
        return redirect(url_for('index'))
    usuario = session['usuario']
    mis_notas = notas.get(usuario, [])
    promedios = [(n, calcular_promedio(n)) for n in mis_notas]
    return render_template('notas.html', notas_data=promedios, calcular_promedio=calcular_promedio)

@app.route('/horario')
def ver_horario():
    if 'usuario' not in session or es_admin():
        return redirect(url_for('index'))
    return render_template('horario.html', horarios=horarios)

@app.route('/noticias')
def ver_noticias():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    return render_template('noticias.html', noticias=noticias)

@app.route('/perfil')
def perfil():
    if 'usuario' not in session or es_admin():
        return redirect(url_for('index'))
    usuario = session['usuario']
    info = usuarios[usuario]
    return render_template('perfil.html', info=info, email=usuario)

# ── RUTAS ADMIN ───────────────────────────────────
@app.route('/admin')
def admin_dashboard():
    if not es_admin():
        return redirect(url_for('index'))
    # Calcular promedios de todos los estudiantes
    resumen = []
    for email, info in usuarios.items():
        mis_notas = notas.get(email, [])
        promedios = [calcular_promedio(n) for n in mis_notas if calcular_promedio(n) is not None]
        prom = round(sum(promedios) / len(promedios), 2) if promedios else 0
        resumen.append({"email": email, "nombre": info["nombre"], "carrera": info["carrera"], "promedio": prom, "materias": len(mis_notas)})
    return render_template('admin_dashboard.html', resumen=resumen, total=len(usuarios))

@app.route('/admin/estudiante/<email>')
def admin_ver_estudiante(email):
    if not es_admin():
        return redirect(url_for('index'))
    if email not in usuarios:
        flash('Estudiante no encontrado.', 'error')
        return redirect(url_for('admin_dashboard'))
    info = usuarios[email]
    mis_notas = notas.get(email, [])
    promedios = [(n, calcular_promedio(n)) for n in mis_notas]
    return render_template('admin_estudiante.html', info=info, email=email, notas_data=promedios)

@app.route('/admin/editar_nota', methods=['POST'])
def admin_editar_nota():
    if not es_admin():
        return redirect(url_for('index'))
    email = request.form.get('email')
    materia = request.form.get('materia')
    corte = request.form.get('corte')
    valor = request.form.get('valor')

    if email in notas:
        for n in notas[email]:
            if n['materia'] == materia:
                try:
                    val = float(valor)
                    if 1.0 <= val <= 5.0:
                        n[corte] = val
                        flash(f'Nota actualizada: {materia} — {corte} = {val}', 'success')
                    else:
                        flash('La nota debe estar entre 1.0 y 5.0', 'error')
                except:
                    n[corte] = None
                    flash(f'Nota eliminada: {materia} — {corte}', 'success')
                break

    return redirect(url_for('admin_ver_estudiante', email=email))

@app.route('/api/notas')
def api_notas():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    usuario = session['usuario']
    mis_notas = notas.get(usuario, [])
    return jsonify(mis_notas)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
