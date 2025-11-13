from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import *

app_name = 'api'
router = DefaultRouter()
router.register(r'locations', LocationView)

urlpatterns = [
    path('', include(router.urls)),
    path('<str:location>/csid/',GenerateCSID.as_view(),name='generate-csid'),
    path('<str:location>/sandbox/csid/',SandboxCSIDView.as_view(),name='sandbox-csid'),
    path('<str:location>/sandbox/x509/',SandboxX509View.as_view(),name='sandbox-x509'),
    path('<str:location>/simulation/csid/',SimulationView.as_view(),name='simulation-csid'),
    path('<str:location>/simulation/x509/',SimulationX509View.as_view(),name='simulation-x509'),
    path('<str:location>/production/csid/',ProductionView.as_view(),name='production-csid'),
    path('<str:location>/production/x509/',ProductionX509View.as_view(),name='production-x509'),
    path('sandbox/compliance/base64/', SandboxComplianceBase64.as_view(),
         name='sandbox/compliance/base64/'),
    path('sandbox/compliance/invoice/', SandboxComplianceInvoice.as_view(),
         name='sandbox/compliance/filter/'),
    path('sandbox/reporting/', SandboxReporting.as_view(),
         name='sandbox/reporting/'),
    path('sandbox/clearance/', SandboxClearance.as_view(),
         name='sandbox/clearance/'),
    #simulation
    path('simulation/compliance/invoice/', SimulationComplianceInvoice.as_view(),
         name='sandbox/compliance/filter/'),
    path('simulation/reporting/', SimulationReporting.as_view(),
         name='sandbox/reporting/'),
    path('simulation/clearance/', SimulationClearance.as_view(),
         name='sandbox/clearance/'),
    path('production/compliance/invoice/', ProductionComplianceInvoice.as_view(),
         name='sandbox/compliance/filter/'),
    path('production/reporting/', ProductionReporting.as_view(),
         name='sandbox/reporting/'),
    path('production/clearance/', ProductionClearance.as_view(),
         name='sandbox/clearance/'),

    path('location/<int:location_id>/verify-otp/', OTPVerificationView.as_view(), name='otp-verify'),
    path('location/<int:id>/', BusinessLocationView.as_view(), name='business-location'),
]