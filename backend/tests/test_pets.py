from datetime import date, timedelta

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.pets.models import HealthRecord, Pet, WeightRecord
from apps.users.models import User


class PetApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="pet-owner@example.com",
            password="StrongPass123",
            nickname="豆豆家长",
        )
        self.other_user = User.objects.create_user(
            email="other-owner@example.com",
            password="StrongPass123",
            nickname="别的家长",
        )

    def authenticate(self, user=None):
        token = RefreshToken.for_user(user or self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def create_pet(self, owner=None, name="豆豆"):
        return Pet.objects.create(
            owner=owner or self.user,
            name=name,
            species=Pet.Species.CAT,
            breed="英短金渐层",
            gender=Pet.Gender.MALE,
            birthday=date(2024, 1, 1),
            weight="4.60",
            neutered=True,
        )

    def pet_payload(self, name="豆豆"):
        return {
            "name": name,
            "species": "cat",
            "breed": "英短金渐层",
            "gender": "male",
            "birthday": "2024-01-01",
            "avatar": "",
            "color": "金色",
            "weight": "4.60",
            "neutered": True,
            "remark": "爱睡觉",
        }

    def test_anonymous_cannot_access_pets(self):
        response = self.client.get(reverse("pet-list"))

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_create_pet(self):
        self.authenticate()
        response = self.client.post(reverse("pet-list"), self.pet_payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["code"], 0)
        pet = Pet.objects.get(id=response.json()["data"]["id"])
        self.assertEqual(pet.owner, self.user)

    def test_user_can_view_own_pet_list(self):
        self.create_pet()
        self.create_pet(owner=self.other_user, name="花花")
        self.authenticate()

        response = self.client.get(reverse("pet-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(response.json()["data"][0]["name"], "豆豆")

    def test_user_can_update_own_pet(self):
        pet = self.create_pet()
        self.authenticate()

        response = self.client.patch(
            reverse("pet-detail", args=[pet.id]),
            {"name": "团团", "weight": "4.80"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        pet.refresh_from_db()
        self.assertEqual(pet.name, "团团")
        self.assertEqual(str(pet.weight), "4.80")

    def test_user_can_delete_own_pet(self):
        pet = self.create_pet()
        self.authenticate()

        response = self.client.delete(reverse("pet-detail", args=[pet.id]))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Pet.objects.filter(id=pet.id).exists())

    def test_user_cannot_view_other_users_pet_detail(self):
        pet = self.create_pet(owner=self.other_user)
        self.authenticate()

        response = self.client.get(reverse("pet-detail", args=[pet.id]))

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_update_other_users_pet(self):
        pet = self.create_pet(owner=self.other_user)
        self.authenticate()

        response = self.client.patch(
            reverse("pet-detail", args=[pet.id]),
            {"name": "不该成功"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_other_users_pet(self):
        pet = self.create_pet(owner=self.other_user)
        self.authenticate()

        response = self.client.delete(reverse("pet-detail", args=[pet.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Pet.objects.filter(id=pet.id).exists())

    def test_user_can_add_health_record_to_own_pet(self):
        pet = self.create_pet()
        self.authenticate()

        response = self.client.post(
            reverse("pet-health-record-list", args=[pet.id]),
            {
                "record_type": "vaccine",
                "title": "猫三联",
                "record_date": "2026-05-01",
                "next_remind_date": (
                    date.today() + timedelta(days=15)
                ).isoformat(),
                "hospital": "星球宠物医院",
                "doctor": "李医生",
                "cost": "120.00",
                "description": "接种正常",
                "attachments": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(HealthRecord.objects.filter(pet=pet).count(), 1)

    def test_user_cannot_add_health_record_to_other_users_pet(self):
        pet = self.create_pet(owner=self.other_user)
        self.authenticate()

        response = self.client.post(
            reverse("pet-health-record-list", args=[pet.id]),
            {
                "record_type": "deworm",
                "title": "体内驱虫",
                "record_date": "2026-05-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(HealthRecord.objects.count(), 0)

    def test_user_can_add_weight_record(self):
        pet = self.create_pet()
        self.authenticate()

        response = self.client.post(
            reverse("pet-weight-record-list", args=[pet.id]),
            {"weight": "4.70", "record_date": "2026-05-23", "remark": "饭前"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(WeightRecord.objects.filter(pet=pet).count(), 1)
        pet.refresh_from_db()
        self.assertEqual(str(pet.weight), "4.70")

    def test_user_cannot_access_other_users_weight_records(self):
        pet = self.create_pet(owner=self.other_user)
        WeightRecord.objects.create(pet=pet, weight="5.10", record_date="2026-05-23")
        self.authenticate()

        response = self.client.get(reverse("pet-weight-record-list", args=[pet.id]))

        self.assertEqual(response.status_code, 404)
