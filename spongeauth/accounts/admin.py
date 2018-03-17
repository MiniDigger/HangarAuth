from django.contrib import admin
from django.contrib.admin import widgets
from django import forms
import django.contrib.auth.admin
import django.contrib.auth.forms
import django.contrib.auth.models
from django.utils import timezone

from . import models


class AdminUserChangeForm(forms.ModelForm):
    password = django.contrib.auth.forms.ReadOnlyPasswordHashField(
        help_text="Raw passwords are not stored, so there is no way to see "
                  "this user's password, but you can change the password "
                  "using <a href=\"../password/\">this form</a>."
    )

    groups = forms.ModelMultipleChoiceField(
        queryset=models.Group.objects.all(),
        required=False,
        widget=widgets.FilteredSelectMultiple('groups', False),
    )

    def __init__(self, *args, **kwargs):
        super(AdminUserChangeForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.all()

    def save_m2m(self):
        self.instance.groups.set(self.cleaned_data['groups'])

    def save(self, *args, **kwargs):
        instance = super().save()
        self.save_m2m()
        return instance

    def clean_password(self):
        return self.initial['password']

    class Meta:
        model = models.User
        fields = (
            'username', 'password', 'email', 'email_verified', 'is_active', 'current_avatar', 'twofa_enabled',
            'is_admin', 'is_staff', 'groups',
            'mc_username', 'irc_nick', 'gh_username')


class UserAdmin(django.contrib.auth.admin.UserAdmin):
    raw_id_fields = ("current_avatar",)
    fieldsets = (
        (None, {
            'fields': (
                'username', 'password', 'email', 'email_verified',
                'is_active', 'is_admin', 'is_staff', 'current_avatar', 'twofa_enabled'),
        }),
        ('Groups', {
            'classes': ('collapse',),
            'fields': ('groups',),
        }),
        ('Profile fields', {
            'classes': ('collapse',),
            'fields': ('mc_username', 'irc_nick', 'gh_username'),
        }),
    )
    filter_horizontal = ()
    list_display = ('username', 'email', 'is_active', 'twofa_enabled')
    list_filter = ('is_admin', 'twofa_enabled')
    search_fields = ['username', 'email']
    form = AdminUserChangeForm

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_admin:
            return self.readonly_fields

        if obj and not obj.is_admin:
            return self.readonly_fields + ('is_admin', 'is_staff')

        return list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ))

    def delete_model(self, request, obj):
        obj.deleted_at = timezone.now()
        obj.is_active = False
        obj.save()


class AvatarAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)


class ExternalAuthenticatorAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = models.Group
        exclude = []

    users = forms.ModelMultipleChoiceField(
        queryset=models.User.objects.all(),
        required=False,
        widget=widgets.FilteredSelectMultiple('users', False),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        instance = super(GroupAdminForm, self).save()
        self.save_m2m()
        return instance


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'internal_only')
    list_filter = ('internal_only',)
    search_fields = ('name',)

    form = GroupAdminForm


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Avatar, AvatarAdmin)
admin.site.register(models.ExternalAuthenticator, ExternalAuthenticatorAdmin)

admin.site.unregister(django.contrib.auth.models.Group)
