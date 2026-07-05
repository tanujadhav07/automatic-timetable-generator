#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
Push-Location frontend
npm ci
npm run build
Pop-Location
Write-Output "Frontend built into frontend/dist"
