import time

import requests
import json
from django.conf import settings

from neksio_api.models import BusinessPackages
from .models import RoleGroup

base = settings.OIDC_HOST
realm = settings.OIDC_REALM


def create_user(token, **data):
    url = f"{base}/admin/realms/{realm}/users"
    payload = json.dumps({
        "username": data["username"],
        "email": data["email"],
        "firstName": data["first_name"],
        "lastName": data["last_name"],
        "enabled": True,
        "emailVerified": False,
        "credentials": [
            {
                "type": "password",
                "value": data["password"],
                "temporary": False
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + str(token)
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    user_id = get_user_id(token, data["username"])
    user_code = user_id.json()[0]['id']
    default = RoleGroup.objects.filter(group_name="setup").first().group_code
    assigned = RoleGroup.objects.filter(id=data["user_roles"].id).first().group_code
    add_user_to_group(token, user_code, assigned)
    remove_user_from_group(token, user_code, default)

    # print(res)
    return response, user_code


def update_user(token, userid, **data):
    url = f"{base}/admin/realms/{realm}/users/{userid}"
    payload = json.dumps({
        "email": data["email"],
        "firstName": data["first_name"],
        "lastName": data["last_name"],
        "enabled": True,
        "emailVerified": True,
        "attributes": {
            "display_picture": data["display_picture"] if "display_picture" in data else ""
        }

    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + str(token)
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    return response

def update_user_collection(token, userid, collection_id, business_type, country):
    url = f"{base}/admin/realms/{realm}/users/{userid}"
    payload = json.dumps({
        "attributes": {
            "collections_id": collection_id,
            "business_plan": business_type,
            "country": country
        }

    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + str(token)
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.text)

    return response


# def update_user_business_type(token, userid, business_type):
#     url = f"{base}/admin/realms/{realm}/users/{userid}"
#     payload = json.dumps({
#
#         "attributes": {
#             "business_plan": business_type
#         }
#
#     })
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': 'Bearer ' + str(token)
#     }
#
#     response = requests.request("PUT", url, headers=headers, data=payload)
#
#     return response

def get_user_ids(token, username):
    url = f"{base}/admin/realms/{realm}/users"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    params = {'username': username}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print("Response code:", response.status_code)
        if response.status_code != 200:
            print(f"Failed to fetch user {username}: {response.text}")
        return response
    except Exception as e:
        print(f"Error fetching user {username}: {e}")
        return None

def assign_expire_group(token, username):
    user_response = get_user_ids(token, username)
    if not user_response or user_response.status_code != 200:
        return None

    users = user_response.json()
    if not users:
        print(f"User not found in Keycloak: {username}")
        return None

    user_id = users[0]['id']

    headers = {'Authorization': f'Bearer {token}'}

    groups_url = f"{base}/admin/realms/{realm}/groups"
    groups_response = requests.get(groups_url, headers=headers, timeout=30)
    if groups_response.status_code != 200:
        print(f"Failed to fetch groups: {groups_response.text}")
        return None

    groups = groups_response.json()
    expire_group = next((g for g in groups if g.get('name') == "Is_Expire"), None)
    if not expire_group:
        print("Group 'Is_Expire' not found in Keycloak!")
        return None

    expire_group_id = expire_group['id']

    user_groups_url = f"{base}/admin/realms/{realm}/users/{user_id}/groups"
    current_groups = requests.get(user_groups_url, headers=headers).json()
    for grp in current_groups:
        del_url = f"{user_groups_url}/{grp['id']}"
        requests.delete(del_url, headers=headers)

    add_url = f"{user_groups_url}/{expire_group_id}"
    res = requests.put(add_url, headers=headers)
    if res.status_code == 204:
        print(f"{username} moved to 'Is_Expire' group.")
        return res
    else:
        print(f"Failed to assign 'Is_Expire' group to {username}: {res.text}")
        return None




def deactivate_user(token, userid, status):
    url = f"{base}/admin/realms/{realm}/users/{userid}"
    payload = json.dumps({
        "enabled": status,
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + str(token)
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    return response


def reset_password_user(token, userid, **data):
    url = f"{base}/admin/realms/{realm}/users/{userid}"
    payload = json.dumps({
        "credentials": [
            {
                "type": "password",
                "value": data["password"],
                "temporary": False
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + str(token)
    }
    response = requests.request("PUT", url, headers=headers, data=payload)

    return response


def get_user_id(token, username):
    url = f"{base}/admin/realms/{realm}/users?username={username}"

    payload = json.dumps({})
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + str(token)
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response


def add_user_to_group(token, user_id, group_id):
    url = f"{base}/admin/realms/{realm}/users/{user_id}/groups/{group_id}"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.put(url.strip(), headers=headers)

    return response


def remove_user_from_group(token, user_id, group_id):
    url = f"{base}/admin/realms/{realm}/users/{user_id}/groups/{group_id}"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(url, headers=headers)

    return response


def update_role(token, userid, default, assign):
    remove_user_from_group(token, userid, default)
    add_user_to_group(token, userid, assign)


def update_role_self(token, userid,collection, business_type, country):
    print("COLLECTION ID:", collection)

    user_id=get_user_id(token,userid).json()[0]['id']
    update_user_collection(token, user_id, collection, business_type, country)
    assigned = BusinessPackages.objects.filter(package_name="Starter").first()
    setup = RoleGroup.objects.filter(group_name="setup").first()
    add_user_to_group(token, user_id, assigned.package_code)
    remove_user_from_group(token, user_id, setup.group_code)
    return user_id,assigned

# def update_role_self(token, userid,collection):
#     user_id=get_user_id(token,userid).json()[0]['id']
#     update_user_collection(token,user_id,collection)
#     assigned = RoleGroup.objects.filter(group_name="owner").first()
#     setup = RoleGroup.objects.filter(group_name="setup").first()
#     add_user_to_group(token, user_id, assigned.group_code)
#     remove_user_from_group(token, user_id, setup.group_code)
#     return user_id,assigned
