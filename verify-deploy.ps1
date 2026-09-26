# verify-deploy.ps1 - confirm a push actually reached the live site.
#
# Run AFTER `git push`, once Cloudflare Pages has built (~2 min).
#   .\verify-deploy.ps1
#
# Everything it checks is read from the repo itself (data\manifest.json and
# data\drops.json), so it needs NO edit per drop: it expects the live homepage and
# llms.txt to advertise the manifest's file count, and it checks that the newest
# drop's page and its headline file pages return HTTP 200.
#
# Notes for future edits:
#   - Use curl.exe, NOT curl. In PowerShell `curl` is an alias for
#     Invoke-WebRequest and does not accept -s/-o/-w.
#   - curl.exe output arrives as an ARRAY of lines, so join it before regexing.
#   - Do not use $home as a variable name; it is read-only in PowerShell.
#   - Bulk-curling the live site too fast returns 000 (a connection failure, not
#     a 404). Keep requests few and spaced; this script makes about 6.

$ErrorActionPreference = "Stop"
$site = "https://pursueufotracker.com"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Expected values come from the repo, so this never goes stale between drops.
$manifest = Get-Content (Join-Path $root "data\manifest.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$expected = "$(@($manifest.files).Count)"
$drops = @((Get-Content (Join-Path $root "data\drops.json") -Raw -Encoding UTF8 | ConvertFrom-Json).drops)
$last = $drops[$drops.Count - 1]
$slug = "{0}-drop-{1:D2}" -f $last.date, $last.number

# Pages that only exist once the newest drop has deployed.
$paths = @("/drops/$slug")
foreach ($id in $last.headline_files) { $paths += "/files/$id" }

Write-Output "Checking $site  (newest drop: $slug, expecting $expected files)"
Write-Output ""
$fail = 0
foreach ($p in $paths) {
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 25 "$site$p"
    if ($code -ne "200") { $fail++ }
    "{0}  {1,-6} {2}" -f $(if ($code -eq "200") { "OK  " } else { "FAIL" }), $code, $p
    Start-Sleep -Milliseconds 400
}

# The archive count the site advertises, on two independent surfaces.
$hp = (curl.exe -s --max-time 25 "$site/") -join " "
$m  = [regex]::Match($hp, 'ALL (\d+) FILES')
$hpN = if ($m.Success) { $m.Groups[1].Value } else { "?" }

$lt = (curl.exe -s --max-time 25 "$site/llms.txt") -join " "
$m2 = [regex]::Match($lt, 'all (\d+) files')
$ltN = if ($m2.Success) { $m2.Groups[1].Value } else { "?" }

Write-Output ""
"{0}  homepage advertises {1} files (want {2})" -f $(if ($hpN -eq $expected) { "OK  " } else { "FAIL" }), $hpN, $expected
"{0}  llms.txt advertises {1} files (want {2})" -f $(if ($ltN -eq $expected) { "OK  " } else { "FAIL" }), $ltN, $expected
if ($hpN -ne $expected) { $fail++ }
if ($ltN -ne $expected) { $fail++ }

Write-Output ""
if ($fail -eq 0) {
    Write-Output "DEPLOY VERIFIED - $slug is live. Safe to post the Reddit thread."
} else {
    Write-Output "$fail check(s) failed."
    Write-Output "If you just pushed, Cloudflare may still be building - wait 60s and re-run."
    Write-Output "If it still fails, the push did not land: run  git status  and  git log --oneline -1"
}
