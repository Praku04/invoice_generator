@echo off
echo Restarting Invoice Generator Application...
echo.

echo Step 1: Stopping application container...
docker compose stop app

echo.
echo Step 2: Removing old container to force reload of environment...
docker compose rm -f app

echo.
echo Step 3: Starting application with new configuration...
docker compose up -d app

echo.
echo Step 4: Checking container status...
docker compose ps

echo.
echo Step 5: Showing recent logs...
docker compose logs --tail=20 app

echo.
echo Application restart complete!
echo The new Hostinger email configuration should now be active.
echo.
pause