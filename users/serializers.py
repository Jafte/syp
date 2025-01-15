from rest_framework import serializers

from users.models import User, FriendshipRequest, Friendship


class UserSerializer(serializers.ModelSerializer):
    friends_count = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['uuid', 'email', 'first_name', 'last_name', 'friends_count', 'created_at']
        read_only_fields = ('uuid', 'friends_count', 'created_at')


    def get_friends_count(self, user):
        return user.friends.count()

class DetailUserSerializer(serializers.ModelSerializer):
    can_be_added_as_a_friend = serializers.SerializerMethodField()
    friendship_request_from = serializers.SerializerMethodField()
    friendship_request_to = serializers.SerializerMethodField()
    friendship = serializers.SerializerMethodField()
    friends_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'uuid',
            'email',
            'first_name',
            'last_name',
            'created_at',
            'can_be_added_as_a_friend',
            'friendship_request_from',
            'friendship_request_to',
            'friendship',
            'friends_count',
        ]
        read_only_fields = ('uuid', 'created_at', 'friends_count')

    def get_can_be_added_as_a_friend(self, user):
        if not self.context['request'].user.is_authenticated:
            return False
        return self.context['request'].user.uuid != user.uuid

    def get_friendship_request_from(self, user):
        if not self.context['request'].user.is_authenticated:
            return None
        if self.context['request'].user.uuid == user.uuid:
            return None
        friendship_request = user.friendship_request_to(self.context['request'].user)
        if not friendship_request:
            return None
        return FriendshipRequestSerializer(friendship_request).data

    def get_friendship_request_to(self, user):
        if not self.context['request'].user.is_authenticated:
            return None
        if self.context['request'].user.uuid == user.uuid:
            return None
        friendship_request = user.friendship_request_from(self.context['request'].user)
        if not friendship_request:
            return None
        return FriendshipRequestSerializer(friendship_request).data

    def get_friendship(self, user):
        if not self.context['request'].user.is_authenticated:
            return None
        if self.context['request'].user.uuid == user.uuid:
            return None
        friendship = user.friendship_with(self.context['request'].user)
        if not friendship:
            return None
        return FriendshipSerializer(friendship).data

    def get_friends_count(self, user):
        return user.friends.count()


class FriendshipRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()
    class Meta:
        model = FriendshipRequest
        fields = ['sender', 'receiver', 'created_at', 'comment', 'accepted_at', 'rejected_at']


class FriendshipSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    friend = UserSerializer()
    class Meta:
        model = Friendship
        fields = ['user', 'friend', 'created_at']
