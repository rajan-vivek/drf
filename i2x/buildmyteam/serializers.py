from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Team, UserVerification
from ..utility import *
from django.db.models.fields import PositiveIntegerField
from rest_framework.renderers import JSONRenderer


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'password', 'email', 'groups',)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        code = self.context['code']

        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)

        instance.save()
        UserVerification.objects.create(user_id=instance.id, code=code)

        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class TeamSerializer(serializers.HyperlinkedModelSerializer):

    # members = UserSerializer(many=True, read_only=False, allow_null=True)
    # members = serializers.SerializerMethodField()
    # members_email = serializers.ReadOnlyField()

    class Meta:
        model = Team
        fields = ('name', 'description', 'owner', 'members_emails')

    def create(self, validated_data):
        members_emails = self.context['request'].data['members_emails']
        # instance = Team.objects.create(**validated_data)
        instance = self.Meta.model(**validated_data)

        emails_string = members_emails.strip()

        if emails_string:  # check for empty
            emails_list = [email.strip() for email in emails_string.split(",")]  # remove spaces

            members = []
            for email in emails_list:
                if is_valid_email(email):  # [0] is used because get_or_create returns the tuple
                    members.append(User.objects.get_or_create(username=email, email=email)[0])

            instance.members = members

        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.owner = validated_data.get('owner', instance.owner)
        # instance.members_emails = validated_data.get('members_emails', instance.members_emails)

        members_emails = self.context['request'].data['members_emails']
        emails_string = members_emails.strip()

        if emails_string:   # check for empty
            emails_list = [email.strip() for email in emails_string.split(",")]  # remove spaces

            members = []
            for email in emails_list:
                if is_valid_email(email):   # [0] is used because get_or_create returns the tuple
                    members.append(User.objects.get_or_create(username=email, email=email)[0])

            instance.members = members

        instance.save()
        return instance

    def get_members(self, obj):
        """
        :param obj: current value
        :return: List of users
        """

        if not obj.members.exists():
            return []

        users = []

        for member in obj.members.all():
            users.append(User.objects.all().get(email=member.email))

        serializer_context = {
            'request': self.context['request']
        }

        serializer_users = UserSerializer(users, many=True, context=serializer_context)

        return serializer_users.data  # JSONRenderer().render(serializer_users.data)

    def validate_members_emails(self, value):
        """
        Check that the blog post is about Django.
        """
        # if 'django' not in value.lower():
        #     raise serializers.ValidationError("Blog post is not about Django")
        return value


class MemberField(serializers.Field):
    """
    Member objects are serialized into Users list
    """

    def to_representation(self, obj):
        return UserSerializer(obj)

    def to_internal_value(self, data):
        return User(username=data.username, email=data.email)

# class TeamMembersSerializer(serializers.ModelSerializer):
#
#     user_id = PositiveIntegerField()
#     team_id = PositiveIntegerField()
#
#     class Meta:
#         model = User
#         fields = ('user_id', 'team_id')


