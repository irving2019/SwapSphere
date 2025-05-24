from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Ad, ExchangeProposal

class AdTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        
        self.ad_data = {
            'title': 'Test Ad',
            'description': 'Test Description',
            'category': 'Electronics',
            'condition': 'new'
        }
        
    def test_create_ad(self):
        """Тест создания объявления"""
        response = self.client.post('/api/ads/', self.ad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ad.objects.count(), 1)
        self.assertEqual(Ad.objects.get().title, 'Test Ad')
        
    def test_update_ad(self):
        """Тест обновления объявления"""
        ad = Ad.objects.create(user=self.user, **self.ad_data)
        response = self.client.patch(
            f'/api/ads/{ad.id}/',
            {'title': 'Updated Title'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Ad.objects.get(id=ad.id).title, 'Updated Title')
        
    def test_delete_ad(self):
        """Тест удаления объявления"""
        ad = Ad.objects.create(user=self.user, **self.ad_data)
        response = self.client.delete(f'/api/ads/{ad.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ad.objects.count(), 0)

class ExchangeProposalTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        
        self.ad1 = Ad.objects.create(
            user=self.user1,
            title='Ad 1',
            description='Description 1',
            category='Electronics',
            condition='new'
        )
        
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Ad 2',
            description='Description 2',
            category='Electronics',
            condition='used'
        )
        
    def test_create_proposal(self):
        """Тест создания предложения обмена"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'ad_sender': self.ad1.id,
            'ad_receiver': self.ad2.id,
            'comment': 'Test exchange proposal'
        }
        response = self.client.post('/api/proposals/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExchangeProposal.objects.count(), 1)
        
    def test_accept_proposal(self):
        """Тест принятия предложения обмена"""
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Test exchange proposal'
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/proposals/{proposal.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ExchangeProposal.objects.get(id=proposal.id).status,
            'accepted'
        )
