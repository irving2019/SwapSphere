from django.shortcuts import render
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Ad, ExchangeProposal
from .serializers import AdSerializer, ExchangeProposalSerializer

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['created_at', 'title']

    def get_queryset(self):
        queryset = Ad.objects.all()
        category = self.request.query_params.get('category', None)
        condition = self.request.query_params.get('condition', None)

        if category:
            queryset = queryset.filter(category=category)
        if condition:
            queryset = queryset.filter(condition=condition)

        return queryset

class ExchangeProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_ads = Ad.objects.filter(user=self.request.user)
        return ExchangeProposal.objects.filter(
            Q(ad_sender__in=user_ads) | Q(ad_receiver__in=user_ads)
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        proposal = self.get_object()
        if proposal.ad_receiver.user != request.user:
            return Response({'error': 'Not authorized'}, status=403)
        
        proposal.status = 'accepted'
        proposal.save()
        return Response({'status': 'proposal accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        proposal = self.get_object()
        if proposal.ad_receiver.user != request.user:
            return Response({'error': 'Not authorized'}, status=403)
        
        proposal.status = 'rejected'
        proposal.save()
        return Response({'status': 'proposal rejected'})
