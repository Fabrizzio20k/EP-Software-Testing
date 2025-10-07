from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


class EstadoCopia(str, Enum):
    DISPONIBLE = "disponible"
    PRESTADA = "prestada"
    RESERVADA = "reservada"
    CON_RETRASO = "con_retraso"
    EN_REPARACION = "en_reparacion"


class Autor(BaseModel):
    nombre: str
    fecha_nacimiento: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Ian Somerville",
                "fecha_nacimiento": "1951-02-23T00:00:00"
            }
        }


class Libro(BaseModel):
    id: str
    nombre: str
    anio: int
    autor: Autor

    class Config:
        json_schema_extra = {
            "example": {
                "id": "libro1",
                "nombre": "Software Engineering",
                "anio": 2015,
                "autor": {
                    "nombre": "Ian Somerville",
                    "fecha_nacimiento": "1951-02-23T00:00:00"
                }
            }
        }


class Copia(BaseModel):
    id: str
    libro_id: str
    estado: EstadoCopia
    edicion: Optional[str] = None
    idioma: str = "ingles"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "copia1",
                "libro_id": "libro1",
                "estado": "disponible",
                "edicion": "10th",
                "idioma": "ingles"
            }
        }


class Prestamo(BaseModel):
    id: str
    copia_id: str
    lector_email: str
    fecha_prestamo: datetime
    fecha_devolucion_esperada: datetime
    fecha_devolucion_real: Optional[datetime] = None
    dias_retraso: int = 0


class Lector(BaseModel):
    email: EmailStr
    nombre: str
    prestamos_activos: List[str] = Field(default_factory=list)
    dias_suspension: int = 0
    fecha_fin_suspension: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "estudiante@universidad.edu",
                "nombre": "Juan Pérez",
                "prestamos_activos": [],
                "dias_suspension": 0
            }
        }


class Suscripcion(BaseModel):
    lector_email: str
    libro_id: str
    fecha_suscripcion: datetime


class BioAlert:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BioAlert, cls).__new__(cls)
            cls._instance.suscripciones = []
        return cls._instance

    def suscribir(self, lector_email: str, libro_id: str):
        suscripcion = Suscripcion(
            lector_email=lector_email,
            libro_id=libro_id,
            fecha_suscripcion=datetime.now()
        )
        self.suscripciones.append(suscripcion)
        return suscripcion

    def notificar_disponibilidad(self, libro_id: str):
        notificaciones = []
        suscripciones_libro = [
            s for s in self.suscripciones if s.libro_id == libro_id]
        for suscripcion in suscripciones_libro:
            notificaciones.append({
                "email": suscripcion.lector_email,
                "mensaje": f"El libro {libro_id} está disponible",
                "fecha": datetime.now()
            })
        self.suscripciones = [
            s for s in self.suscripciones if s.libro_id != libro_id]
        return notificaciones

    def obtener_suscripciones(self, lector_email: Optional[str] = None):
        if lector_email:
            return [s for s in self.suscripciones if s.lector_email == lector_email]
        return self.suscripciones
