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
cat << EOF > .secrets.env
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
        "127.0.0.1",
        "enacdrives.epfl.ch",
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

cat << EOF > enacmoni.cred
username = enacmoni
password = theSecretPassword
domain   = INTRANET
EOF
```

2. Run it

```bash
make dev_db

# if starting from scratch : feed the database
# some dump must be dump in `data/db_YYYY-MM-DD.yaml`
make dev_feed_db

# run as dev, no authentification
make dev

# run as dev, with an authentificated user
HTTP_X_CUSTOM_REMOTE_USER="username" make dev

# run all dockerized (authentication will be Tequila)
make run
```

3. Local testing

```bash
http "https://localhost/config/validate_username?username=username"
http "https://localhost/config/get?username=username"
http "https://localhost/config/ldap_settings?username=username"
```

3.1 manage releases

https://localhost/releases/admin
https://localhost/releases/download?os=Windows
https://localhost/releases/api/latest_release_number?os=Windows

3.2 manage config

https://localhost/admin/
https://localhost/config/get?username=bancal
https://localhost/config/validate_username?username=bancal
https://localhost/config/ldap_settings?username=bancal
