from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet, CustomFieldViewSet, OrganizationActionsViewSet, OrganizationView

router = DefaultRouter()
router.register(r'custom-fields', CustomFieldViewSet, basename='custom-field')
router.register(r'organization', OrganizationActionsViewSet, basename='organization-actions')
router.register(r'branches', BranchViewSet, basename='branch')

urlpatterns = [
    path('organization', OrganizationView.as_view(), name='organization'),
    path('', include(router.urls)),
]
