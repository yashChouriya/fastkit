from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
)
import re


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
        pat = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])\S{8,}$")
        if not pat.fullmatch(self.password):
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
