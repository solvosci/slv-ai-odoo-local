import threading
from collections import defaultdict
from contextlib import contextmanager

from ...application.ports.conversation_lock import ConversationLock


class MemoryConversationLock(ConversationLock):
    """

    Garantiza que solo una petición a la vez procese un mismo thread_id,
    evitando que dos mensajes simultáneos de la misma conversación se
    mezclen. Conversaciones distintas no se bloquean entre sí.
    Al vivir en memoria, solo funciona con un único proceso.

    https://www.stacklesson.com/react-fastapi/py-file-exceptions/ch07-lesson-04-context-managers/
    """

    def __init__(self):
        self._locks = defaultdict(threading.Lock)

    @contextmanager
    def hold(self, thread_id):
        with self._locks[thread_id]:
            yield
