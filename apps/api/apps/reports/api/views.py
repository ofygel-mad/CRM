from datetime import timedelta
import csv

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.customers.models import Customer
        from apps.deals.models import Deal
        from apps.tasks.models import Task

        org = request.user.organization
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        prev_start = (month_start - timedelta(days=1)).replace(day=1)

        customers_total = Customer.objects.filter(organization=org, deleted_at__isnull=True).count()
        customers_this_month = Customer.objects.filter(organization=org, created_at__gte=month_start).count()
        customers_prev_month = Customer.objects.filter(
            organization=org, created_at__gte=prev_start, created_at__lt=month_start,
        ).count()

        active_deals = Deal.objects.filter(organization=org, status='open', deleted_at__isnull=True).count()
        revenue = Deal.objects.filter(
            organization=org, status='won', closed_at__gte=month_start,
        ).aggregate(t=Sum('amount'))['t'] or 0

        tasks_today = Task.objects.filter(
            organization=org,
            assigned_to=request.user,
            status='open',
            due_at__date=now.date(),
        ).count()

        overdue_tasks = Task.objects.filter(
            organization=org,
            assigned_to=request.user,
            status='open',
            due_at__lt=now,
        ).count()

        recent_customers = Customer.objects.filter(
            organization=org, deleted_at__isnull=True,
        ).order_by('-created_at').values('id', 'full_name', 'company_name', 'status', 'created_at')[:5]

        deals_by_stage = (
            Deal.objects
            .filter(organization=org, status='open')
            .values('stage__name')
            .annotate(count=Count('id'), amount=Sum('amount'))
            .order_by('-amount')[:10]
        )

        customers_by_source = (
            Customer.objects
            .filter(organization=org, deleted_at__isnull=True)
            .exclude(source='')
            .values('source')
            .annotate(count=Count('id'))
            .order_by('-count')[:8]
        )

        data = {
            'customers_count': customers_total,
            'customers_delta': customers_this_month - customers_prev_month,
            'active_deals_count': active_deals,
            'revenue_month': float(revenue),
            'revenue_delta': 0,
            'tasks_today': tasks_today,
            'overdue_tasks': overdue_tasks,
            'recent_customers': list(recent_customers),
        }
        data['deals_by_stage'] = [
            {'stage': d['stage__name'], 'count': d['count'], 'amount': d['amount'] or 0}
            for d in deals_by_stage
        ]
        data['customers_by_source'] = [
            {'source': c['source'], 'count': c['count']}
            for c in customers_by_source
        ]

        revenue_by_month = (
            Deal.objects
            .filter(organization=org, status='won', closed_at__isnull=False)
            .annotate(month=TruncMonth('closed_at'))
            .values('month')
            .annotate(revenue=Sum('amount'), deals=Count('id'))
            .order_by('month')
        )
        data['revenue_by_month'] = [
            {
                'month': r['month'].strftime('%b %Y'),
                'revenue': float(r['revenue'] or 0),
                'deals': r['deals'],
            }
            for r in revenue_by_month
        ]

        return Response(data)


class ReportExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.customers.models import Customer
        org = request.user.organization

        customers = Customer.objects.filter(
            organization=org, deleted_at__isnull=True,
        ).values('full_name', 'company_name', 'phone', 'email', 'status', 'source', 'created_at')

        def stream():
            yield 'Имя,Компания,Телефон,Email,Статус,Источник,Дата\n'
            for c in customers:
                yield f"{c['full_name']},{c['company_name'] or ''},{c['phone'] or ''},{c['email'] or ''},{c['status']},{c['source'] or ''},{c['created_at'].strftime('%d.%m.%Y')}\n"

        response = StreamingHttpResponse(stream(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="crm-export.csv"'
        return response
