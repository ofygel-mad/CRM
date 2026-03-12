import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestRegistration:
    def test_register_creates_org_and_pipeline(self):
        """Регистрация создаёт организацию и дефолтную воронку."""
        client = APIClient()
        r = client.post('/api/v1/auth/register/', {
            'organization_name': 'Test Org',
            'full_name': 'Test Owner',
            'email': 'owner@test.com',
            'password': 'strongpass123',
            'mode': 'basic',
        })
        assert r.status_code == 201, r.data
        assert 'access' in r.data
        assert r.data['org']['name'] == 'Test Org'

        from apps.pipelines.models import Pipeline
        assert Pipeline.objects.filter(
            organization__slug=r.data['org']['slug']
        ).exists()

    def test_register_sets_basic_capabilities(self):
        """basic mode → только basic capabilities, без advanced."""
        client = APIClient()
        r = client.post('/api/v1/auth/register/', {
            'organization_name': 'Basic Org',
            'full_name': 'Owner',
            'email': 'basic@test.com',
            'password': 'strongpass123',
            'mode': 'basic',
        })
        assert r.status_code == 201
        caps = set(r.data['capabilities'])
        assert 'customers.read' in caps
        assert 'automations.manage' not in caps
        assert 'audit.read' not in caps

    def test_register_duplicate_email_rejected(self):
        client = APIClient()
        payload = {
            'organization_name': 'Org', 'full_name': 'User',
            'email': 'dupe@test.com', 'password': 'strongpass123',
        }
        client.post('/api/v1/auth/register/', payload)
        r = client.post('/api/v1/auth/register/', payload)
        assert r.status_code == 400

    def test_register_weak_password_rejected(self):
        client = APIClient()
        r = client.post('/api/v1/auth/register/', {
            'organization_name': 'Org', 'full_name': 'User',
            'email': 'weak@test.com', 'password': '123',
        })
        assert r.status_code == 400

    def test_login_returns_tokens(self):
        client = APIClient()
        client.post('/api/v1/auth/register/', {
            'organization_name': 'Login Org', 'full_name': 'User',
            'email': 'login@test.com', 'password': 'strongpass123',
        })
        r = client.post('/api/v1/auth/login/', {
            'email': 'login@test.com', 'password': 'strongpass123',
        })
        assert r.status_code == 200
        assert 'access' in r.data
        assert 'refresh' in r.data

    def test_login_wrong_password_rejected(self):
        client = APIClient()
        r = client.post('/api/v1/auth/login/', {
            'email': 'nobody@test.com', 'password': 'wrong',
        })
        assert r.status_code in (400, 401)

    def test_me_returns_user_data(self, api_client):
        r = api_client.get('/api/v1/auth/me/')
        assert r.status_code == 200
        assert 'user' in r.data
        assert 'org' in r.data
        assert 'capabilities' in r.data


@pytest.mark.django_db
class TestPermissions:
    def _make_client(self, org, role='viewer'):
        from apps.users.models import OrganizationMembership
        from rest_framework_simplejwt.tokens import RefreshToken

        user = User.objects.create_user(
            email=f'{role}_{org.id}@test.com',
            password='pass123',
            full_name=f'{role.title()} User',
            organization=org,
        )
        OrganizationMembership.objects.get_or_create(
            user=user, organization=org, defaults={'role': role}
        )
        client = APIClient()
        token = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        return client

    def test_viewer_cannot_create_customer(self, org):
        client = self._make_client(org, 'viewer')
        r = client.post('/api/v1/customers/', {
            'full_name': 'Viewer Test', 'phone': '+77001111111',
        })
        assert r.status_code in (403, 405)

    def test_manager_can_create_customer(self, org):
        client = self._make_client(org, 'manager')
        r = client.post('/api/v1/customers/', {
            'full_name': 'Manager Test', 'phone': '+77002222222',
        })
        assert r.status_code == 201

    def test_unauthenticated_rejected(self):
        client = APIClient()
        r = client.get('/api/v1/customers/')
        assert r.status_code == 401

    def test_cross_org_isolation(self, org, customer):
        """Клиент из другой организации не должен быть виден."""
        from apps.organizations.models import Organization
        from apps.organizations.models import apply_mode_capabilities

        other_org = Organization.objects.create(
            name='Other Org', slug='other-org', mode='basic'
        )
        apply_mode_capabilities(other_org)
        other_client = self._make_client(other_org, 'manager')

        r = other_client.get(f'/api/v1/customers/{customer.id}/')
        assert r.status_code in (403, 404)
