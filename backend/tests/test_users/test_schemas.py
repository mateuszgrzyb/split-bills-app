import uuid

from app.users.models import User
from app.users.schemas import LoginIn, RegisterIn, TokenOut, UserOut


def test_register_and_login_inputs_accept_credentials():
    # Given valid credentials
    credentials = {"username": "alice", "password": "password"}

    # When parsing registration and login requests
    registration = RegisterIn.model_validate(credentials)
    login = LoginIn.model_validate(credentials)

    # Then both schemas preserve the submitted fields
    assert registration.model_dump() == credentials
    assert login.model_dump() == credentials


def test_user_output_reads_orm_attributes_without_password_hash():
    # Given an ORM user
    user = User(id=uuid.uuid4(), username="alice", password_hash="hidden")

    # When converting the user to the public schema
    result = UserOut.model_validate(user)

    # Then only public fields are serialized
    assert result.id == user.id
    assert result.username == "alice"
    assert "password_hash" not in result.model_dump()


def test_token_output_defaults_to_bearer():
    # Given a token response with an access token
    result = TokenOut(access_token="access")

    # When serializing the response
    serialized = result.model_dump()

    # Then the token type defaults to bearer
    assert serialized == {"access_token": "access", "token_type": "bearer"}
