from pydantic import BaseModel, EmailStr, Field, field_validator


class UserDto(BaseModel):
    fullname: str = Field(..., error_message="Fullname is required.", min_length=3, max_length=50)
    email: EmailStr = Field(error_message="Please enter a valid email address.")
    password: str = Field(..., error_message="Password is required.")

    @field_validator('password')
    @classmethod
    def password_validation(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one capital letter")
        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in password):
            raise ValueError("The password must contain at least one number")
        return password

class UserUpdatedDto(BaseModel):
    fullname: str | None  = Field(default=None) 
    email: EmailStr | None =  Field(default=None) 
    password: str | None =  Field(default=None)

    @field_validator('password')
    @classmethod
    def password_validation(cls, password):
        if password is not None:  
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters long")
            if not any(char.isupper() for char in password):
                raise ValueError("Password must contain at least one capital letter")
            if not any(char.islower() for char in password):
                raise ValueError("Password must contain at least one lowercase letter")
            if not any(char.isdigit() for char in password):
                raise ValueError("The password must contain at least one number")
        return password 
    
    def dtoToUser(self,user):
        data = self.model_dump(exclude_none = True)
        for key, value in data.items():
            setattr(user, key, value)

