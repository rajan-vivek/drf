# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.urlresolvers import reverse
from models import Team, UserVerification
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create your tests here.


class TeamModelTestCase(TestCase):
    """This class defines the test suite for Team model"""

    def setUp(self):
        """Define the test client and other test variables"""
        user = User.objects.create(username="vivek555@gmail.com")
        self.team_name = "Barcelona"
        self.team1 = Team(name=self.team_name, owner=user)

        self.team_name2 = "ManchesterUnited"
        self.members = [User.objects.create(username="mcb12345@gmail.com"),
                        User.objects.create(username="mcb54321@gmail.com")]
        self.team2 = Team(name=self.team_name2, owner=user)

    def test_model_can_create_a_team(self):
        """Test if Team model can create a team"""
        old_count = Team.objects.count()
        self.team1.save()
        new_count = Team.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_returns_readable_repr(self):
        """Test a readable representation returned from model"""
        self.assertEqual(str(self.team1), self.team_name)

    def test_model_add_team_members(self):
        """Test if team members can be added into team"""
        old_count = Team.objects.count()
        self.team2.save()
        new_count = Team.objects.count()
        self.assertNotEqual(old_count, new_count)

        self.team2.members = self.members
        self.team2.save()

        latest_team = Team.objects.get(id=self.team2.id)
        latest_team_members = [member for member in latest_team.members.all()]

        self.assertListEqual(latest_team_members, self.members)


class UserVerificationTestCase(TestCase):
    """This class defines the test suite for UserVerification model"""

    def setUp(self):
        """Define the test client and other test variables"""

        self.username = "vivek12345@gmail.com"
        user = User.objects.create(username=self.username)
        self.name = "Verification code for user:" + str(user.id)
        self.code = "TESTING100"

        self.user_verification = UserVerification(user=user, code=self.code)

    def test_model_can_create_a_verification_code(self):
        """Test if UserVerification model can save a verification code"""

        old_count = UserVerification.objects.count()
        self.user_verification.save()
        new_count = UserVerification.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_can_retrieve_a_verification_code(self):
        """Test if UserVerification model can retrieve same code for user"""

        self.user_verification.save()
        user = User.objects.get(username=self.username)

        self.assertEqual(user.verification.code, self.code)


class GeneralViewTestCase(TestCase):
    """Test suite for User api views"""

    def setUp(self):
        """Define the test client and other test variables"""

        self.email = "mcb00@gmail.com"
        self.password = "123456"
        user = User.objects.create(username=self.email, email=self.email, password=self.password)

        # Initialize client and force it to use authentication
        # self.client = APIClient()
        # self.client.force_authenticate(user=user)
        # self.client.login(username=self.email, password=self.password)

        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.team_name = 'Asana'
        self.user_url = "http://127.0.0.1:8000/users/" + str(user.id) + "/"  # FIXME: better soln ?

        team = Team.objects.create(name=self.team_name, owner=user)
        # self.add_member_data = {
        #                         'owner': self.user_url,
        #                         'members_emails': "mcb11@gmail.com, mcb22@gmail.com"
        #                         }
        # self.add_member_response = self.client.put('/add-member/' + str(team.id),
        #                                            self.add_member_data,
        #                                            format="json")

        self.response = self.client.get("/users/", format="json")


    def test_api_can_add_member_to_team(self):
        """Test if members can be added into the team"""
        self.assertEqual(self.add_member_response.status_code, status.HTTP_201_CREATED)
