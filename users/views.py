import hmac
import hashlib
import json
from urllib import parse
from urllib.parse import unquote, urlparse

from django.conf import settings
from django.contrib.auth import login

from rest_framework import permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response

from users.forms import FriendshipAction
from users.models import User, FriendshipRequest
from users.serializers import DetailUserSerializer, UserSerializer, FriendshipRequestSerializer

from knox.views import LoginView as KnoxLoginView


class TelegramLoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        tg_data = parse.parse_qs(request.data.get('user_data'))

        try:
            hash_str = tg_data['hash'][0]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not self.validate(hash_str, request.data.get('user_data'), settings.TELEGRAM_BOT_TOKEN):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_data = json.loads(tg_data['user'][0])
        telegram_id = user_data['id']
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            user = User.objects.create(
                email=f'{user_data['id']}@telegram.org',
                is_email_faked=True,
                telegram_id=user_data['id'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
            )
        login(request, user)
        return super(TelegramLoginView, self).post(request, format=format)

    def validate(self, hash_str, init_data, token, c_str="WebAppData"):
        """
        Validates the data received from the Telegram web app, using the
        method documented here:
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

        hash_str - the has string passed by the webapp
        init_data - the query string passed by the webapp
        token - Telegram bot's token
        c_str - constant string (default = "WebAppData")
        """

        init_data = sorted([chunk.split("=")
                            for chunk in unquote(init_data).split("&")
                            if chunk[:len("hash=")] != "hash="],
                           key=lambda x: x[0])
        init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

        secret_key = hmac.new(c_str.encode(), token.encode(),
                              hashlib.sha256).digest()
        data_check = hmac.new(secret_key, init_data.encode(),
                              hashlib.sha256)

        return data_check.hexdigest() == hash_str


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=format)


class UserView(RetrieveAPIView):
    model = User
    serializer_class = DetailUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'user_uuid'
    lookup_field = 'uuid'
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        form = FriendshipAction(request.data)
        if form.is_valid():
            user = self.get_object()
            friendship = user.friendship_with(request.user)
            reversed_friendship = request.user.friendship_with(user)
            if form.cleaned_data['action'] == 'remove_from_friends':
                if not friendship and not reversed_friendship:
                    return Response({'message': 'You are not friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
                friendship.delete()
                reversed_friendship.delete()
            if form.cleaned_data['action'] == 'send_request':
                if friendship or reversed_friendship:
                    return Response({'message': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
                FriendshipRequest.objects.create(
                    sender=self.request.user,
                    receiver=user,
                    comment=form.cleaned_data['comment'],
                )
            if form.cleaned_data['action'] == 'cancel_request':
                if friendship or reversed_friendship:
                    return Response({'message': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
                friendship_request = user.friendship_request_from(self.request.user)
                if not friendship_request:
                    return Response({'message': 'You have not sent a friendship request to this user'}, status=status.HTTP_400_BAD_REQUEST)
                friendship_request.delete()
            if form.cleaned_data['action'] == 'accept_request':
                if friendship or reversed_friendship:
                    return Response({'message': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
                friendship_request = request.user.friendship_request_from(user)
                if not friendship_request:
                    return Response({'message': 'You have not a friendship request from this user'}, status=status.HTTP_400_BAD_REQUEST)
                friendship_request.accept()
            if form.cleaned_data['action'] == 'reject_request':
                if friendship or reversed_friendship:
                    return Response({'message': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)
                friendship_request = request.user.friendship_request_from(user)
                if not friendship_request:
                    return Response({'message': 'You have not a friendship request from this user'}, status=status.HTTP_400_BAD_REQUEST)
                friendship_request.reject()
            return self.retrieve(request, *args, **kwargs)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthUserView(UserView):
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user


class UserFriendsView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.none()
        return self.request.user.friends.all()


class UserFriendRequestsView(ListAPIView):
    serializer_class = FriendshipRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return FriendshipRequest.objects.none()
        return self.request.user.friendship_requests()
