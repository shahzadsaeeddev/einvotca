from celery import shared_task
from django.utils import timezone
from neksio_api.models import BusinessProfile
from django.conf import settings
import requests
from accounts.keycloak import assign_expire_group

from accounts.models import Users


@shared_task
def activity_logs_task(location_id, user_id, module, action_type, description, ip_address=None):
    from .models import ActivityLog

    ActivityLog.objects.create(location_id=location_id, user_id=user_id, module=module, action_type=action_type, description=description,
                               ip_address=ip_address, )


def get_admin_token():
    url = f"{settings.OIDC_HOST}/realms/{settings.OIDC_REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.OIDC_RP_CLIENT_ID,
        "client_secret": settings.OIDC_RP_CLIENT_SECRET,
    }
    try:
        resp = requests.post(url, data=data, verify=False)
        if resp.status_code != 200:
            print("Unable to get admin token:", resp.text)
            return None
        return resp.json().get("access_token")
    except Exception as e:
        print("Error requesting admin token:", e)
        return None



@shared_task
def assign_expired_user_group():
    token = get_admin_token()
    if not token:
        print("Failed to get admin token")
        return

    now = timezone.now()
    companies = BusinessProfile.objects.filter(expiry_date__lt=now)
    print(f"Found {companies.count()} expired companies")

    for company in companies:
        print(f"Processing expired company: {company.registered_name} (slug: {company.slug})")

        users = Users.objects.filter(business_profile=company, is_delete=False)
        print(f"Found {users.count()} users for company {company.registered_name}")

        for user in users:
            print(f"Processing user: {user.username} (Keycloak UUID: {user.keycloak_uuid})")

            result = assign_expire_group(token, user.username)

            if result is None and user.keycloak_uuid:
                print(f"Trying with Keycloak UUID for user {user.username}")
                result = assign_expire_group(token, user.keycloak_uuid)

            if result is None:
                print(f"Failed to process user: {user.username}")

    print("Expiry group assignment complete.")

