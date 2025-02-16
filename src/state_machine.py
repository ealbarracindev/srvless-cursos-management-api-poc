class StateMachine:
    def __init__(self):
        self.transitions = {
            "Planeado": ["En Curso", "Cancelado"],
            "En Curso": ["Completado", "Cancelado"],
            "Completado": [],
            "Cancelado": []
        }

    def can_transition(self, current_state: str, new_state: str) -> bool:
        """
        Verifica si una transición de estado es válida.
        
        :param current_state: Estado actual.
        :param new_state: Estado al que se desea transitar.
        :return: True si la transición es válida.
        """
        return new_state in self.transitions.get(current_state, [])

    def validate_transition(self, current_state: str, new_state: str):
        """
        Valida una transición de estado. Lanza una excepción si no es válida.

        :param current_state: Estado actual.
        :param new_state: Estado al que se desea transitar.
        """
        if not self.can_transition(current_state, new_state):
            raise ValueError(f"No se puede transitar de '{current_state}' a '{new_state}'.")
