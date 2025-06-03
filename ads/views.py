from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ad, ExchangeProposal, UserProfile, AdImage, AdComment, PrivateMessage, UserBlock, Conversation
from .serializers import AdSerializer, ExchangeProposalSerializer
from .forms import AdForm, ExchangeProposalForm, UserRegistrationForm, UserProfileForm, UserForm, AdImageForm, AdImageFormSet, AdCommentForm, AdCommentReplyForm, PrivateMessageForm, MessageReplyForm, UserBlockForm

# HTML Views
def ad_list(request):
    search = request.GET.get('search')
    category = request.GET.get('category')
    condition = request.GET.get('condition')
    status = request.GET.get('status')

    # Исключаем объявления с завершенными обменами
    ads = Ad.objects.filter(
        ~Q(sent_proposals__status='completed') & 
        ~Q(received_proposals__status='completed')
    ).distinct().order_by('-created_at')

    if search:
        ads = ads.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    if category:
        ads = ads.filter(category=category)
    if condition:
        ads = ads.filter(condition=condition)
    if status:
        ads = ads.filter(status=status)

    context = {
        'ads': ads,
        'category_choices': Ad.CATEGORY_CHOICES,
        'selected_category': category,
        'selected_condition': condition,
        'selected_status': status,
        'search': search,
        'condition_choices': Ad.CONDITION_CHOICES,
        'status_choices': Ad.STATUS_CHOICES,
    }
    return render(request, 'ads/ad_list.html', context)

def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    
    # Получаем только основные комментарии (не ответы)
    comments = ad.comments.filter(parent=None).prefetch_related('replies__author__userprofile', 'author__userprofile').order_by('-created_at')
    
    # Если пользователь - автор объявления, отмечаем комментарии как прочитанные
    if request.user.is_authenticated and request.user == ad.user:
        ad.comments.filter(is_read=False).update(is_read=True)
    
    # Формы для комментариев
    comment_form = AdCommentForm()
    reply_form = AdCommentReplyForm()
    
    context = {
        'ad': ad,
        'comments': comments,
        'comment_form': comment_form,
        'reply_form': reply_form,
    }
    return render(request, 'ads/ad_detail.html', context)

@login_required
def ad_create(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        image_formset = AdImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and image_formset.is_valid():
            # Проверяем, что добавлено хотя бы одно изображение
            has_images = any(
                image_form.cleaned_data and not image_form.cleaned_data.get('DELETE', False) and
                (image_form.cleaned_data.get('image_file') or image_form.cleaned_data.get('image_url'))
                for image_form in image_formset
            )
            
            if not has_images:
                messages.error(request, 'Необходимо добавить хотя бы одно изображение.')
                return render(request, 'ads/ad_form.html', {
                    'form': form,
                    'image_formset': image_formset,
                    'title': 'Создать объявление'
                })
            
            # Сохраняем объявление
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            
            # Обрабатываем изображения
            image_order = 0
            first_image = True
            for image_form in image_formset:
                if (image_form.cleaned_data and not image_form.cleaned_data.get('DELETE', False) and
                    (image_form.cleaned_data.get('image_file') or image_form.cleaned_data.get('image_url'))):
                    
                    image_file = image_form.cleaned_data.get('image_file')
                    image_url = image_form.cleaned_data.get('image_url')
                    is_main = image_form.cleaned_data.get('is_main', False)
                    
                    # Если не выбрано главное изображение явно, делаем первое главным
                    if first_image and not any(f.cleaned_data.get('is_main', False) for f in image_formset if f.cleaned_data):
                        is_main = True
                    
                    AdImage.objects.create(
                        ad=ad,
                        image_file=image_file,
                        image_url=image_url,
                        is_main=is_main,
                        order=image_order
                    )
                    
                    image_order += 1
                    first_image = False
            
            messages.success(request, 'Объявление успешно создано!')
            return redirect('ad_detail', pk=ad.pk)
        else:
            # Отладочная информация при ошибках валидации
            if not form.is_valid():
                print("Form errors:", form.errors)
            if not image_formset.is_valid():
                print("Formset errors:", image_formset.errors)
                print("Formset non form errors:", image_formset.non_form_errors())
    
    else:
        form = AdForm()
        image_formset = AdImageFormSet()
    
    return render(request, 'ads/ad_form.html', {
        'form': form,
        'image_formset': image_formset,
        'title': 'Создать объявление'
    })

@login_required
def ad_update(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if ad.user != request.user:
        messages.error(request, 'У вас нет прав на редактирование этого объявления.')
        return redirect('ad_detail', pk=pk)
        
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        image_formset = AdImageFormSet(request.POST, request.FILES)
        
        # Проверяем, были ли отмечены изображения для удаления
        images_to_delete = request.POST.getlist('delete_image')
        
        if form.is_valid() and image_formset.is_valid():
            ad = form.save()
            
            # Удаляем выбранные изображения
            if images_to_delete:
                for image_id in images_to_delete:
                    try:
                        image = AdImage.objects.get(id=image_id, ad=ad)
                        image.delete()
                        messages.info(request, f'Изображение успешно удалено')
                    except AdImage.DoesNotExist:
                        pass
            
            # Обрабатываем новые изображения из формсета
            added_images = 0
            for i, image_form in enumerate(image_formset):
                if (image_form.cleaned_data and not image_form.cleaned_data.get('DELETE', False) and
                    (image_form.cleaned_data.get('image_file') or image_form.cleaned_data.get('image_url'))):
                    
                    image_file = image_form.cleaned_data.get('image_file')
                    image_url = image_form.cleaned_data.get('image_url')
                    
                    # Получаем текущее количество изображений
                    current_count = ad.images.count()
                    
                    # Добавляем новое изображение только если не превышен лимит
                    if current_count < 5:
                        try:
                            AdImage.objects.create(
                                ad=ad,
                                image_file=image_file,
                                image_url=image_url,
                                is_main=(current_count == 0),
                                order=current_count
                            )
                            added_images += 1
                        except ValueError as e:
                            messages.warning(request, f'Не удалось добавить изображение: {str(e)}')
                    else:
                        messages.warning(request, 'Достигнуто максимальное количество изображений (5)')
                        break
            
            if added_images > 0:
                messages.success(request, f'Объявление обновлено! Добавлено изображений: {added_images}')
            else:
                messages.success(request, 'Объявление успешно обновлено!')
            return redirect('ad_detail', pk=pk)
    else:
        form = AdForm(instance=ad)
        image_formset = AdImageFormSet()
    
    # Передаем существующие изображения в контекст
    context = {
        'form': form,
        'image_formset': image_formset,
        'title': 'Редактировать объявление',
        'ad': ad,
        'existing_images': ad.images.all()
    }
    return render(request, 'ads/ad_form.html', context)

@login_required
def ad_delete(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if ad.user != request.user:
        messages.error(request, 'У вас нет прав на удаление этого объявления.')
        return redirect('ad_detail', pk=pk)
    
    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Объявление успешно удалено!')
        return redirect('profile')
    
    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Создаем профиль с дополнительными данными
            profile = UserProfile.objects.create(
                user=user,
                phone_number=form.cleaned_data.get('phone_number'),
                avatar=form.cleaned_data.get('avatar')
            )
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('ad_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'ads/register.html', {'form': form})

@login_required
def profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    user_ads = Ad.objects.filter(user=request.user).order_by('-created_at')
    
    # Добавляем информацию о завершенных обменах для каждого объявления
    for ad in user_ads:
        # Проверяем, есть ли завершенные обмены для этого объявления
        completed_exchange = ExchangeProposal.objects.filter(
            Q(ad_sender=ad) | Q(ad_receiver=ad),
            status='completed'
        ).first()
        ad.is_exchanged = completed_exchange is not None
        if completed_exchange:
            ad.exchange_date = completed_exchange.exchange_completed_at
    
    # Подсчет непрочитанных предложений
    unread_received = ExchangeProposal.objects.filter(
        ad_receiver__user=request.user, 
        is_read_by_receiver=False
    ).count()
    
    unread_sent = ExchangeProposal.objects.filter(
        ad_sender__user=request.user, 
        is_read_by_sender=False,
        status__in=['accepted', 'rejected', 'cancelled']
    ).count()
    
    context = {
        'profile': profile,
        'form': form,
        'user_ads': user_ads,
        'unread_received': unread_received,
        'unread_sent': unread_sent,
    }
    return render(request, 'ads/profile.html', context)

@login_required
def profile_edit(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                user_form.save()
                profile_form.save()
                messages.success(request, 'Профиль успешно обновлен!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {e}')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
        
        # Правильно форматируем дату рождения для input[type="date"]
        if profile.birth_date:
            profile_form.fields['birth_date'].widget.attrs['value'] = profile.birth_date.strftime('%Y-%m-%d')
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'ads/profile_edit.html', context)

def user_profile(request, user_id):
    """Просмотр профиля другого пользователя"""
    viewed_user = get_object_or_404(User, id=user_id)
    
    # Если это собственный профиль, перенаправляем на основную страницу профиля
    if request.user.is_authenticated and viewed_user == request.user:
        return redirect('profile')
    
    try:
        profile = viewed_user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=viewed_user)
    
    # Получаем объявления пользователя
    user_ads = Ad.objects.filter(user=viewed_user).order_by('-created_at')
    
    # Проверяем, заблокирован ли пользователь
    is_blocked = False
    if request.user.is_authenticated:
        is_blocked = UserBlock.objects.filter(
            Q(blocker=request.user, blocked=viewed_user) |
            Q(blocker=viewed_user, blocked=request.user)
        ).exists()
    
    context = {
        'viewed_user': viewed_user,
        'profile': profile,
        'user_ads': user_ads,
        'is_blocked': is_blocked,
    }
    return render(request, 'ads/user_profile.html', context)

@login_required
def proposal_list(request):
    proposal_type = request.GET.get('type', 'all')
    
    # Базовый queryset
    base_queryset = ExchangeProposal.objects.filter(
        Q(ad_sender__user=request.user) | Q(ad_receiver__user=request.user)
    ).select_related('ad_sender', 'ad_receiver', 'ad_sender__user', 'ad_receiver__user')
    
    # Фильтрация по типу
    if proposal_type == 'received':
        proposals = base_queryset.filter(ad_receiver__user=request.user)
        # Отмечаем как прочитанные получателем
        base_queryset.filter(ad_receiver__user=request.user, is_read_by_receiver=False).update(is_read_by_receiver=True)
    elif proposal_type == 'sent':
        proposals = base_queryset.filter(ad_sender__user=request.user)
        # Отмечаем как прочитанные отправителем
        base_queryset.filter(ad_sender__user=request.user, is_read_by_sender=False).update(is_read_by_sender=True)
    else:
        proposals = base_queryset
        # Отмечаем все как прочитанные
        base_queryset.filter(ad_receiver__user=request.user, is_read_by_receiver=False).update(is_read_by_receiver=True)
        base_queryset.filter(ad_sender__user=request.user, is_read_by_sender=False).update(is_read_by_sender=True)
    
    proposals = proposals.order_by('-created_at')
    
    # Подсчет непрочитанных для уведомлений
    unread_received = ExchangeProposal.objects.filter(
        ad_receiver__user=request.user, 
        is_read_by_receiver=False
    ).count()
    
    unread_sent = ExchangeProposal.objects.filter(
        ad_sender__user=request.user, 
        is_read_by_sender=False,
        status__in=['accepted', 'rejected']  # Только когда статус изменился
    ).count()
    
    context = {
        'proposals': proposals,
        'proposal_type': proposal_type,
        'unread_received': unread_received,
        'unread_sent': unread_sent,
    }
    return render(request, 'ads/proposal_list.html', context)

@login_required
def create_proposal(request, ad_id):
    ad_receiver = get_object_or_404(Ad, pk=ad_id)
    
    if ad_receiver.user == request.user:
        messages.error(request, 'Нельзя предложить обмен на собственное объявление')
        return redirect('ad_detail', pk=ad_id)
    
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        ad_sender_id = request.POST.get('ad_sender')
        
        if form.is_valid() and ad_sender_id:
            ad_sender = get_object_or_404(Ad, pk=ad_sender_id, user=request.user)
            proposal = form.save(commit=False)
            proposal.ad_sender = ad_sender
            proposal.ad_receiver = ad_receiver
            proposal.save()
            messages.success(request, 'Предложение обмена отправлено!')
            return redirect('proposal_list')
            
    else:
        form = ExchangeProposalForm()
    
    user_ads = Ad.objects.filter(user=request.user)
    context = {
        'form': form,
        'ad_receiver': ad_receiver,
        'user_ads': user_ads
    }
    return render(request, 'ads/proposal_form.html', context)

@login_required
def update_proposal_status(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, pk=proposal_id)
    
    action = request.POST.get('action')
    # Проверяем права доступа в зависимости от действия
    if action in ['accept', 'reject']:
        if proposal.ad_receiver.user != request.user:
            messages.error(request, 'У вас нет прав на изменение статуса этого предложения')
            return redirect('proposal_list')
    elif action == 'cancel':
        if proposal.ad_sender.user != request.user:
            messages.error(request, 'У вас нет прав на отмену этого предложения')
            return redirect('proposal_list')
        if not proposal.can_be_cancelled():
            messages.error(request, 'Это предложение уже нельзя отменить')
            return redirect('proposal_list')
    elif action == 'complete':
        # Проверка прав доступа для завершения обмена
        # Оба пользователя должны подтвердить получение товара
        if not proposal.sender_confirmed_exchange or not proposal.receiver_confirmed_exchange:
            messages.error(request, 'Обе стороны должны подтвердить получение товара перед завершением обмена')
            return redirect('proposal_list')
        
        # Проверяем, что пользователь участвует в обмене
        if request.user != proposal.ad_sender.user and request.user != proposal.ad_receiver.user:
            messages.error(request, 'У вас нет прав на завершение этого обмена')
            return redirect('proposal_list')
            
    # Выполняем действие
    if action == 'accept':
        proposal.status = 'accepted'
        proposal.is_read_by_sender = False  # Уведомляем отправителя
        # Изменяем статус объявлений на "в обмене"
        proposal.ad_sender.status = 'in_exchange'
        proposal.ad_receiver.status = 'in_exchange'
        proposal.ad_sender.save()
        proposal.ad_receiver.save()
        messages.success(request, 'Предложение обмена принято! Товары переведены в статус "В обмене".')
    elif action == 'reject':
        proposal.status = 'rejected'
        proposal.is_read_by_sender = False  # Уведомляем отправителя
        messages.success(request, 'Предложение обмена отклонено!')
    elif action == 'cancel':        
        proposal.status = 'cancelled'
        proposal.is_read_by_receiver = False  # Уведомляем получателя
        messages.success(request, 'Предложение обмена отменено!')
    elif action == 'complete':
        # Новое действие для завершения обмена
        if proposal.status != 'accepted':
            messages.error(request, 'Можно завершить только принятое предложение обмена.')
            return redirect('proposal_list')
            
        from django.utils import timezone
        
        proposal.status = 'completed'
        proposal.exchange_completed_at = timezone.now()  # Устанавливаем время завершения обмена
        
        # Изменяем статус объявлений на "обменен"
        proposal.ad_sender.status = 'exchanged'
        proposal.ad_receiver.status = 'exchanged'
        proposal.ad_sender.save()
        proposal.ad_receiver.save()
        messages.success(request, 'Обмен успешно завершен и отправлен в архив! Товары помечены как обмененные.')
    
    proposal.save()
    return redirect('proposal_list')

@login_required
def delete_ad_image(request, pk, image_id):
    """Удаление изображения объявления"""
    ad = get_object_or_404(Ad, pk=pk)
    if ad.user != request.user:
        messages.error(request, 'У вас нет прав на редактирование этого объявления.')
        return redirect('ad_detail', pk=pk)
    
    image = get_object_or_404(AdImage, id=image_id, ad=ad)
    
    if request.method == 'POST':
        # Если удаляемое изображение было главным, назначаем новое главное
        was_main = image.is_main
        image.delete()
        
        if was_main:
            first_remaining = ad.images.first()
            if first_remaining:
                first_remaining.is_main = True
                first_remaining.save()
        
        messages.success(request, 'Изображение успешно удалено!')
        return redirect('ad_update', pk=pk)
    
    return redirect('ad_update', pk=pk)

@login_required
def set_main_image(request, pk, image_id):
    """Установка главного изображения объявления"""
    ad = get_object_or_404(Ad, pk=pk)
    if ad.user != request.user:
        messages.error(request, 'У вас нет прав на редактирование этого объявления.')
        return redirect('ad_detail', pk=pk)
    
    image = get_object_or_404(AdImage, id=image_id, ad=ad)
    
    # Снимаем флаг главного с других изображений
    ad.images.update(is_main=False)
    
    # Получаем все изображения и обновляем их порядок
    all_images = list(ad.images.all().order_by('order'))
    
    # Удаляем выбранное изображение из списка
    all_images.remove(image)
    
    # Добавляем выбранное изображение в начало списка
    all_images.insert(0, image)
    
    # Обновляем порядок всех изображений
    for i, img in enumerate(all_images):
        img.order = i
        img.save()
    
    # Устанавливаем новое главное изображение
    image.is_main = True
    image.save()
    
    messages.success(request, 'Изображение установлено как главное и перемещено в начало!')
    return redirect('ad_update', pk=pk)

@login_required
def add_comment(request, ad_id):
    """Добавление комментария к объявлению"""
    ad = get_object_or_404(Ad, pk=ad_id)
    
    if request.method == 'POST':
        form = AdCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ad = ad
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
        else:
            messages.error(request, 'Ошибка при добавлении комментария.')
    
    return redirect('ad_detail', pk=ad_id)

@login_required
def reply_comment(request, comment_id):
    """Ответ на комментарий"""
    parent_comment = get_object_or_404(AdComment, pk=comment_id)
    
    if request.method == 'POST':
        form = AdCommentReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.ad = parent_comment.ad
            reply.author = request.user
            reply.parent = parent_comment
            reply.save()
            messages.success(request, 'Ответ добавлен!')
        else:
            messages.error(request, 'Ошибка при добавлении ответа.')
    
    return redirect('ad_detail', pk=parent_comment.ad.pk)

@login_required
def delete_comment(request, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(AdComment, pk=comment_id)
    
    # Проверяем права на удаление
    if not comment.can_delete(request.user):
        messages.error(request, 'У вас нет прав на удаление этого комментария.')
        return redirect('ad_detail', pk=comment.ad.pk)
    
    if request.method == 'POST':
        ad_pk = comment.ad.pk
        comment.delete()
        messages.success(request, 'Комментарий удален!')
        return redirect('ad_detail', pk=ad_pk)
    
    return redirect('ad_detail', pk=comment.ad.pk)

# API Views

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['created_at', 'title']

    def index(request):
        return render(request, 'index.html')

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


# Система личных сообщений

@login_required
def messages_list(request):
    """Список всех бесед пользователя"""
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related('participants', 'last_message__sender', 'last_message__receiver')
    
    for conversation in conversations:
        conversation.other_user = conversation.get_other_participant(request.user)
        conversation.unread_count = conversation.get_unread_count(request.user)
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'ads/messages_list.html', context)


@login_required
def conversation_detail(request, user_id):
    """Детальный вид беседы между двумя пользователями"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Проверяем, не заблокирован ли один из пользователей
    if UserBlock.objects.filter(
        Q(blocker=request.user, blocked=other_user) |
        Q(blocker=other_user, blocked=request.user)
    ).exists():
        messages.error(request, 'Невозможно отправить сообщение заблокированному пользователю.')
        return redirect('messages_list')
    
    # Получаем или создаем беседу
    conversation = None
    conversations = Conversation.objects.filter(participants=request.user).filter(participants=other_user)
    if conversations.exists():
        conversation = conversations.first()
    
    # Получаем сообщения между пользователями
    message_list = PrivateMessage.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')
    
    # AJAX запрос для получения новых сообщений
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'GET':
        last_message_id = int(request.GET.get('last_message_id', 0))
        new_messages = message_list.filter(id__gt=last_message_id)
        
        messages_data = []
        for msg in new_messages:
            messages_data.append({
                'id': msg.id,
                'content': msg.content,
                'is_sent': msg.sender == request.user,
                'formatted_time': msg.created_at.strftime('%H:%M'),
                'sender': msg.sender.username
            })
        
        return JsonResponse({
            'messages': messages_data,
            'last_message_id': message_list.last().id if message_list.exists() else 0
        })
    
    # AJAX запрос для отметки сообщений как прочитанных
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            if data.get('action') == 'mark_read':
                # Отмечаем полученные сообщения как прочитанные
                updated_count = PrivateMessage.objects.filter(
                    sender=other_user,
                    receiver=request.user,
                    is_read=False
                ).update(is_read=True)
                return JsonResponse({'status': 'success', 'updated_count': updated_count})
        except json.JSONDecodeError:
            pass
    
    # Отмечаем полученные сообщения как прочитанные
    PrivateMessage.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    if request.method == 'POST' and not request.headers.get('X-Requested-With'):
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = other_user
            message.subject = f"Re: Сообщение от {request.user.username}"
            message.save()
            
            # Создаем или обновляем беседу
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, other_user)
            
            conversation.last_message = message
            conversation.save()
            
            # AJAX ответ для отправки сообщения
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'is_sent': True,
                        'formatted_time': message.created_at.strftime('%H:%M')
                    }
                })
            
            messages.success(request, 'Сообщение отправлено!')
            return redirect('conversation_detail', user_id=user_id)
    else:
        form = MessageReplyForm()
    
    context = {
        'other_user': other_user,
        'messages': message_list,
        'form': form,
        'conversation': conversation,
    }
    return render(request, 'ads/conversation_detail.html', context)


@login_required
def send_message(request, user_id):
    """Отправка нового сообщения пользователю"""
    receiver = get_object_or_404(User, id=user_id)
    
    # Проверяем, не заблокирован ли один из пользователей
    if UserBlock.objects.filter(
        Q(blocker=request.user, blocked=receiver) |
        Q(blocker=receiver, blocked=request.user)
    ).exists():
        messages.error(request, 'Невозможно отправить сообщение заблокированному пользователю.')
        return redirect('profile')
    
    if request.method == 'POST':
        form = PrivateMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            
            # Создаем или обновляем беседу
            conversation = None
            conversations = Conversation.objects.filter(participants=request.user).filter(participants=receiver)
            if conversations.exists():
                conversation = conversations.first()
            else:
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, receiver)
            
            conversation.last_message = message
            conversation.save()
            
            messages.success(request, 'Сообщение отправлено!')
            return redirect('conversation_detail', user_id=receiver.id)
    else:
        form = PrivateMessageForm()
    
    context = {
        'form': form,
        'receiver': receiver,
    }
    return render(request, 'ads/send_message.html', context)


@login_required
def block_user(request, user_id):
    """Блокировка пользователя"""
    user_to_block = get_object_or_404(User, id=user_id)
    
    if user_to_block == request.user:
        messages.error(request, 'Вы не можете заблокировать самого себя.')
        return redirect('profile')
    
    if request.method == 'POST':
        form = UserBlockForm(request.POST)
        if form.is_valid():
            # Проверяем, не заблокирован ли уже пользователь
            if not UserBlock.objects.filter(blocker=request.user, blocked=user_to_block).exists():
                block = form.save(commit=False)
                block.blocker = request.user
                block.blocked = user_to_block
                block.save()
                messages.success(request, f'Пользователь {user_to_block.username} заблокирован.')
            else:
                messages.info(request, 'Пользователь уже заблокирован.')
            return redirect('profile')
    else:
        form = UserBlockForm()
    
    context = {
        'form': form,
        'user_to_block': user_to_block,
    }
    return render(request, 'ads/block_user.html', context)


@login_required
def unblock_user(request, user_id):
    """Разблокировка пользователя"""
    user_to_unblock = get_object_or_404(User, id=user_id)
    
    block = get_object_or_404(UserBlock, blocker=request.user, blocked=user_to_unblock)
    block.delete()
    
    messages.success(request, f'Пользователь {user_to_unblock.username} разблокирован.')
    return redirect('blocked_users')


@login_required
def blocked_users(request):
    """Список заблокированных пользователей"""
    blocked = UserBlock.objects.filter(blocker=request.user).select_related('blocked__userprofile')
    
    context = {
        'blocked_users': blocked,
    }
    return render(request, 'ads/blocked_users.html', context)

@login_required
def notifications_api(request):
    """API для получения количества непрочитанных уведомлений"""
    if request.method == 'GET':
        # Подсчет непрочитанных сообщений
        unread_messages_count = 0
        conversations = Conversation.objects.filter(
            participants=request.user
        ).distinct()
        
        for conversation in conversations:
            unread_messages_count += conversation.get_unread_count(request.user)
        
        # Подсчет непрочитанных предложений
        unread_proposals_count = ExchangeProposal.objects.filter(
            ad_receiver__user=request.user,
            is_read_by_receiver=False
        ).count()
        
        return JsonResponse({
            'unread_messages_count': unread_messages_count,
            'unread_proposals_count': unread_proposals_count,
            'status': 'success'
        })
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
def proposal_archive(request):
    """Архив завершенных обменов"""
    # Получаем только завершенные предложения
    proposals = ExchangeProposal.objects.filter(
        Q(ad_sender__user=request.user) | Q(ad_receiver__user=request.user),
        status='completed'
    ).select_related('ad_sender', 'ad_receiver', 'ad_sender__user', 'ad_receiver__user').order_by('-exchange_completed_at')
    
    context = {
        'proposals': proposals,
        'title': 'Архив обменов'
    }
    return render(request, 'ads/proposal_archive.html', context)

@login_required
def confirm_exchange(request, proposal_id):
    """Подтверждение обмена пользователем"""
    proposal = get_object_or_404(ExchangeProposal, pk=proposal_id)
    
    # Проверяем, что пользователь участвует в обмене
    if request.user not in [proposal.ad_sender.user, proposal.ad_receiver.user]:
        messages.error(request, 'У вас нет прав на подтверждение этого обмена')
        return redirect('proposal_list')
    
    # Проверяем, что обмен принят
    if proposal.status != 'accepted':
        messages.error(request, 'Обмен должен быть сначала принят')
        return redirect('proposal_list')
    
    if request.method == 'POST':
        # Подтверждаем обмен от имени текущего пользователя
        if request.user == proposal.ad_sender.user:
            proposal.confirm_exchange_by_sender()
            messages.success(request, 'Вы подтвердили получение товара!')
        elif request.user == proposal.ad_receiver.user:
            proposal.confirm_exchange_by_receiver()
            messages.success(request, 'Вы подтвердили получение товара!')
        
        # Проверяем, завершился ли обмен
        if proposal.is_exchanged():
            messages.success(request, 'Обмен успешно завершен! Товар перемещен в архив.')
        
        return redirect('proposal_list')
    
    # GET запрос - показываем форму подтверждения
    context = {
        'proposal': proposal,
        'user_can_confirm': proposal.can_confirm_exchange(request.user)
    }
    return render(request, 'ads/confirm_exchange.html', context)