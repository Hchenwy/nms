from rest_framework import serializers
from rest_framework_bulk import BulkListSerializer, BulkSerializerMixin
from .models import User, UserGroup




class UserSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    groups_display = serializers.SerializerMethodField()
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=UserGroup.objects.all())

    class Meta:
        model = User
        list_serializer_class = BulkListSerializer
        exclude = ['first_name', 'last_name', 'password']

    def get_field_names(self, declared_fields, info):
        fields = super(UserSerializer, self).get_field_names(declared_fields, info)
        fields.extend(['groups_display', 'get_role_display', 'is_valid'])
        return fields

    @staticmethod
    def get_groups_display(obj):
        return " ".join([group.name for group in obj.groups.all()])


class UserGroupSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    user_amount = serializers.SerializerMethodField()

    class Meta:
        model = UserGroup
        list_serializer_class = BulkListSerializer
        fields = '__all__'

    @staticmethod
    def get_user_amount(obj):
        return obj.users.count()