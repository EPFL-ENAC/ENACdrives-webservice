.PHONY: shell dev_db dev_feed_db dev run

shell:
	poetry run python enacdrivesweb/manage.py shell

dev_db:
	docker compose up db adminer -d

dev_feed_db:
	poetry run enacdrivesweb/manage.py migrate
	@latest_dump_file=$$(ls data/db_*.yaml 2>/dev/null | sort -r | head -n 1) && \
	echo "Going to load $$latest_dump_file" && \
	poetry run enacdrivesweb/manage.py loaddata $$latest_dump_file

dev:
	poetry run enacdrivesweb/manage.py migrate
	poetry run enacdrivesweb/manage.py collectstatic --noinput
	poetry run enacdrivesweb/manage.py admin_staff_setup < enacdrivesweb/config/admin_staff_list
	poetry run enacdrivesweb/manage.py runserver

run:
	poetry run enacdrivesweb/manage.py collectstatic --noinput
	docker compose up -d db apache2 gunicorn
