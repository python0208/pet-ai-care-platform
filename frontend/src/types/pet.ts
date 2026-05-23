export type PetSpecies = "cat" | "dog" | "other";
export type PetGender = "male" | "female" | "unknown";
export type HealthRecordType = "vaccine" | "deworm" | "medical" | "allergy" | "other";

export interface Pet {
  id: number;
  name: string;
  species: PetSpecies;
  breed: string;
  gender: PetGender;
  birthday: string | null;
  avatar: string;
  color: string;
  weight: string | null;
  neutered: boolean;
  remark: string;
  created_at: string;
  updated_at: string;
}

export interface HealthRecord {
  id: number;
  record_type: HealthRecordType;
  title: string;
  record_date: string;
  next_remind_date: string | null;
  hospital: string;
  doctor: string;
  cost: string | null;
  description: string;
  attachments: string[];
  created_at: string;
  updated_at: string;
}

export interface WeightRecord {
  id: number;
  weight: string;
  record_date: string;
  remark: string;
  created_at: string;
}

export interface PetReminder {
  record_type: HealthRecordType;
  title: string;
  next_remind_date: string;
  days_until: number;
}

export interface PetRecordStats {
  vaccine_count: number;
  deworm_status: string;
  current_weight: string;
}

export interface PetDetail extends Pet {
  latest_vaccine_record: HealthRecord | null;
  latest_deworm_record: HealthRecord | null;
  latest_weight_record: WeightRecord | null;
  reminders: PetReminder[];
  record_stats: PetRecordStats;
}

export type PetPayload = Omit<
  Pet,
  "id" | "created_at" | "updated_at" | "weight"
> & {
  weight?: string | null;
};

export type HealthRecordPayload = Omit<
  HealthRecord,
  "id" | "created_at" | "updated_at" | "attachments" | "cost"
> & {
  cost?: string | null;
  attachments?: string[];
};

export interface WeightRecordPayload {
  weight: string;
  record_date: string;
  remark?: string;
}
