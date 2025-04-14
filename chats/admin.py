from django.contrib import admin
from .models import ChatRoom, Message
from django.utils.html import format_html
from django.urls import reverse


class ChatRoomAdmin(admin.ModelAdmin):
    # Настройки отображения списка чатов
    list_display = ('name', 'formatted_created_at', 'members_count', 'messages_count')
    list_filter = ('created_at',)
    search_fields = ('name', 'members__email', 'members__username')
    ordering = ('-created_at',)
    filter_horizontal = ('members',)
    readonly_fields = ('created_at',)

    # Группировка полей при редактировании
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Участники', {
            'fields': ('members',),
            'classes': ('collapse', 'wide'),
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    # Кастомные методы для отображения
    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    formatted_created_at.short_description = 'Дата создания'
    formatted_created_at.admin_order_field = 'created_at'

    def members_count(self, obj):
        return obj.members.count()

    members_count.short_description = 'Участников'

    def messages_count(self, obj):
        url = reverse('admin:chats_message_changelist') + f'?room__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj.messages.count())

    messages_count.short_description = 'Сообщений'

    # Действия администратора
    actions = ['clear_members']

    def clear_members(self, request, queryset):
        for chat in queryset:
            chat.members.clear()

    clear_members.short_description = "Очистить участников чатов"


class MessageAdmin(admin.ModelAdmin):
    # Настройки отображения списка сообщений
    list_display = ('short_content', 'room_link', 'sender_link', 'formatted_timestamp', 'read_status')
    list_filter = ('read', 'timestamp', 'room', 'sender')
    search_fields = ('content', 'room__name', 'sender__email', 'sender__username')
    ordering = ('-timestamp',)
    list_select_related = ('room', 'sender')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    # Группировка полей при редактировании
    fieldsets = (
        (None, {'fields': ('room', 'sender', 'content')}),
        ('Статус', {
            'fields': ('read',),
            'classes': ('collapse',),
        }),
        ('Дополнительно', {
            'fields': ('timestamp',),
            'classes': ('collapse',),
        }),
    )

    # Кастомные методы для отображения
    def short_content(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content

    short_content.short_description = 'Сообщение'

    def room_link(self, obj):
        url = reverse('admin:chats_chatroom_change', args=[obj.room.id])
        return format_html('<a href="{}">{}</a>', url, obj.room.name)

    room_link.short_description = 'Чат'
    room_link.admin_order_field = 'room__name'

    def sender_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.sender.id])
        return format_html('<a href="{}">{}</a>', url, obj.sender.username)

    sender_link.short_description = 'Отправитель'
    sender_link.admin_order_field = 'sender__username'

    def formatted_timestamp(self, obj):
        return obj.timestamp.strftime('%d.%m.%Y %H:%M')

    formatted_timestamp.short_description = 'Дата/время'
    formatted_timestamp.admin_order_field = 'timestamp'

    def read_status(self, obj):
        color = 'green' if obj.read else 'red'
        text = '✓ Прочитано' if obj.read else '✗ Не прочитано'
        return format_html('<span style="color: {};">{}</span>', color, text)

    read_status.short_description = 'Статус'

    # Действия администратора
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(read=True)

    mark_as_read.short_description = "Пометить как прочитанные"

    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)

    mark_as_unread.short_description = "Пометить как непрочитанные"


# Регистрация моделей
admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(Message, MessageAdmin)

# Настройки заголовков админки
admin.site.site_header = "Администрирование чат-системы"
admin.site.site_title = "Чат система"
admin.site.index_title = "Управление чатами и сообщениями"
