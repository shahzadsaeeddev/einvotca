from celery import shared_task
from .models import Sandbox
from .zatca_operations.zatca import Zatca
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_credentials_task(location_id, sandbox_id):
    try:
        sandbox = Sandbox.objects.filter(id=sandbox_id).first()
        if not sandbox:
            logger.error(f"Sandbox record with ID {sandbox_id} does not exist.")
            return

        zatca = Zatca(location_id=location_id)
        x509_result = zatca.generate_x509(**sandbox.__dict__)

        if x509_result:
            logger.info(f"X509 certificate successfully generated for sandbox ID: {sandbox_id}")
        else:
            logger.error(f"Failed to generate X509 certificate for sandbox ID: {sandbox_id}")
    except Exception as e:
        logger.error(f"Error in X509 generation task: {str(e)}")
        raise

# @shared_task
# def generate_credentials_task(location_id, sandbox_id):
#     try:
#         sandbox = Sandbox.objects.filter(id=sandbox_id).first()
#         if not sandbox:
#             raise ValueError(f"Sandbox record with ID {sandbox_id} does not exist.")
#
#         zatca = Zatca(location_id=location_id)
#
#
#
#         x509_result = zatca.generate_x509(**sandbox.__dict__)
#
#         if x509_result:
#             logger.info(f"X509 certificate successfully generated for sandbox ID: {sandbox_id}")
#         else:
#             logger.error(f"Failed to generate X509 certificate for sandbox ID: {sandbox_id}")
#     except Exception as e:
#         logger.error(f"Error in X509 generation task: {str(e)}")
#         raise



