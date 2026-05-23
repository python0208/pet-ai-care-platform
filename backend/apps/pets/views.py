from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.views import APIView

from apps.common.responses import success_response
from apps.pets.models import HealthRecord, Pet, WeightRecord
from apps.pets.serializers import (
    HealthRecordSerializer,
    PetDetailSerializer,
    PetSerializer,
    WeightRecordSerializer,
)


def get_owned_pet(user, pet_id):
    return get_object_or_404(Pet, id=pet_id, owner=user)


def get_owned_health_record(user, record_id):
    return get_object_or_404(
        HealthRecord.objects.select_related("pet"),
        id=record_id,
        pet__owner=user,
    )


def get_owned_weight_record(user, record_id):
    return get_object_or_404(
        WeightRecord.objects.select_related("pet"),
        id=record_id,
        pet__owner=user,
    )


class PetListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pets = Pet.objects.filter(owner=request.user).order_by("-updated_at", "-created_at")
        return success_response(PetSerializer(pets, many=True).data)

    def post(self, request):
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pet = serializer.save(owner=request.user)
        return success_response(PetDetailSerializer(pet).data, status=status.HTTP_201_CREATED)


class PetDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        pet = get_owned_pet(request.user, pk)
        return success_response(PetDetailSerializer(pet).data)

    def put(self, request, pk):
        pet = get_owned_pet(request.user, pk)
        serializer = PetSerializer(pet, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(PetDetailSerializer(pet).data)

    def patch(self, request, pk):
        pet = get_owned_pet(request.user, pk)
        serializer = PetSerializer(pet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(PetDetailSerializer(pet).data)

    def delete(self, request, pk):
        pet = get_owned_pet(request.user, pk)
        pet.delete()
        return success_response({})


class PetHealthRecordListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pet_id):
        pet = get_owned_pet(request.user, pet_id)
        records = pet.health_records.all()
        record_type = request.query_params.get("record_type")
        if record_type:
            records = records.filter(record_type=record_type)
        return success_response(HealthRecordSerializer(records, many=True).data)

    def post(self, request, pet_id):
        pet = get_owned_pet(request.user, pet_id)
        serializer = HealthRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = serializer.save(pet=pet)
        return success_response(
            HealthRecordSerializer(record).data,
            status=status.HTTP_201_CREATED,
        )


class HealthRecordDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        record = get_owned_health_record(request.user, pk)
        return success_response(HealthRecordSerializer(record).data)

    def put(self, request, pk):
        record = get_owned_health_record(request.user, pk)
        serializer = HealthRecordSerializer(record, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(HealthRecordSerializer(record).data)

    def patch(self, request, pk):
        record = get_owned_health_record(request.user, pk)
        serializer = HealthRecordSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(HealthRecordSerializer(record).data)

    def delete(self, request, pk):
        record = get_owned_health_record(request.user, pk)
        record.delete()
        return success_response({})


class PetWeightRecordListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pet_id):
        pet = get_owned_pet(request.user, pet_id)
        return success_response(WeightRecordSerializer(pet.weight_records.all(), many=True).data)

    def post(self, request, pet_id):
        pet = get_owned_pet(request.user, pet_id)
        serializer = WeightRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = serializer.save(pet=pet)
        pet.weight = record.weight
        pet.save(update_fields=["weight", "updated_at"])
        return success_response(
            WeightRecordSerializer(record).data,
            status=status.HTTP_201_CREATED,
        )


class WeightRecordDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        record = get_owned_weight_record(request.user, pk)
        record.delete()
        return success_response({})
