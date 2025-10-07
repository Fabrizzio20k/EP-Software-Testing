from datetime import datetime
from src.models import EstadoCopia, Autor, Libro, Copia, Lector, Prestamo, Suscripcion, BioAlert


def test_estado_copia_enum():
    assert EstadoCopia.DISPONIBLE == "disponible"
    assert EstadoCopia.PRESTADA == "prestada"
    assert EstadoCopia.RESERVADA == "reservada"
    assert EstadoCopia.CON_RETRASO == "con_retraso"
    assert EstadoCopia.EN_REPARACION == "en_reparacion"


def test_autor_model():
    autor = Autor(
        nombre="Ian Somerville",
        fecha_nacimiento=datetime(1951, 2, 23)
    )
    assert autor.nombre == "Ian Somerville"
    assert autor.fecha_nacimiento == datetime(1951, 2, 23)


def test_libro_model():
    autor = Autor(
        nombre="Ian Somerville",
        fecha_nacimiento=datetime(1951, 2, 23)
    )
    libro = Libro(
        id="libro1",
        nombre="Software Engineering",
        anio=2015,
        autor=autor
    )
    assert libro.id == "libro1"
    assert libro.nombre == "Software Engineering"
    assert libro.anio == 2015
    assert libro.autor.nombre == "Ian Somerville"


def test_copia_model():
    copia = Copia(
        id="copia1",
        libro_id="libro1",
        estado=EstadoCopia.DISPONIBLE,
        edicion="10th",
        idioma="ingles"
    )
    assert copia.id == "copia1"
    assert copia.libro_id == "libro1"
    assert copia.estado == EstadoCopia.DISPONIBLE
    assert copia.edicion == "10th"
    assert copia.idioma == "ingles"


def test_copia_model_defaults():
    copia = Copia(
        id="copia2",
        libro_id="libro1",
        estado=EstadoCopia.DISPONIBLE
    )
    assert copia.edicion is None
    assert copia.idioma == "ingles"


def test_lector_model():
    lector = Lector(
        email="test@universidad.edu",
        nombre="Test User"
    )
    assert lector.email == "test@universidad.edu"
    assert lector.nombre == "Test User"
    assert lector.prestamos_activos == []
    assert lector.dias_suspension == 0
    assert lector.fecha_fin_suspension is None


def test_prestamo_model():
    fecha_prestamo = datetime.now()
    fecha_devolucion_esperada = datetime.now()

    prestamo = Prestamo(
        id="prestamo1",
        copia_id="copia1",
        lector_email="test@universidad.edu",
        fecha_prestamo=fecha_prestamo,
        fecha_devolucion_esperada=fecha_devolucion_esperada
    )
    assert prestamo.id == "prestamo1"
    assert prestamo.copia_id == "copia1"
    assert prestamo.lector_email == "test@universidad.edu"
    assert prestamo.fecha_devolucion_real is None
    assert prestamo.dias_retraso == 0


def test_suscripcion_model():
    fecha_suscripcion = datetime.now()
    suscripcion = Suscripcion(
        lector_email="test@universidad.edu",
        libro_id="libro1",
        fecha_suscripcion=fecha_suscripcion
    )
    assert suscripcion.lector_email == "test@universidad.edu"
    assert suscripcion.libro_id == "libro1"
    assert suscripcion.fecha_suscripcion == fecha_suscripcion


def test_bioalert_singleton():
    bio_alert1 = BioAlert()
    bio_alert2 = BioAlert()
    assert bio_alert1 is bio_alert2


def test_bioalert_suscribir():
    bio_alert = BioAlert()
    bio_alert.suscripciones.clear()

    suscripcion = bio_alert.suscribir("test@universidad.edu", "libro1")

    assert suscripcion.lector_email == "test@universidad.edu"
    assert suscripcion.libro_id == "libro1"
    assert len(bio_alert.suscripciones) == 1


def test_bioalert_notificar_disponibilidad():
    bio_alert = BioAlert()
    bio_alert.suscripciones.clear()

    bio_alert.suscribir("test1@universidad.edu", "libro1")
    bio_alert.suscribir("test2@universidad.edu", "libro1")
    bio_alert.suscribir("test3@universidad.edu", "libro2")

    notificaciones = bio_alert.notificar_disponibilidad("libro1")

    assert len(notificaciones) == 2
    assert len(bio_alert.suscripciones) == 1
    assert bio_alert.suscripciones[0].libro_id == "libro2"


def test_bioalert_obtener_suscripciones():
    bio_alert = BioAlert()
    bio_alert.suscripciones.clear()

    bio_alert.suscribir("test1@universidad.edu", "libro1")
    bio_alert.suscribir("test2@universidad.edu", "libro2")

    todas = bio_alert.obtener_suscripciones()
    assert len(todas) == 2

    filtradas = bio_alert.obtener_suscripciones("test1@universidad.edu")
    assert len(filtradas) == 1
    assert filtradas[0].lector_email == "test1@universidad.edu"


def test_bioalert_obtener_suscripciones_sin_resultados():
    bio_alert = BioAlert()
    bio_alert.suscripciones.clear()

    bio_alert.suscribir("test1@universidad.edu", "libro1")

    filtradas = bio_alert.obtener_suscripciones("inexistente@universidad.edu")
    assert len(filtradas) == 0
