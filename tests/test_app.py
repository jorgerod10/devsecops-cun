import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app

@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test'
    with app.test_client() as cliente:
        yield cliente

def test_login_page_carga(cliente):
    """La página de login debe cargar correctamente"""
    respuesta = cliente.get('/')
    assert respuesta.status_code == 200

def test_login_credenciales_incorrectas(cliente):
    """Login con credenciales incorrectas debe redirigir"""
    respuesta = cliente.post('/login', data={
        'email': 'falso@cun.edu.co',
        'password': 'wrongpassword'
    })
    assert respuesta.status_code == 302

def test_login_credenciales_correctas(cliente):
    """Login con credenciales correctas debe redirigir al dashboard"""
    respuesta = cliente.post('/login', data={
        'email': 'estudiante@cun.edu.co',
        'password': '123456'
    }, follow_redirects=True)
    assert respuesta.status_code == 200

def test_dashboard_sin_login_redirige(cliente):
    """El dashboard sin sesión debe redirigir al login"""
    respuesta = cliente.get('/dashboard')
    assert respuesta.status_code == 302

def test_notas_sin_login_redirige(cliente):
    """Las notas sin sesión deben redirigir al login"""
    respuesta = cliente.get('/notas')
    assert respuesta.status_code == 302

def test_logout(cliente):
    """El logout debe redirigir al login"""
    respuesta = cliente.get('/logout')
    assert respuesta.status_code == 302
