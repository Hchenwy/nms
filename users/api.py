from rest_framework import generics
from rest_framework_bulk import BulkModelViewSet
from common.mixins import IDInFilterMixin
from .permissions import IsSuperUser
from .models import User, UserGroup
from . import serializers


class UserViewSet(IDInFilterMixin, BulkModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (IsSuperUser,)
    # filter_backends = (DjangoFilterBackend,)
    filter_fields = ('username', 'email', 'name', 'id')

class UserGroupViewSet(IDInFilterMixin, BulkModelViewSet):
    queryset = UserGroup.objects.all()
    serializer_class = serializers.UserGroupSerializer


class UserResetPasswordApi(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def perform_update(self, serializer):
        # Note: we are not updating the user object here.
        # We just do the reset-password stuff.
        import uuid
        from .utils import send_reset_password_mail
        user = self.get_object()
        user.password_raw = str(uuid.uuid4())
        user.save()
        send_reset_password_mail(user)