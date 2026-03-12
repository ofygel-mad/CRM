from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestDashboard:
    def test_dashboard_returns_required_fields(self, api_client):
        r = api_client.get('/api/v1/reports/dashboard')
        assert r.status_code == 200
        for field in [
            'customers_count', 'customers_delta', 'active_deals_count',
            'revenue_month', 'tasks_today', 'overdue_tasks',
        ]:
            assert field in r.data, f'missing: {field}'

    def test_dashboard_customers_count(self, api_client, customer):
        r = api_client.get('/api/v1/reports/dashboard')
        assert r.status_code == 200
        assert r.data['customers_count'] >= 1

    def test_dashboard_revenue_only_current_month(self, api_client, org, user, customer, pipeline):
        from apps.deals.models import Deal

        stage = pipeline.stages.filter(type='won').first() or pipeline.stages.first()
        now = timezone.now()
        Deal.objects.create(
            organization=org, owner=user, customer=customer,
            pipeline=pipeline, stage=stage,
            title='Won this month', amount=100000, currency='KZT',
            status='won', closed_at=now,
        )
        Deal.objects.create(
            organization=org, owner=user, customer=customer,
            pipeline=pipeline, stage=stage,
            title='Old deal', amount=999999, currency='KZT',
            status='won', closed_at=now - timedelta(days=40),
        )

        r = api_client.get('/api/v1/reports/dashboard')
        assert r.status_code == 200
        assert float(r.data['revenue_month']) == 100000.0

    def test_dashboard_overdue_tasks(self, api_client, org, user, customer):
        from apps.tasks.models import Task

        Task.objects.create(
            organization=org, assigned_to=user, customer=customer,
            title='Overdue', priority='high', status='open',
            due_at=timezone.now() - timedelta(days=2),
        )
        r = api_client.get('/api/v1/reports/dashboard')
        assert r.status_code == 200
        assert r.data['overdue_tasks'] >= 1

    def test_dashboard_cached(self, api_client):
        """Второй запрос отдаётся из кэша (нет ошибок)."""
        api_client.get('/api/v1/reports/dashboard')
        r = api_client.get('/api/v1/reports/dashboard')
        assert r.status_code == 200

    def test_manager_kpi(self, api_client):
        r = api_client.get('/api/v1/reports/manager-kpi/')
        assert r.status_code == 200
        assert 'managers' in r.data
