docker compose -f ../build/compose.yml -f ../build/compose.dev.yml down --remove-orphans
docker compose -f ../build/compose.yml -f ../build/compose.dev.yml up --watch