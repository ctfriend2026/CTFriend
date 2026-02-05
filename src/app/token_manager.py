import argparse
import os
import hmac
import hashlib
from core.db_logger import SessionLocal, User, init_db
from sqlalchemy import inspect

# It is highly recommended to set this as an environment variable in production.
SECRET_KEY = os.environ.get("TOKEN_SECRET_KEY", "a-secure-default-secret-for-dev")


def add_is_active_column() -> None:
    """Adds the is_active column to the users table if it doesn't exist."""
    engine = init_db.__globals__["engine"]
    inspector = inspect(subject=engine)
    columns = [c["name"] for c in inspector.get_columns("users")]
    if "is_active" not in columns:
        print("Column 'is_active' not found in 'users' table, adding it.")
        with engine.connect() as con:
            con.execute(
                "ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT FALSE;"
            )
        print("Column 'is_active' added successfully.")


def add_email_column() -> None:
    """Adds the email column to the users table if it doesn't exist."""
    engine = init_db.__globals__["engine"]
    inspector = inspect(subject=engine)
    columns = [c["name"] for c in inspector.get_columns("users")]
    if "email" not in columns:
        print("Column 'email' not found in 'users' table, adding it.")
        with engine.connect() as con:
            con.execute("ALTER TABLE users ADD COLUMN email VARCHAR;")
            con.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);"
            )
        print(
            "Column 'email' added successfully. Please manually update existing user records with their email addresses."
        )


def generate_token(email: str) -> str:
    """Generates a deterministic HMAC-SHA256 token from an email address."""
    return hmac.new(
        key=SECRET_KEY.encode(), msg=email.lower().encode(), digestmod=hashlib.sha256
    ).hexdigest()


def whitelist_email(email: str) -> None:
    """Creates a new user with the given email and a generated token."""
    normalized_email = email.lower()
    token = generate_token(email=normalized_email)

    with SessionLocal() as session:
        user = session.query(User).filter_by(email=normalized_email).first()
        if user:
            if user.is_active:
                print(
                    f"User with email '{normalized_email}' is already whitelisted and active."
                )
                print(f"Their token is: {user.username}")
            else:
                user.is_active = True
                session.commit()
                print(f"User with email '{normalized_email}' has been re-activated.")
                print(f"Their token is: {user.username}")
        else:
            new_user = User(email=normalized_email, username=token, is_active=True)
            session.add(new_user)
            session.commit()
            print(
                f"New user with email '{normalized_email}' has been created and whitelisted."
            )
            print(f"Their token is: {token}")


def list_users() -> None:
    """Lists all users, their tokens, and their active status."""
    with SessionLocal() as session:
        users = session.query(User).all()
        if not users:
            print("No users found in the database.")
            return

        print(
            f"{'Email':<30} {'Token (Username)':<66} {'Is Active':<12} {'Created At'}"
        )
        print("-" * 130)
        for user in users:
            print(
                f"{user.email:<30} {user.username:<66} {str(user.is_active):<12} {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )


if __name__ == "__main__":
    init_db()
    add_is_active_column()
    add_email_column()

    parser = argparse.ArgumentParser(description="Manage user tokens for the chatbot.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    whitelist_parser = subparsers.add_parser(
        name="whitelist",
        help="Whitelist a new user by email or reactivate an existing one.",
    )
    whitelist_parser.add_argument(
        "email", type=str, help="The user's email address to whitelist."
    )

    list_parser = subparsers.add_parser("list", help="List all users in the database.")

    generate_parser = subparsers.add_parser(
        name="generate", help="Generate a token for an email without DB interaction."
    )
    generate_parser.add_argument(
        "email", type=str, help="The email to generate a token for."
    )

    args = parser.parse_args()

    if args.command == "whitelist":
        whitelist_email(email=args.email)
    elif args.command == "list":
        list_users()
    elif args.command == "generate":
        print(generate_token(email=args.email))
