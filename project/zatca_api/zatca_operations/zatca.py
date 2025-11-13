import base64
import json

from ..csr.csid_create import generate_csid, generate_x509
from ..csr.csr_generator import create_csr
from ..models import BusinessLocation,Sandbox

import logging

logger = logging.getLogger(__name__)

class Zatca:
    def __init__(self, location_id):
        self.id = location_id
        self.csr_response = None
        self.csid_response = None
        self.location = self._get_location()
        self.update_instance=None

    def _get_location(self):
        location = BusinessLocation.objects.filter(id=self.id).first()
        if not location:
            raise ValueError(f"Invalid location with ID: {self.id}")
        return location

    def generate_csr(self):
        try:
            location = self.location
            self.csr_response = create_csr(OU=location.organisation_unit, O=location.organisation, CN=location.common_name, SN=location.serial_number,  UID=location.tax_no,
                title=location.title, registeredAddress=location.registered_address, business=location.business_category,
                TYPE='TSTZATCA-Code-Signing'
            )
            logger.info(f"CSR Response: {self.csr_response}")

            return self.csr_response
        except Exception as e:
            logger.error(f"Error generating CSR: {str(e)}")
            return None

    def generate_csid(self,otp,**csid):
        try:
            self.csid_response = generate_csid(
                csr=csid['csr'], otp=otp,type="sandbox"
            )
            result = json.loads(self.csid_response.text)
            Sandbox.objects.filter(id=csid['id']).update(
                                            csid = result['binarySecurityToken'],
                                            csid_base64 = base64.b64decode(bytes(result['binarySecurityToken'], 'utf-8')).decode('utf-8'),
                                            secret_csid = result['secret'],
                                            csid_request = result['requestID'])
            return self.csid_response
        except Exception as e:
            logger.error(f"Error generating CSID: {str(e)}")
            return None

    # def generate_x509(self,**record):
    #     result_x509 = generate_x509(record['csid'],record['secret_csid'], record['csid_request'], 'sandbox')
    #     result = json.loads(result_x509.text)
    #     Sandbox.objects.filter(id=record['id']).update(
    #     x509_base64 = base64.b64decode(bytes(result['binarySecurityToken'], 'utf-8')).decode('utf-8'),
    #     x509_certificate = result['binarySecurityToken'],
    #     x509_secret = result['secret'],
    #     x509_request = result['requestID'])

    def generate_x509(self, **record):
        try:
            if not all([record.get('csid'), record.get('secret_csid'), record.get('csid_request')]):
                logger.error("Missing required fields for X509 generation.")
                return None

            result_x509 = generate_x509(record['csid'], record['secret_csid'], record['csid_request'], 'sandbox')
            if result_x509.status_code != 200:
                logger.error(f"X509 generation failed with status {result_x509.status_code}")
                return None

            result = json.loads(result_x509.text)
            Sandbox.objects.filter(id=record['id']).update(
                x509_base64=base64.b64decode(result['binarySecurityToken']).decode('utf-8'),
                x509_certificate=result['binarySecurityToken'],
                x509_secret=result['secret'],
                x509_request=result['requestID']
            )
            logger.info(f"X509 certificate successfully generated for sandbox ID: {record['id']}")
            return result_x509
        except Exception as e:
            logger.error(f"Error generating X509: {str(e)}")
            return None


