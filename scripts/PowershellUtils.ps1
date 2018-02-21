function IsDirectory([Parameter(Mandatory=$true)][string]$path)
{
    return (Get-Item $path) -is [System.IO.DirectoryInfo]
}

function RemoveItem([Parameter(Mandatory=$true)][string]$path)
{
    if ([string]::IsNullOrEmpty($path))
    {
        return
    }

    if (Test-Path $path)
    {
        # Remove-Item -Recurse occasionally fails. This is a workaround
        if (IsDirectory $path)
        {
            & cmd.exe /c rd /s /q $path
        }
        else
        {
            Remove-Item $path -Force
        }
    }
}

function CreateParentDirectoryIfNotExists([Parameter(Mandatory=$true)][string]$path)
{
    $parentDir = split-path -parent $path
    if ([string]::IsNullOrEmpty($parentDir))
    {
        return
    }

    if (!(Test-Path $parentDir))
    {
        New-Item -ItemType Directory -Path $parentDir | Out-Null
    }
}
function DownloadFile( [Parameter(Mandatory=$true)][string]$url,
                       [Parameter(Mandatory=$true)][string]$downloadPath)
{
    if (Test-Path $downloadPath)
    {
        return
    }

    CreateParentDirectoryIfNotExists $downloadPath

    $downloadPartPath = "$downloadPath.part"
    RemoveItem $downloadPartPath

    $wc = New-Object System.Net.WebClient
    $wc.DownloadFile($url, $downloadPartPath)
    Move-Item -Path $downloadPartPath -Destination $downloadPath
}
function findFileRecursivelyUp()
{
    param(
        [ValidateNotNullOrEmpty()]
        [Parameter(Mandatory=$true)][string]$startingDir,
        [ValidateNotNullOrEmpty()]
        [Parameter(Mandatory=$true)][string]$filename
    )

    $currentDir = $startingDir

    while (!($currentDir -eq "") -and !(Test-Path "$currentDir\$filename"))
    {
        Write-Verbose "Examining $currentDir for $filename"
        $currentDir = Split-path $currentDir -Parent
    }
    Write-Verbose "Examining $currentDir for $filename - Found"
    return $currentDir
}

function is_installed_program( [Parameter(Mandatory=$true)][string]$program_name )
{
    $x86 = ((Get-ChildItem "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall") |
        Where-Object { $_.GetValue( "DisplayName" ) -like "*$program_name*" } ).Length -gt 0;

    $x64 = ((Get-ChildItem "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall") |
        Where-Object { $_.GetValue( "DisplayName" ) -like "*$program_name*" } ).Length -gt 0;

    return $x86 -or $x64;
}