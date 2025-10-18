"""
Middleware para capturar y loguear todas las excepciones no manejadas
antes de que se conviertan en error 500
"""
import logging
import traceback

logger = logging.getLogger(__name__)


class ExceptionLoggingMiddleware:
    """
    Middleware que captura TODAS las excepciones no manejadas
    y las loguea con el traceback completo antes de que Django
    genere el error 500.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Este método se llama cuando una vista lanza una excepción.
        Se ejecuta ANTES de que Django genere la respuesta 500.
        """
        logger.error("=" * 80)
        logger.error("🚨 EXCEPCIÓN NO MANEJADA DETECTADA 🚨")
        logger.error("=" * 80)
        logger.error(f"Path: {request.path}")
        logger.error(f"Method: {request.method}")
        logger.error(f"User: {request.user}")
        logger.error(f"Exception Type: {type(exception).__name__}")
        logger.error(f"Exception Message: {str(exception)}")
        logger.error("-" * 80)
        logger.error("Traceback completo:")
        logger.error(traceback.format_exc())
        logger.error("=" * 80)

        # Retornar None para que Django continúe con su manejo normal de errores
        return None

