.PHONY: shell dev_db dev

shell:
	poetry run python enacdrivesweb/manage.py shell

dev_db:
	docker compose up db adminer -d

dev:
	poetry run enacdrivesweb/manage.py migrate
	poetry run enacdrivesweb/manage.py collectstatic --noinput
	poetry run enacdrivesweb/manage.py admin_staff_setup < enacdrivesweb/config/admin_staff_list
	poetry run enacdrivesweb/manage.py runserver
