docker compose -f ../build/compose.yml -f ../build/compose.prod.yml down --remove-orphans
docker compose -f ../build/compose.yml -f ../build/compose.prod.yml build