# ENACdrives-webservice

ENACdrives is the interactive tool developed by ENAC-IT for enployees and students to facilitate access to storage services, including individual storage and collaborative/archive/raw services (NAS3 based).
This repository contains the code for the web service part of the ENACdrives tool.

End-user documentation can be read at : https://go.epfl.ch/KB0016347

End-user software can be downloaded from https://go.epfl.ch/KB0016347

Settings administration page is located here : http://enacdrives.epfl.ch/admin/config/config/

New releases are to be uploaded here in order to be accessible to the users : http://enacdrives.epfl.ch/releases/admin

## Run it

1. Set mandatory setup into the 2 following files (replace values with your own):

```bash
cat << EOF > secrets.env
MYSQL_ROOT_PASSWORD="rootP4ssw0rd"
MYSQL_DATABASE="enacdrives_db"
MYSQL_USER="enacdrives_user"
MYSQL_PASSWORD="userP4ssw0rd"
EOF

cat << EOF > .secrets.json
{
    "ADMINS": [
        [
            "Your Name",
            "your.email@epfl.ch"
        ]
    ],
    "EMAIL_HOST": "mail.epfl.ch",
    "EMAIL_SUBJECT_PREFIX": "[ENACdrives on laptop] ",
    "SERVER_EMAIL": "no-reply+ENACdrives-dev@epfl.ch",
    "SECRET_KEY": "OneSecretStringRandomlyGenerated",
    "DEBUG": true,
    "ALLOWED_HOSTS": [
        "localhost",
        "127.0.0.1"
    ],
    "CSRF_TRUSTED_ORIGINS": [
        "http://localhost",
        "http://127.0.0.1"
    ],
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "enacdrives_db",
            "USER": "enacdrives_user",
            "PASSWORD": "userP4ssw0rd",
            "HOST": "127.0.0.1",
            "PORT": "3306"
        }
    }
}
EOF

cat << EOF > enacdrivesweb/config/admin_staff_list
admin_username
one_per_line
third_admin_username
EOF
```

2. Run it

```bash
make dev_db

# if starting from scratch : feed the database
# some dump must be dump in `data/db_YYYY-MM-DD.yaml`
make dev_feed_db

# no authentification
make dev

# with an authentificated user
HTTP_X_CUSTOM_REMOTE_USER="username" make dev
```

3. Local testing

```bash
http "http://127.0.0.1:8000/config/validate_username?username=username"
http "http://127.0.0.1:8000/config/get?username=username"
http "http://127.0.0.1:8000/config/ldap_settings?username=username"
```
