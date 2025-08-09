from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
)
import re

PASSWORD_VALIDATION_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])\S{8,}$")


class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str


class SignupRequestSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=55)
    email: EmailStr
    password: str
    password_repeat: str

    @field_validator("username", "email", mode="before")
    @classmethod
    def normalize_identifiers(cls, v):
        if v is None:
            return v
        v = re.sub(r"\s+", "", str(v))  # remove all whitespace
        return v.lower()

    @model_validator(mode="after")
    def validate_password_and_repeat_password(self):
        # Password must be: ≥8 non-space chars, ≥1 uppercase, ≥1 digit, ≥1 special (non-alnum).
        if not PASSWORD_VALIDATION_REGEX.fullmatch(self.password):
            raise ValueError(
                "Password is weak. Require ≥8 non-space chars, ≥1 uppercase, ≥1 digit, and ≥1 special."
            )
        if self.password != self.password_repeat:
            raise ValueError("password and password_repeat do not match.")
        return self


class UserCreationSchema(BaseModel):

    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=55)
    email: EmailStr
    password: str


class ChangePassRequestSchema(BaseModel):
    current_password: str
    new_password: str
    new_password_repeat: str

    @model_validator(mode="after")
    def validate_password_and_repeat_password(self):
        # Password must be: ≥8 non-space chars, ≥1 uppercase, ≥1 digit, ≥1 special (non-alnum).
        if not PASSWORD_VALIDATION_REGEX.fullmatch(self.new_password):
            raise ValueError(
                "New password is weak. Require ≥8 non-space chars, ≥1 uppercase, ≥1 digit, and ≥1 special."
            )
        if self.new_password != self.new_password_repeat:
            raise ValueError("new password and new password repeat do not match.")
        return self
