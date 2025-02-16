import uuid
from datetime import datetime

class Course:
    def __init__(self, titulo, descripcion, instructor, capacidad, cursoId=None, estado="Planeado"):
        self.cursoId = cursoId if cursoId is not None else str(uuid.uuid4())
        self.titulo = titulo
        self.descripcion = descripcion
        self.instructor = instructor
        self.capacidad = capacidad
        self.inscritos = 0
        self.estado = estado
        self.fechaCreacion = datetime.utcnow().isoformat()

    def to_dict(self):
        """Convierte el curso a un diccionario para DynamoDB"""
        return {
            "cursoId": self.cursoId,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "instructor": self.instructor,
            "capacidad": self.capacidad,
            "inscritos": self.inscritos,
            "estado": self.estado,
            "fechaCreacion": self.fechaCreacion
        }

    @staticmethod
    def create_course_item(titulo, descripcion, instructor, capacidad, estado="Planeado"):
        """Método estático para crear un diccionario de curso sin instanciar la clase"""
        return {
            "cursoId": str(uuid.uuid4()),
            "titulo": titulo,
            "descripcion": descripcion,
            "instructor": instructor,
            "capacidad": capacidad,
            "inscritos": 0,
            "estado": estado,
            "fechaCreacion": datetime.utcnow().isoformat()
        }
