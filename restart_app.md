# Restart Application to Apply Email Settings

## Option 1: Restart just the app container
```bash
docker compose restart app
```

## Option 2: Restart all containers
```bash
docker compose restart
```

## Option 3: If docker compose doesn't work, try:
```bash
docker-compose restart app
```

## Verify the application is running:
```bash
docker compose ps
```

## Check logs to ensure no errors:
```bash
docker compose logs app
```

After restarting, your application will be able to send emails using your Hostinger email account!