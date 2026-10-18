"""
auth.py - Section (a): Access Control (login + role-based access control)
MINN2020A Mining Health, Safety and Equipment Monitoring Application

Design:
  * Users are stored in data/users.json
  * Passwords are never stored in plain text
  * Permissions come from one lookup table
"""

import hashlib
import hmac
import json
import os
import secrets


DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data"
)

USERS_FILE = os.path.join(DATA_DIR, "users.json")


ROLES = [
    "Administrator",
    "Safety Officer",
    "Mining Engineer",
    "Maintenance Engineer",
    "Manager"
]


PERMISSIONS = {
    "View dashboard": [
        "Administrator",
        "Safety Officer",
        "Mining Engineer",
        "Maintenance Engineer",
        "Manager"
    ],

    "Worker safety data": [
        "Administrator",
        "Safety Officer",
        "Mining Engineer",
        "Manager"
    ],

    "Safety incidents": [
        "Administrator",
        "Safety Officer",
        "Mining Engineer",
        "Manager"
    ],

    "Equipment data": [
        "Administrator",
        "Mining Engineer",
        "Maintenance Engineer",
        "Manager"
    ],

    "Maintenance data": [
        "Administrator",
        "Mining Engineer",
        "Maintenance Engineer",
        "Manager"
    ],

    "Risk assessment": [
        "Administrator",
        "Safety Officer",
        "Mining Engineer",
        "Manager"
    ],

    "Generate reports": [
        "Administrator",
        "Safety Officer",
        "Mining Engineer",
        "Maintenance Engineer",
        "Manager"
    ],

    "Manage users": [
        "Administrator"
    ],
}


ITERATIONS = 100_000
MIN_PASSWORD_LENGTH = 8


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password, salt=None):
    """Return (salt_hex, hash_hex) for a password."""

    if salt is None:
        salt = secrets.token_hex(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        ITERATIONS
    )

    return salt, digest.hex()


def verify_password(password, salt, stored_hash):
    """Check whether a password matches the stored hash."""

    _, new_hash = hash_password(password, salt)

    return hmac.compare_digest(
        new_hash,
        stored_hash
    )


# ============================================================
# USER STORAGE
# ============================================================

def load_users():

    if not os.path.exists(USERS_FILE):
        create_default_users()

    with open(
        USERS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_users(users):

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    with open(
        USERS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            users,
            f,
            indent=2
        )


def create_default_users():

    defaults = {
        "admin": (
            "Admin@123",
            "Administrator"
        ),

        "safety": (
            "Safety@123",
            "Safety Officer"
        ),

        "engineer": (
            "Engineer@123",
            "Mining Engineer"
        ),

        "maintenance": (
            "Maint@1234",
            "Maintenance Engineer"
        ),

        "manager": (
            "Manager@123",
            "Manager"
        ),
    }

    users = {}

    for username, (password, role) in defaults.items():

        salt, password_hash = hash_password(
            password
        )

        users[username] = {
            "salt": salt,
            "hash": password_hash,
            "role": role,
            "active": True
        }

    save_users(users)


# ============================================================
# LOGIN
# ============================================================

def authenticate(username, password):

    username = (
        username or ""
    ).strip().lower()

    if not username or not password:

        return (
            False,
            "Please enter both username and password."
        )

    users = load_users()

    user = users.get(username)

    if (
        user is None
        or not user["active"]
        or not verify_password(
            password,
            user["salt"],
            user["hash"]
        )
    ):

        return (
            False,
            "Invalid username or password."
        )

    return (
        True,
        user["role"]
    )


# ============================================================
# PERMISSIONS
# ============================================================

def has_permission(role, function):

    return role in PERMISSIONS.get(
        function,
        []
    )


def allowed_functions(role):

    return [
        function
        for function, roles in PERMISSIONS.items()
        if role in roles
    ]


# ============================================================
# USER VALIDATION
# ============================================================

def validate_new_user(
    username,
    password,
    role,
    users
):

    username = username.strip().lower()

    if not username.isalnum():

        return (
            False,
            "Username must contain letters and numbers only."
        )

    if username in users:

        return (
            False,
            "That username already exists."
        )

    if len(password) < MIN_PASSWORD_LENGTH:

        return (
            False,
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )

    if not (
        any(c.isdigit() for c in password)
        and
        any(c.isalpha() for c in password)
    ):

        return (
            False,
            "Password must contain letters and digits."
        )

    if role not in ROLES:

        return (
            False,
            "Invalid role."
        )

    return (
        True,
        username
    )


def add_user(
    username,
    password,
    role
):

    users = load_users()

    ok, result = validate_new_user(
        username,
        password,
        role,
        users
    )

    if not ok:

        return (
            False,
            result
        )

    salt, password_hash = hash_password(
        password
    )

    users[result] = {
        "salt": salt,
        "hash": password_hash,
        "role": role,
        "active": True
    }

    save_users(users)

    return (
        True,
        f"User '{result}' created as {role}."
    )


def set_user_active(
    username,
    active,
    acting_user
):

    users = load_users()

    if username not in users:

        return (
            False,
            "User not found."
        )

    if username == acting_user and not active:

        return (
            False,
            "You cannot disable your own account."
        )

    users[username]["active"] = active

    save_users(users)

    status = (
        "enabled"
        if active
        else "disabled"
    )

    return (
        True,
        f"User '{username}' {status}."
    )


def delete_user(
    username,
    acting_user
):

    users = load_users()

    if username not in users:

        return (
            False,
            "User not found."
        )

    if username == acting_user:

        return (
            False,
            "You cannot delete your own account."
        )

    admins = [
        username
        for username, data in users.items()
        if data["role"] == "Administrator"
        and data["active"]
    ]

    if (
        users[username]["role"] == "Administrator"
        and len(admins) <= 1
    ):

        return (
            False,
            "Cannot delete the last active administrator."
        )

    del users[username]

    save_users(users)

    return (
        True,
        f"User '{username}' deleted."
    )


# ============================================================
# STREAMLIT LOGIN PAGE
# ============================================================

def login_page(st):

    st.title(
        "Khwezi Mining: Health, Safety and Equipment Monitoring"
    )

    st.subheader("Sign in")

    with st.form("login_form"):

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Log in"
        )

    if submitted:

        ok, result = authenticate(
            username,
            password
        )

        if ok:

            st.session_state["user"] = (
                username.strip().lower()
            )

            st.session_state["role"] = result

            st.rerun()

        else:

            st.error(result)

    with st.expander("Demo accounts"):

        st.write(
            "admin / Admin@123, "
            "safety / Safety@123, "
            "engineer / Engineer@123, "
            "maintenance / Maint@1234, "
            "manager / Manager@123"
        )


# ============================================================
# LOGOUT
# ============================================================

def logout_button(st):

    st.sidebar.write(
        f"Signed in as **{st.session_state['user']}** "
        f"({st.session_state['role']})"
    )

    if st.sidebar.button("Log out"):

        for key in (
            "user",
            "role"
        ):

            st.session_state.pop(
                key,
                None
            )

        st.rerun()


# ============================================================
# LOGIN STATUS
# ============================================================

def is_logged_in(st):

    return "role" in st.session_state


# ============================================================
# PERMISSION CHECK
# ============================================================

def require_permission(
    st,
    function
):

    if not is_logged_in(st):

        st.warning(
            "Please log in."
        )

        st.stop()

    if not has_permission(
        st.session_state["role"],
        function
    ):

        st.error(
            f"Access denied: the "
            f"{st.session_state['role']} role "
            f"cannot open '{function}'."
        )

        st.stop()


# ============================================================
# MANAGE USERS PAGE
# ============================================================

def manage_users_page(st):

    require_permission(
        st,
        "Manage users"
    )

    st.header(
        "Manage users"
    )

    users = load_users()

    st.subheader(
        "Existing users"
    )

    st.table([
        {
            "Username": username,
            "Role": data["role"],
            "Status": (
                "Active"
                if data["active"]
                else "Disabled"
            )
        }

        for username, data in users.items()
    ])

    st.subheader(
        "Add user"
    )

    with st.form(
        "add_user",
        clear_on_submit=True
    ):

        new_username = st.text_input(
            "Username"
        )

        new_password = st.text_input(
            "Password",
            type="password"
        )

        new_role = st.selectbox(
            "Role",
            ROLES
        )

        if st.form_submit_button(
            "Create user"
        ):

            ok, message = add_user(
                new_username,
                new_password,
                new_role
            )

            if ok:
                st.success(message)
            else:
                st.error(message)

    st.subheader(
        "Enable, disable or delete"
    )

    target = st.selectbox(
        "User",
        list(users.keys())
    )

    c1, c2, c3 = st.columns(3)

    current_user = st.session_state[
        "user"
    ]

    if c1.button("Enable"):

        st.info(
            set_user_active(
                target,
                True,
                current_user
            )[1]
        )

    if c2.button("Disable"):

        st.info(
            set_user_active(
                target,
                False,
                current_user
            )[1]
        )

    if c3.button("Delete"):

        st.info(
            delete_user(
                target,
                current_user
            )[1]
        )