from django.urls import path

from apps.pets.views import (
    HealthRecordDetailView,
    PetDetailView,
    PetHealthRecordListCreateView,
    PetListCreateView,
    PetWeightRecordListCreateView,
    WeightRecordDeleteView,
)

urlpatterns = [
    path("pets/", PetListCreateView.as_view(), name="pet-list"),
    path("pets/<int:pk>/", PetDetailView.as_view(), name="pet-detail"),
    path(
        "pets/<int:pet_id>/health-records/",
        PetHealthRecordListCreateView.as_view(),
        name="pet-health-record-list",
    ),
    path(
        "health-records/<int:pk>/",
        HealthRecordDetailView.as_view(),
        name="health-record-detail",
    ),
    path(
        "pets/<int:pet_id>/weight-records/",
        PetWeightRecordListCreateView.as_view(),
        name="pet-weight-record-list",
    ),
    path(
        "weight-records/<int:pk>/",
        WeightRecordDeleteView.as_view(),
        name="weight-record-detail",
    ),
]
