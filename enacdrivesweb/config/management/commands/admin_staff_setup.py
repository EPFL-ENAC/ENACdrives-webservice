import sys
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = "Add admin staff to the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            nargs="*",
            type=str,
            help="Username to add as admin.",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        usernames = options["username"]
        if len(usernames) == 0:
            # if no username is provided, read from stdin
            for line in sys.stdin:
                usernames.append(line.strip())

        for username in usernames:
            try:
                u = User.objects.get(username=username)
                u.is_superuser = True
                u.is_staff = True
                u.is_active = True
                u.save()
                print(f"Set user {username} as admin.")
            except ObjectDoesNotExist:
                u = User(
                    username=username,
                    is_superuser=True,
                    is_staff=True,
                    is_active=True,
                    date_joined=now,
                )
                u.save()
                print(f"Added user {username} as admin.")
