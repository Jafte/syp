from django.contrib.auth import login

from rest_framework import permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response

from users.forms import FriendshipAction
from users.models import User, FriendshipRequest
from users.serializers import DetailUserSerializer, UserSerializer, FriendshipRequestSerializer

from knox.views import LoginView as KnoxLoginView


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
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
