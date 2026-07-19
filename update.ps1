# update.ps1 - refresh Fever data and push updates
Write-Host "Scraping latest shot data..." -ForegroundColor Cyan
python scraper/scrape.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Scrape failed - not pushing. Check the output above." -ForegroundColor Red
    exit 1
}

$changed = git status --porcelain data/
if ($changed) {
    git add data/
    git commit -m "Update shot data $(Get-Date -Format 'yyyy-MM-dd')"
    git push
    Write-Host "Pushed. Live app will redeploy shortly." -ForegroundColor Green
} else {
    Write-Host "No new data - nothing to push." -ForegroundColor Yellow
}