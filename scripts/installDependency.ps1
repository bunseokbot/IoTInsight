$scriptsDir = split-path -parent $script:MyInvocation.MyCommand.Definition

. "$scriptsDir\PowershellUtils.ps1"

Write-Verbose "Installing dependency"

$rootDir = findFileRecursivelyUp $scriptsDir .

$downloadsDir = "$rootDir\downloads"

$dependencies = @("node", "wireshark", "winpcap")

ForEach (${dependency} in ${dependencies}) {
    if(${dependency} -eq "node")
    {
        $downloadVersion ="8.9.4"
        if(![Environment]::Is64BitProcess)
        {
            $url = "https://nodejs.org/dist/v8.9.4/node-v8.9.4-x86.msi"
        }
        else
        {
            $url = "https://nodejs.org/dist/v8.9.4/node-v8.9.4-x64.msi"
        }     
        $downloadPath = "$downloadsDir\node-$downloadVersion\node-v8.9.4.msi"
        $is_msi_installer = $true
    }
    elseif(${dependency} -eq "wireshark")
    {
        $downloadVersion ="2.4.4"
        if(![Environment]::Is64BitProcess)
        {
            $url = "https://2.na.dl.wireshark.org/win32/Wireshark-win32-2.4.4.exe"
        }
        else
        {
            $url = "https://2.na.dl.wireshark.org/win64/Wireshark-win64-2.4.4.exe"
        }   
        
        $downloadPath = "$downloadsDir\wireshark-$downloadVersion\wireshark.exe"
        $argumentList = "/S /desktopicon=yes"
        $is_msi_installer = $false
    }
    elseif(${dependency} -eq "winpcap")
    {
        $downloadVersion ="8.9.4"
        $url = "https://www.winpcap.org/install/bin/WinPcap_4_1_3.exe"
        $downloadPath = "$downloadsDir\winpcap-$downloadVersion\winpcap.exe"
        $is_msi_installer = $false
    }
    else
    {
        Write-Host "Unknown program requested."
        continue
    }
    
    if(is_installed_program($Dependency))
    {
        Write-Host "$Dependency already installed"
        continue
    }

    if (!(Test-Path $downloadPath))
    {
        Write-Host "Downloading $Dependency..."
        DownloadFile $url $downloadPath
        Write-Host "Downloading $Dependency has completed successfully."
        Write-Host "Installing $Dependency..."
        try {
            if($is_msi_installer) {
                Start-Process -FilePath "msiexec" -ArgumentList "/i $downloadPath /norestart" -Wait
                Write-Host "Installing $Dependency has completed successfully."
                
                RemoveItem $downloadPartPath
            }
            
            if(!([string]::IsNullOrEmpty($argumentList))) {
                Start-Process -FilePath $downloadPath -ArgumentList $argumentList -Wait
                Write-Host "Installing $Dependency has completed successfully."
            } else {
                Start-Process -FilePath $downloadPath -Wait
                Write-Host "Installing $Dependency has completed successfully."

                RemoveItem $downloadPartPath
            }
        } catch{
            Write-Host "Error:" $_.Exception.Message
        }
    }
}

