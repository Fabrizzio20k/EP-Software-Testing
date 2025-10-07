from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from main import app, libros_db, copias_db, lectores_db, prestamos_db, bio_alert, inicializar_datos
from src.models import EstadoCopia, Autor, Libro, Copia, Lector

client = TestClient(app)


def setup_function():
    libros_db.clear()
    copias_db.clear()
    lectores_db.clear()
    prestamos_db.clear()
    bio_alert.suscripciones.clear()
    inicializar_datos()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "mensaje": "API Sistema de Biblioteca", "version": "1.0.0"}


def test_crear_libro():
    libro_data = {
        "id": "libro_test",
        "nombre": "Test Book",
        "anio": 2024,
        "autor": {
            "nombre": "Test Author",
            "fecha_nacimiento": "1980-01-01T00:00:00"
        }
    }
    response = client.post("/libros/", json=libro_data)
    assert response.status_code == 201
    assert response.json()["id"] == "libro_test"


def test_crear_libro_duplicado():
    libro_data = {
        "id": "libro_se_somerville",
        "nombre": "Software Engineering",
        "anio": 2015,
        "autor": {
            "nombre": "Ian Somerville",
            "fecha_nacimiento": "1951-02-23T00:00:00"
        }
    }
    response = client.post("/libros/", json=libro_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "El libro ya existe"


def test_listar_libros():
    response = client.get("/libros/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_obtener_libro():
    response = client.get("/libros/libro_se_somerville")
    assert response.status_code == 200
    assert response.json()["id"] == "libro_se_somerville"


def test_obtener_libro_no_encontrado():
    response = client.get("/libros/libro_inexistente")
    assert response.status_code == 404
    assert response.json()["detail"] == "Libro no encontrado"


def test_buscar_libros_por_autor():
    response = client.get("/libros/autor/Somerville")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_buscar_libros_por_autor_sin_resultados():
    response = client.get("/libros/autor/AutorInexistente")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_crear_copia():
    copia_data = {
        "id": "copia_test",
        "libro_id": "libro_se_somerville",
        "estado": "disponible",
        "edicion": "10th",
        "idioma": "ingles"
    }
    response = client.post("/copias/", json=copia_data)
    assert response.status_code == 201
    assert response.json()["id"] == "copia_test"


def test_crear_copia_duplicada():
    copia_data = {
        "id": "copia1",
        "libro_id": "libro_se_somerville",
        "estado": "disponible",
        "edicion": "8th",
        "idioma": "ingles"
    }
    response = client.post("/copias/", json=copia_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "La copia ya existe"


def test_crear_copia_libro_no_encontrado():
    copia_data = {
        "id": "copia_error",
        "libro_id": "libro_inexistente",
        "estado": "disponible",
        "edicion": "1st",
        "idioma": "ingles"
    }
    response = client.post("/copias/", json=copia_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Libro no encontrado"


def test_listar_copias():
    response = client.get("/copias/")
    assert response.status_code == 200
    assert len(response.json()) >= 3


def test_obtener_copias_libro():
    response = client.get("/copias/libro/libro_se_somerville")
    assert response.status_code == 200
    assert len(response.json()) >= 3


def test_obtener_copias_libro_no_encontrado():
    response = client.get("/copias/libro/libro_inexistente")
    assert response.status_code == 404
    assert response.json()["detail"] == "Libro no encontrado"


def test_obtener_copia():
    response = client.get("/copias/copia1")
    assert response.status_code == 200
    assert response.json()["id"] == "copia1"


def test_obtener_copia_no_encontrada():
    response = client.get("/copias/copia_inexistente")
    assert response.status_code == 404
    assert response.json()["detail"] == "Copia no encontrada"


def test_actualizar_estado_copia():
    response = client.put("/copias/copia1/estado?estado=en_reparacion")
    assert response.status_code == 200
    assert response.json()["estado"] == "en_reparacion"


def test_actualizar_estado_copia_no_encontrada():
    response = client.put("/copias/copia_inexistente/estado?estado=disponible")
    assert response.status_code == 404
    assert response.json()["detail"] == "Copia no encontrada"


def test_crear_lector():
    lector_data = {
        "email": "test@universidad.edu",
        "nombre": "Test User",
        "prestamos_activos": [],
        "dias_suspension": 0
    }
    response = client.post("/lectores/", json=lector_data)
    assert response.status_code == 201
    assert response.json()["email"] == "test@universidad.edu"


def test_crear_lector_duplicado():
    lector_data = {
        "email": "test@universidad.edu",
        "nombre": "Test User",
        "prestamos_activos": [],
        "dias_suspension": 0
    }
    client.post("/lectores/", json=lector_data)
    response = client.post("/lectores/", json=lector_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "El lector ya existe"


def test_listar_lectores():
    lector_data = {
        "email": "test@universidad.edu",
        "nombre": "Test User"
    }
    client.post("/lectores/", json=lector_data)
    response = client.get("/lectores/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_obtener_lector():
    lector_data = {
        "email": "test@universidad.edu",
        "nombre": "Test User"
    }
    client.post("/lectores/", json=lector_data)
    response = client.get("/lectores/test@universidad.edu")
    assert response.status_code == 200
    assert response.json()["email"] == "test@universidad.edu"


def test_obtener_lector_no_encontrado():
    response = client.get("/lectores/inexistente@universidad.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Lector no encontrado"


def test_crear_prestamo():
    lector_data = {
        "email": "prestamo@universidad.edu",
        "nombre": "Test Prestamo"
    }
    client.post("/lectores/", json=lector_data)
    response = client.post(
        "/prestamos/?copia_id=copia1&lector_email=prestamo@universidad.edu")
    assert response.status_code == 201
    assert response.json()["copia_id"] == "copia1"
    assert response.json()["lector_email"] == "prestamo@universidad.edu"


def test_crear_prestamo_copia_no_encontrada():
    lector_data = {
        "email": "prestamo2@universidad.edu",
        "nombre": "Test Prestamo 2"
    }
    client.post("/lectores/", json=lector_data)
    response = client.post(
        "/prestamos/?copia_id=copia_inexistente&lector_email=prestamo2@universidad.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Copia no encontrada"


def test_crear_prestamo_lector_no_encontrado():
    response = client.post(
        "/prestamos/?copia_id=copia1&lector_email=inexistente@universidad.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Lector no encontrado"


def test_crear_prestamo_copia_no_disponible():
    lector_data = {
        "email": "prestamo3@universidad.edu",
        "nombre": "Test Prestamo 3"
    }
    client.post("/lectores/", json=lector_data)
    client.post(
        "/prestamos/?copia_id=copia2&lector_email=prestamo3@universidad.edu")
    response = client.post(
        "/prestamos/?copia_id=copia2&lector_email=prestamo3@universidad.edu")
    assert response.status_code == 400
    assert "La copia no está disponible" in response.json()["detail"]


def test_crear_prestamo_maximo_prestamos():
    lector_data = {
        "email": "prestamo4@universidad.edu",
        "nombre": "Test Prestamo 4"
    }
    client.post("/lectores/", json=lector_data)

    client.put("/copias/copia1/estado?estado=disponible")
    client.put("/copias/copia2/estado?estado=disponible")
    client.put("/copias/copia3/estado?estado=disponible")

    copia_extra = {
        "id": "copia_extra",
        "libro_id": "libro_se_somerville",
        "estado": "disponible",
        "edicion": "10th",
        "idioma": "ingles"
    }
    client.post("/copias/", json=copia_extra)

    client.post(
        "/prestamos/?copia_id=copia1&lector_email=prestamo4@universidad.edu")
    client.post(
        "/prestamos/?copia_id=copia2&lector_email=prestamo4@universidad.edu")
    client.post(
        "/prestamos/?copia_id=copia3&lector_email=prestamo4@universidad.edu")

    response = client.post(
        "/prestamos/?copia_id=copia_extra&lector_email=prestamo4@universidad.edu")
    assert response.status_code == 400
    assert response.json()[
        "detail"] == "El lector ya tiene 3 préstamos activos"


def test_crear_prestamo_lector_suspendido():
    lector_data = {
        "email": "suspendido@universidad.edu",
        "nombre": "Test Suspendido",
        "dias_suspension": 5,
        "fecha_fin_suspension": (datetime.now() + timedelta(days=5)).isoformat()
    }
    client.post("/lectores/", json=lector_data)

    client.put("/copias/copia1/estado?estado=disponible")

    response = client.post(
        "/prestamos/?copia_id=copia1&lector_email=suspendido@universidad.edu")
    assert response.status_code == 400
    assert "Lector suspendido hasta" in response.json()["detail"]


def test_crear_prestamo_suspension_expirada():
    lector_data = {
        "email": "suspension_expirada@universidad.edu",
        "nombre": "Test Suspension Expirada",
        "dias_suspension": 5,
        "fecha_fin_suspension": (datetime.now() - timedelta(days=1)).isoformat()
    }
    client.post("/lectores/", json=lector_data)

    client.put("/copias/copia1/estado?estado=disponible")

    response = client.post(
        "/prestamos/?copia_id=copia1&lector_email=suspension_expirada@universidad.edu")
    assert response.status_code == 201


def test_devolver_prestamo_sin_retraso():
    lector_data = {
        "email": "devolucion@universidad.edu",
        "nombre": "Test Devolucion"
    }
    client.post("/lectores/", json=lector_data)

    client.put("/copias/copia1/estado?estado=disponible")

    prestamo_response = client.post(
        "/prestamos/?copia_id=copia1&lector_email=devolucion@universidad.edu")
    prestamo_id = prestamo_response.json()["id"]

    response = client.put(f"/prestamos/{prestamo_id}/devolver")
    assert response.status_code == 200
    assert response.json()["multa_dias"] == 0


def test_devolver_prestamo_con_retraso():
    lector_data = {
        "email": "devolucion_retraso@universidad.edu",
        "nombre": "Test Devolucion Retraso"
    }
    client.post("/lectores/", json=lector_data)

    client.put("/copias/copia2/estado?estado=disponible")

    prestamo_response = client.post(
        "/prestamos/?copia_id=copia2&lector_email=devolucion_retraso@universidad.edu")
    prestamo_id = prestamo_response.json()["id"]

    prestamo = prestamos_db[prestamo_id]
    prestamo.fecha_devolucion_esperada = datetime.now() - timedelta(days=5)

    response = client.put(f"/prestamos/{prestamo_id}/devolver")
    assert response.status_code == 200
    assert response.json()["multa_dias"] == 10


def test_devolver_prestamo_no_encontrado():
    response = client.put("/prestamos/prestamo_inexistente/devolver")
    assert response.status_code == 404
    assert response.json()["detail"] == "Préstamo no encontrado"


def test_listar_prestamos():
    lector_data = {
        "email": "listar@universidad.edu",
        "nombre": "Test Listar"
    }
    client.post("/lectores/", json=lector_data)

    client.put("/copias/copia3/estado?estado=disponible")
    client.post(
        "/prestamos/?copia_id=copia3&lector_email=listar@universidad.edu")

    response = client.get("/prestamos/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_obtener_prestamos_lector():
    lector_data = {
        "email": "prestamos_lector@universidad.edu",
        "nombre": "Test Prestamos Lector"
    }
    client.post("/lectores/", json=lector_data)

    client.put("/copias/copia1/estado?estado=disponible")
    client.post(
        "/prestamos/?copia_id=copia1&lector_email=prestamos_lector@universidad.edu")

    response = client.get("/prestamos/lector/prestamos_lector@universidad.edu")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_obtener_prestamos_lector_no_encontrado():
    response = client.get("/prestamos/lector/inexistente@universidad.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Lector no encontrado"


def test_suscribir_bioalert():
    lector_data = {
        "email": "suscripcion@universidad.edu",
        "nombre": "Test Suscripcion"
    }
    client.post("/lectores/", json=lector_data)

    response = client.post(
        "/bioalert/suscribir?lector_email=suscripcion@universidad.edu&libro_id=libro_se_somerville")
    assert response.status_code == 200
    assert response.json()["mensaje"] == "Suscripción exitosa"


def test_suscribir_bioalert_lector_no_encontrado():
    response = client.post(
        "/bioalert/suscribir?lector_email=inexistente@universidad.edu&libro_id=libro_se_somerville")
    assert response.status_code == 404
    assert response.json()["detail"] == "Lector no encontrado"


def test_suscribir_bioalert_libro_no_encontrado():
    lector_data = {
        "email": "suscripcion2@universidad.edu",
        "nombre": "Test Suscripcion 2"
    }
    client.post("/lectores/", json=lector_data)

    response = client.post(
        "/bioalert/suscribir?lector_email=suscripcion2@universidad.edu&libro_id=libro_inexistente")
    assert response.status_code == 404
    assert response.json()["detail"] == "Libro no encontrado"


def test_listar_suscripciones():
    lector_data = {
        "email": "lista_suscripciones@universidad.edu",
        "nombre": "Test Lista Suscripciones"
    }
    client.post("/lectores/", json=lector_data)
    client.post(
        "/bioalert/suscribir?lector_email=lista_suscripciones@universidad.edu&libro_id=libro_se_somerville")

    response = client.get("/bioalert/suscripciones")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_listar_suscripciones_por_lector():
    lector_data = {
        "email": "filtrar_suscripciones@universidad.edu",
        "nombre": "Test Filtrar Suscripciones"
    }
    client.post("/lectores/", json=lector_data)
    client.post(
        "/bioalert/suscribir?lector_email=filtrar_suscripciones@universidad.edu&libro_id=libro_se_somerville")

    response = client.get(
        "/bioalert/suscripciones?lector_email=filtrar_suscripciones@universidad.edu")
    assert response.status_code == 200
    assert len(response.json()) >= 1
