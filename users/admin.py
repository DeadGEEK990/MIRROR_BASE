from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    # Настройки отображения списка пользователей
    list_display = ('email', 'username', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')

    # Группировка полей при редактировании пользователя
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('username',)}),
        ('Статусы', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',),
        }),
        ('Права доступа', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    # Поля при создании нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    # Настройки для действий администратора
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)

    activate_users.short_description = "Активировать выбранных пользователей"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)

    deactivate_users.short_description = "Деактивировать выбранных пользователей"


admin.site.register(User, CustomUserAdmin)
