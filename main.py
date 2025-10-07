from fastapi import FastAPI, HTTPException, status
from typing import Optional, Dict
from datetime import datetime, timedelta
from src.models import EstadoCopia, Autor, Libro, Copia, Lector, Prestamo, BioAlert


app = FastAPI(
    title="Sistema de Biblioteca",
    version="1.0.0",
    description="API REST para gestión de biblioteca con préstamos, copias y sistema de alertas BioAlert"
)

libros_db: Dict[str, Libro] = {}
copias_db: Dict[str, Copia] = {}
lectores_db: Dict[str, Lector] = {}
prestamos_db: Dict[str, Prestamo] = {}
bio_alert = BioAlert()
notFoundBook = "Libro no encontrado"
notFoundCopy = "Copia no encontrada"
notFoundReader = "Lector no encontrado"


def inicializar_datos():
    autor_somerville = Autor(
        nombre="Ian Somerville",
        fecha_nacimiento=datetime(1951, 2, 23)
    )

    libro1 = Libro(
        id="libro_se_somerville",
        nombre="Software Engineering",
        anio=2015,
        autor=autor_somerville
    )
    libros_db[libro1.id] = libro1

    copias = [
        Copia(id="copia1", libro_id=libro1.id,
              estado=EstadoCopia.DISPONIBLE, edicion="8th", idioma="ingles"),
        Copia(id="copia2", libro_id=libro1.id,
              estado=EstadoCopia.DISPONIBLE, edicion="9th", idioma="ingles"),
        Copia(id="copia3", libro_id=libro1.id,
              estado=EstadoCopia.DISPONIBLE, edicion="9th", idioma="espanol"),
    ]

    for copia in copias:
        copias_db[copia.id] = copia


inicializar_datos()


@app.get("/", tags=["General"])
def root():
    """
    Endpoint raíz que retorna información básica de la API
    """
    return {"mensaje": "API Sistema de Biblioteca", "version": "1.0.0"}


@app.post("/libros/", status_code=status.HTTP_201_CREATED, tags=["Libros"])
def crear_libro(libro: Libro):
    """
    Crea un nuevo libro en el sistema

    - **id**: Identificador único del libro
    - **nombre**: Título del libro
    - **anio**: Año de publicación
    - **autor**: Información del autor (nombre y fecha de nacimiento)
    """
    if libro.id in libros_db:
        raise HTTPException(status_code=400, detail="El libro ya existe")
    libros_db[libro.id] = libro
    return libro


@app.get("/libros/", tags=["Libros"])
def listar_libros():
    """
    Obtiene la lista de todos los libros registrados en el sistema
    """
    return list(libros_db.values())


@app.get("/libros/{libro_id}", tags=["Libros"])
def obtener_libro(libro_id: str):
    """
    Obtiene la información de un libro específico por su ID

    - **libro_id**: Identificador único del libro
    """
    if libro_id not in libros_db:
        raise HTTPException(status_code=404, detail=notFoundBook)
    return libros_db[libro_id]


@app.get("/libros/autor/{nombre_autor}", tags=["Libros"])
def buscar_libros_por_autor(nombre_autor: str):
    """
    Busca libros por nombre del autor (búsqueda parcial case-insensitive)

    - **nombre_autor**: Nombre o parte del nombre del autor a buscar
    """
    libros = [libro for libro in libros_db.values()
              if nombre_autor.lower() in libro.autor.nombre.lower()]
    return libros


@app.post("/copias/", status_code=status.HTTP_201_CREATED, tags=["Copias"])
def crear_copia(copia: Copia):
    """
    Crea una nueva copia de un libro existente

    - **id**: Identificador único de la copia
    - **libro_id**: ID del libro al que pertenece la copia
    - **estado**: Estado actual de la copia
    - **edicion**: Edición del libro (ej: "8th", "9th")
    - **idioma**: Idioma de la copia
    """
    if copia.id in copias_db:
        raise HTTPException(status_code=400, detail="La copia ya existe")
    if copia.libro_id not in libros_db:
        raise HTTPException(status_code=404, detail=notFoundBook)
    copias_db[copia.id] = copia
    return copia


@app.get("/copias/", tags=["Copias"])
def listar_copias():
    """
    Obtiene la lista de todas las copias registradas
    """
    return list(copias_db.values())


@app.get("/copias/libro/{libro_id}", tags=["Copias"])
def obtener_copias_libro(libro_id: str):
    """
    Obtiene todas las copias de un libro específico

    - **libro_id**: Identificador del libro
    """
    if libro_id not in libros_db:
        raise HTTPException(status_code=404, detail=notFoundBook)
    copias = [copia for copia in copias_db.values() if copia.libro_id ==
              libro_id]
    return copias


@app.get("/copias/{copia_id}", tags=["Copias"])
def obtener_copia(copia_id: str):
    """
    Obtiene la información de una copia específica

    - **copia_id**: Identificador de la copia
    """
    if copia_id not in copias_db:
        raise HTTPException(status_code=404, detail=notFoundCopy)
    return copias_db[copia_id]


@app.put("/copias/{copia_id}/estado", tags=["Copias"])
def actualizar_estado_copia(copia_id: str, estado: EstadoCopia):
    """
    Actualiza el estado de una copia

    - **copia_id**: Identificador de la copia
    - **estado**: Nuevo estado (disponible, prestada, reservada, con_retraso, en_reparacion)
    """
    if copia_id not in copias_db:
        raise HTTPException(status_code=404, detail=notFoundCopy)
    copias_db[copia_id].estado = estado
    return copias_db[copia_id]


@app.post("/lectores/", status_code=status.HTTP_201_CREATED, tags=["Lectores"])
def crear_lector(lector: Lector):
    """
    Registra un nuevo lector en el sistema

    - **email**: Correo electrónico del lector (usado como identificador)
    - **nombre**: Nombre completo del lector
    """
    if lector.email in lectores_db:
        raise HTTPException(status_code=400, detail="El lector ya existe")
    lectores_db[lector.email] = lector
    return lector


@app.get("/lectores/", tags=["Lectores"])
def listar_lectores():
    """
    Obtiene la lista de todos los lectores registrados
    """
    return list(lectores_db.values())


@app.get("/lectores/{email}", tags=["Lectores"])
def obtener_lector(email: str):
    """
    Obtiene la información de un lector específico

    - **email**: Correo electrónico del lector
    """
    if email not in lectores_db:
        raise HTTPException(status_code=404, detail=notFoundReader)
    return lectores_db[email]


@app.post("/prestamos/", status_code=status.HTTP_201_CREATED, tags=["Préstamos"])
def crear_prestamo(copia_id: str, lector_email: str):
    """
    Crea un nuevo préstamo de una copia a un lector

    Restricciones:
    - La copia debe estar disponible
    - El lector no puede tener más de 3 préstamos activos
    - El lector no debe estar suspendido
    - Duración del préstamo: 30 días

    - **copia_id**: Identificador de la copia a prestar
    - **lector_email**: Email del lector que solicita el préstamo
    """
    if copia_id not in copias_db:
        raise HTTPException(status_code=404, detail=notFoundCopy)
    if lector_email not in lectores_db:
        raise HTTPException(status_code=404, detail=notFoundReader)

    copia = copias_db[copia_id]
    lector = lectores_db[lector_email]

    if copia.estado != EstadoCopia.DISPONIBLE:
        raise HTTPException(
            status_code=400, detail=f"La copia no está disponible. Estado: {copia.estado}")

    if len(lector.prestamos_activos) >= 3:
        raise HTTPException(
            status_code=400, detail="El lector ya tiene 3 préstamos activos")

    if lector.dias_suspension > 0:
        if lector.fecha_fin_suspension and datetime.now() < lector.fecha_fin_suspension:
            raise HTTPException(
                status_code=400,
                detail=f"Lector suspendido hasta {lector.fecha_fin_suspension}"
            )
        else:
            lector.dias_suspension = 0
            lector.fecha_fin_suspension = None

    prestamo_id = f"prestamo_{copia_id}_{int(datetime.now().timestamp())}"
    fecha_prestamo = datetime.now()
    fecha_devolucion = fecha_prestamo + timedelta(days=30)

    prestamo = Prestamo(
        id=prestamo_id,
        copia_id=copia_id,
        lector_email=lector_email,
        fecha_prestamo=fecha_prestamo,
        fecha_devolucion_esperada=fecha_devolucion
    )

    prestamos_db[prestamo_id] = prestamo
    copia.estado = EstadoCopia.PRESTADA
    lector.prestamos_activos.append(prestamo_id)

    return prestamo


@app.put("/prestamos/{prestamo_id}/devolver", tags=["Préstamos"])
def devolver_prestamo(prestamo_id: str):
    """
    Registra la devolución de un libro prestado

    Si hay retraso:
    - Se calculan los días de retraso
    - Se aplica una multa de 2 días de suspensión por cada día de retraso
    - Se notifica a los usuarios suscritos via BioAlert

    - **prestamo_id**: Identificador del préstamo a devolver
    """
    if prestamo_id not in prestamos_db:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    prestamo = prestamos_db[prestamo_id]
    copia = copias_db[prestamo.copia_id]
    lector = lectores_db[prestamo.lector_email]

    fecha_devolucion = datetime.now()
    prestamo.fecha_devolucion_real = fecha_devolucion

    if fecha_devolucion > prestamo.fecha_devolucion_esperada:
        dias_retraso = (fecha_devolucion -
                        prestamo.fecha_devolucion_esperada).days
        prestamo.dias_retraso = dias_retraso
        multa_dias = dias_retraso * 2
        lector.dias_suspension += multa_dias
        lector.fecha_fin_suspension = datetime.now() + timedelta(days=multa_dias)
        copia.estado = EstadoCopia.DISPONIBLE
    else:
        copia.estado = EstadoCopia.DISPONIBLE

    lector.prestamos_activos.remove(prestamo_id)

    notificaciones = bio_alert.notificar_disponibilidad(copia.libro_id)

    return {
        "prestamo": prestamo,
        "multa_dias": prestamo.dias_retraso * 2 if prestamo.dias_retraso > 0 else 0,
        "notificaciones_enviadas": notificaciones
    }


@app.get("/prestamos/", tags=["Préstamos"])
def listar_prestamos():
    """
    Obtiene la lista de todos los préstamos registrados
    """
    return list(prestamos_db.values())


@app.get("/prestamos/lector/{email}", tags=["Préstamos"])
def obtener_prestamos_lector(email: str):
    """
    Obtiene todos los préstamos de un lector específico

    - **email**: Correo electrónico del lector
    """
    if email not in lectores_db:
        raise HTTPException(status_code=404, detail=notFoundReader)
    prestamos = [p for p in prestamos_db.values() if p.lector_email == email]
    return prestamos


@app.post("/bioalert/suscribir", tags=["BioAlert"])
def suscribir_bioalert(lector_email: str, libro_id: str):
    """
    Suscribe a un lector para recibir notificaciones cuando un libro esté disponible

    Sistema BioAlert (Singleton): permite a los lectores suscribirse a libros no disponibles
    y recibir notificaciones automáticas cuando estén disponibles

    - **lector_email**: Email del lector que se suscribe
    - **libro_id**: ID del libro al que desea suscribirse
    """
    if lector_email not in lectores_db:
        raise HTTPException(status_code=404, detail=notFoundReader)
    if libro_id not in libros_db:
        raise HTTPException(status_code=404, detail=notFoundBook)

    suscripcion = bio_alert.suscribir(lector_email, libro_id)
    return {
        "mensaje": "Suscripción exitosa",
        "suscripcion": suscripcion
    }


@app.get("/bioalert/suscripciones", tags=["BioAlert"])
def listar_suscripciones(lector_email: Optional[str] = None):
    """
    Obtiene las suscripciones activas del sistema BioAlert

    - **lector_email**: (Opcional) Si se proporciona, filtra por suscripciones de ese lector
    """
    return bio_alert.obtener_suscripciones(lector_email)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
