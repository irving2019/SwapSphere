from rest_framework import serializers
from .models import Ad, ExchangeProposal

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['id', 'user', 'title', 'description', 'image_url', 
                 'category', 'condition', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ExchangeProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_receiver', 'message', 
                 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        return super().create(validated_data)
