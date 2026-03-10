from django.contrib.auth import get_user_model
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.users.models import OrganizationMembership
from ..models import User
from ..serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'email']

    def get_queryset(self):
        return User.objects.filter(
            organization=self.request.user.organization,
        ).order_by('full_name')

    @action(detail=False, methods=['get'])
    def me(self, request):
        membership = OrganizationMembership.objects.filter(
            user=request.user, organization=request.user.organization,
        ).first()
        return Response({
            **UserSerializer(request.user).data,
            'role': membership.role if membership else 'viewer',
        })

    @action(detail=False, methods=['get'], url_path='team')
    def team(self, request):
        users = request.user.organization.users.all()
        memberships = {
            m.user_id: m.role
            for m in OrganizationMembership.objects.filter(
                organization=request.user.organization,
            )
        }
        data = []
        for u in users:
            d = UserSerializer(u).data
            d['role'] = memberships.get(u.id, 'viewer')
            data.append(d)
        return Response({'results': data})

    @action(detail=True, methods=['patch'], url_path='role')
    def set_role(self, request, pk=None):
        from apps.core.permissions import user_can

        if not user_can(request.user, 'users.invite'):
            return Response({'detail': 'Недостаточно прав'}, status=403)
        target = get_user_model().objects.get(id=pk, organization=request.user.organization)
        role = request.data.get('role')
        if role not in ('admin', 'manager', 'viewer'):
            return Response({'detail': 'Неверная роль'}, status=400)
        OrganizationMembership.objects.update_or_create(
            user=target,
            organization=request.user.organization,
            defaults={'role': role},
        )
        return Response({'user_id': str(target.id), 'role': role})
