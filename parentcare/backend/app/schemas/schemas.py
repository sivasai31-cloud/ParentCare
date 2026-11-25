from datetime import datetime, timezone
from typing import Optional, List, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator

# --- AUTH & USER SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: Optional[str] = "USER"

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str
    # In dev mode, the reset token is returned so it can be used without email.
    # In production this would be omitted and emailed instead.
    reset_token: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


# --- PARENT SCHEMAS ---
class ParentBase(BaseModel):
    name: str = Field(..., min_length=1)
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    emergency_notes: Optional[str] = None
    avatar_url: Optional[str] = None

class ParentCreate(ParentBase):
    pass

class ParentUpdate(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    emergency_notes: Optional[str] = None
    avatar_url: Optional[str] = None

class ParentResponse(ParentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


# --- MEDICINE SCHEMAS ---
class MedicineBase(BaseModel):
    parent_id: int
    name: str = Field(..., min_length=1)
    dosage: str
    frequency: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    instructions: Optional[str] = None
    status: Optional[str] = "active"

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    instructions: Optional[str] = None
    status: Optional[str] = None

class MedicineResponse(MedicineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    parent_name: Optional[str] = None


# --- APPOINTMENT SCHEMAS ---
class AppointmentBase(BaseModel):
    parent_id: int
    doctor_name: str = Field(..., min_length=1)
    hospital_clinic: str = Field(..., min_length=1)
    appointment_date: str # YYYY-MM-DD
    appointment_time: str # HH:MM
    purpose: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "upcoming"

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    doctor_name: Optional[str] = None
    hospital_clinic: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    parent_name: Optional[str] = None


# --- MEDICAL REPORT SCHEMAS ---
class MedicalReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: int
    uploader_id: int
    title: str
    report_type: str
    file_path: str
    original_filename: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    parent_name: Optional[str] = None


# --- EMERGENCY CONTACT SCHEMAS ---
class EmergencyContactBase(BaseModel):
    parent_id: int
    name: str = Field(..., min_length=1)
    relationship_type: str
    phone: str = Field(..., min_length=3)
    location: Optional[str] = None
    priority: Optional[str] = "primary"

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactUpdate(BaseModel):
    name: Optional[str] = None
    relationship_type: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    priority: Optional[str] = None

class EmergencyContactResponse(EmergencyContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    parent_name: Optional[str] = None


# --- HEALTH READINGS ---
class HealthReadingCreate(BaseModel):
    parent_id: int
    metric: Literal["blood_pressure", "blood_glucose", "temperature", "weight", "heart_rate"]
    value: float = Field(..., gt=0, le=1000)
    secondary_value: Optional[float] = Field(None, gt=0, le=1000)
    unit: str = Field(..., min_length=1, max_length=30)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = Field(None, max_length=2000)

    @model_validator(mode="after")
    def validate_reading_values(self):
        if self.metric == "blood_pressure" and self.secondary_value is None:
            raise ValueError("Blood pressure requires systolic and diastolic values.")
        if self.metric != "blood_pressure" and self.secondary_value is not None:
            raise ValueError("A second value is only supported for blood pressure.")
        return self


class HealthReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: int
    metric: str
    value: float
    secondary_value: Optional[float] = None
    unit: str
    recorded_at: datetime
    notes: Optional[str] = None
    created_at: datetime
    parent_name: Optional[str] = None


# --- NOTIFICATION SCHEMAS ---
class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: Optional[str] = "system"
    link: Optional[str] = None

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    is_read: bool
    created_at: datetime


# --- DASHBOARD & ADMIN STATS SCHEMAS ---
class DashboardOverviewResponse(BaseModel):
    total_parents: int
    total_active_medicines: int
    total_upcoming_appointments: int
    total_reports: int
    today_medicines: List[MedicineResponse]
    upcoming_appointments: List[AppointmentResponse]
    recent_reports: List[MedicalReportResponse]
    emergency_contacts: List[EmergencyContactResponse]
    unread_notifications_count: int

class AdminStatsResponse(BaseModel):
    total_users: int
    total_parents: int
    total_active_medicines: int
    total_appointments: int
    total_reports: int
    recent_users: List[UserResponse]
