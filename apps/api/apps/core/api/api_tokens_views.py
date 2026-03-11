import hashlib
import secrets

from django.db import models
from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import BaseModel
from apps.core.permissions import IsOrgAdmin


class ApiToken(BaseModel):
    """Долгоживущий API-токен для интеграций/партнёров."""

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='api_tokens')
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    token_hash = models.CharField(max_length=64, db_index=True, unique=True)
    scopes = models.JSONField(default=list)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'api_tokens'

    @staticmethod
    def hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def is_expired(self) -> bool:
        return bool(self.expires_at and self.expires_at < timezone.now())

    def __str__(self):
        return f'{self.name} ({self.organization_id})'


class ApiTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiToken
        fields = ['id', 'name', 'scopes', 'expires_at', 'last_used_at', 'is_active', 'created_at']
        read_only_fields = ['id', 'last_used_at', 'created_at']


class ApiTokenListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOrgAdmin]

    def get(self, request):
        tokens = ApiToken.objects.filter(organization=request.user.organization, is_active=True)
        return Response(ApiTokenSerializer(tokens, many=True).data)

    def post(self, request):
        name = (request.data.get('name') or '').strip()
        scopes = request.data.get('scopes', ['*'])
        expires = request.data.get('expires_at')

        if not name:
            return Response({'name': ['Обязательное поле']}, status=400)

        raw = f'crm_{secrets.token_urlsafe(40)}'
        token = ApiToken.objects.create(
            organization=request.user.organization,
            created_by=request.user,
            name=name,
            token_hash=ApiToken.hash(raw),
            scopes=scopes,
            expires_at=expires,
        )
        data = ApiTokenSerializer(token).data
        data['token'] = raw
        return Response(data, status=201)


class ApiTokenRevokeView(APIView):
    permission_classes = [IsAuthenticated, IsOrgAdmin]

    def delete(self, request, pk):
        try:
            token = ApiToken.objects.get(id=pk, organization=request.user.organization)
            token.is_active = False
            token.save(update_fields=['is_active'])
            return Response({'detail': 'Токен отозван'})
        except ApiToken.DoesNotExist:
            return Response({'detail': 'Не найден'}, status=404)
