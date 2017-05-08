# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from i2x.buildmyteam.serializers import (
    UserSerializer,
    GroupSerializer,
    TeamSerializer,
    # TeamMembersSerializer
)
from .models import Team
from rest_framework.decorators import api_view, detail_route, list_route
from django.core.mail import send_mail
from permissions import IsOwnerOrReadOnly
from ..utility import *


# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    """
    Endpoint allows users to be created/retrieved/updated/destroyed
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewset(viewsets.ModelViewSet):
    """ 
    Endpoint allows groups to be created/retrieved/updated/destroyed
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TeamViewset(viewsets.ModelViewSet):
    """
    Endpoint allows teams to be created/retrieved/updated/destroyed
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    @list_route()
    def test(self, request):
        """
        Testing framework
        :param request: 
        :return: 
        """

        teams = Team.objects.all()
        serializer = self.get_serializer(teams, many=True)

        subject = "Test email"
        message = "This is a test message"
        from_email = "vivek.d.techi@gmail.com"
        recipient = "vivekrajan555@gmail.com"

        send_mail(subject, message, from_email, [recipient], fail_silently=False)

        return Response(serializer.data)

    @detail_route(methods=['get', 'post'], serializer_class=TeamSerializer)
    def add_member(self, request, pk=None):
        """
        This adds your team
        :param request: default
        :param pk: primary key of Team
        :return: returns the team corresponds to Primary Key for GET
                 returns the team after adding team member for POST
        """
        # team = self.get_object()

        # serializer = TeamSerializer

        if request.method == "GET":

            queryset = Team.objects.all().get(id=pk)
            serializer = self.get_serializer(queryset)
            # serializer = TeamSerializer(queryset, context={'request': request})
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                # team.set_password(serializer.data['password'])
                serializer.save()
                return Response({'status': 'member added'})
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

    # def get_serializer(self, *args, **kwargs):
    #
    #     """
    #     Return the serializer instance that should be used for validating and
    #     deserializing input, and for serializing output.
    #     """
    #
    #     serializer_class = TeamSerializer
    #     # kwargs['context'] = self.get_serializer_context()
    #     return serializer_class(*args, **kwargs)


class AddTeamMemberView(APIView):
    metadata_class = Team
    permission_classes = [IsOwnerOrReadOnly]

    # def get_serializer(self, *args, **kwargs):
    #     """
    #     Return the serializer instance that should be used for validating and
    #     deserializing input, and for serializing output.
    #     """
    #     serializer_class = TeamMembersSerializer
    #     # kwargs['context'] = self.get_serializer_context()
    #     return serializer_class(*args, **kwargs)

    def post(self, request, format=None):
        serializer = TeamSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['POST'])
def register(request):
    username = request.data["username"]
    email = request.data["email"]
    password = request.data["password"]
    verification_code = get_random_code()

    data = dict(username=username, email=email, password=password)

    serializer_context = {
        'request': request,
        'code': verification_code
    }

    serializer = UserSerializer(data=data, context=serializer_context)
    if serializer.is_valid():
        serializer.save()
        mail_success = send_registration_mail(username, email, verification_code)
        combined_result = dict(serializer.data.items() + {'mail_success': mail_success}.items())
        return Response(combined_result, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
