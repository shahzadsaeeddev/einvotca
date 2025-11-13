""" Assets management roles. """
from rest_framework.permissions import BasePermission
from  accounts.models import Users

#
# class HasAMPRoles(BasePermission):
#     """
#     Check if the user has any of the required AMP Roles
#     """
#
#     message = (
#         "You do not have any Assets Management Roles, "
#         "Please contact Keycloak Administrator to add roles into your Keycloak Account"
#     )
#
#     def has_permission(self, request, view):
#         return request.user.has_roles(User.AMP_ALL_ROLES, any_role=True)
#
#
# class HasNCARoles(BasePermission):
#     """
#         Check if the user has NCA roles
#         """
#
#     def has_permission(self, request, view):
#         return request.user.is_nca
#
#
# class IsRiskManager(BasePermission):
#     """
#         Check if the user has NCA roles
#         """
#
#     def has_permission(self, request, view):
#         return request.user.is_risk_manager