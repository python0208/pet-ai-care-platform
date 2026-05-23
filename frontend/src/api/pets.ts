import { request } from "@/api/request";
import type {
  HealthRecord,
  HealthRecordPayload,
  Pet,
  PetDetail,
  PetPayload,
  WeightRecord,
  WeightRecordPayload,
} from "@/types/pet";

export function getPets() {
  return request<Pet[]>("/pets/");
}

export function createPet(data: Partial<PetPayload>) {
  return request<PetDetail>("/pets/", {
    method: "POST",
    data,
    loading: true,
  });
}

export function getPet(id: number | string) {
  return request<PetDetail>(`/pets/${id}/`);
}

export function updatePet(id: number | string, data: Partial<PetPayload>) {
  return request<PetDetail>(`/pets/${id}/`, {
    method: "PATCH",
    data,
    loading: true,
  });
}

export function deletePet(id: number | string) {
  return request<Record<string, never>>(`/pets/${id}/`, {
    method: "DELETE",
    loading: true,
  });
}

export function getHealthRecords(petId: number | string, recordType?: string) {
  const query = recordType ? `?record_type=${recordType}` : "";
  return request<HealthRecord[]>(`/pets/${petId}/health-records/${query}`);
}

export function createHealthRecord(petId: number | string, data: Partial<HealthRecordPayload>) {
  return request<HealthRecord>(`/pets/${petId}/health-records/`, {
    method: "POST",
    data,
    loading: true,
  });
}

export function getHealthRecord(id: number | string) {
  return request<HealthRecord>(`/health-records/${id}/`);
}

export function updateHealthRecord(id: number | string, data: Partial<HealthRecordPayload>) {
  return request<HealthRecord>(`/health-records/${id}/`, {
    method: "PATCH",
    data,
    loading: true,
  });
}

export function deleteHealthRecord(id: number | string) {
  return request<Record<string, never>>(`/health-records/${id}/`, {
    method: "DELETE",
    loading: true,
  });
}

export function getWeightRecords(petId: number | string) {
  return request<WeightRecord[]>(`/pets/${petId}/weight-records/`);
}

export function createWeightRecord(petId: number | string, data: WeightRecordPayload) {
  return request<WeightRecord>(`/pets/${petId}/weight-records/`, {
    method: "POST",
    data,
    loading: true,
  });
}

export function deleteWeightRecord(id: number | string) {
  return request<Record<string, never>>(`/weight-records/${id}/`, {
    method: "DELETE",
    loading: true,
  });
}
