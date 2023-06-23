.PHONY: shell dev_db dev

shell:
	poetry run python enacdrivesweb/manage.py shell

dev_db:
	docker compose up db adminer -d

dev:
	poetry run enacdrivesweb/manage.py migrate
