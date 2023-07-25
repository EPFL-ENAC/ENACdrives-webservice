include .secrets.env
UID := $(shell id -u)
GID := $(shell id -g)

.PHONY: shell dev_db dev_feed_db dev run container_entrypoint

shell:
	poetry run python enacdrivesweb/manage.py shell

dev_db:
	docker compose up --build db adminer -d

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
	docker compose up --build -d db traefik-reverse-proxy apache2 gunicorn

container_entrypoint:
	/root/.local/bin/poetry run enacdrivesweb/manage.py migrate
	/root/.local/bin/poetry run enacdrivesweb/manage.py collectstatic --noinput
	/root/.local/bin/poetry run enacdrivesweb/manage.py admin_staff_setup < enacdrivesweb/config/admin_staff_list
	cd enacdrivesweb && /root/.local/bin/poetry run gunicorn --bind 0.0.0.0:8000 enacdrivesweb.wsgi

generate-selfsigned-cert:
	cd cert && OWNER="${UID}.${GID}" docker compose up --remove-orphans

backup-dump:
	@docker-compose exec db sh -c 'exec mysqldump --all-databases -uroot -p"${MYSQL_ROOT_PASSWORD}"' > ${DEST_FOLDER}/all-databases.sql
