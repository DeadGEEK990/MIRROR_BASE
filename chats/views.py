from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatRoom, Message
from .forms import ChatRoomForm, ChatRoomFormSet, MessageFormSet, MessageForm

@login_required
def chat_main(request):
    return render(request, 'chats/chat_list.html')


@login_required
def get_chat(request, chat_id):
    chat = get_object_or_404(ChatRoom, id=chat_id, members=request.user)
    # Получаем последние 50 сообщений и создаем формсет
    messages = Message.objects.filter(room=chat).order_by('-timestamp')[:50]
    formset = MessageFormSet(queryset=messages)
    return render(request, 'chats/messages_partial.html', {'formset': formset})

@login_required
def send_message(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(ChatRoom, id=chat_id, members=request.user)
        Message.objects.create(
            room=chat,
            sender=request.user,
            content=request.POST.get('text')
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def chat_create(request):
    if request.method == "POST":
        form = ChatRoomForm(request.POST)
        if form.is_valid():
            chat = form.save(commit=False)
            chat.save()
            form.save_m2m()  # Для сохранения many-to-many (members)
            chat.members.add(request.user)
            return redirect('chat_list')  # Или другой ваш URL
    else:
        form = ChatRoomForm()

    return render(request, 'chats/create_chat.html', {'form': form})
