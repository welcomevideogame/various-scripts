function Connect-VPN {
    param (
        [string]$VPNName,
        [string]$Username,
        [string]$Password
    )

    $connectionResult = rasdial $VPNName $Username $Password

    if ($connectionResult -like '*No connections*') {
        Write-Host "Connection failed. Login does not exist or login failed." -ForegroundColor Red
        $userInput = Read-Host -Prompt "Please enter your login information (Username:Password)"
        $inputArray = $userInput.Split(":")

        if ($inputArray.Count -eq 2) {
            $Username = $inputArray[0]
            $Password = $inputArray[1]
            Connect-VPN -VPNName $VPNName -Username $Username -Password $Password
        } else {
            Write-Host "Invalid input format. Please enter the information in the format Username:Password." -ForegroundColor Red
        }
    } elseif ($connectionResult -like '*Command completed successfully*') {
        Write-Host "Connected to VPN successfully." -ForegroundColor Green
    } else {
        Write-Host "Connection failed. An unexpected error occurred." -ForegroundColor Red
    }
}

$VPNName = "Name"
$Username = "Username"
$Password = "Password"
Connect-VPN -VPNName $VPNName -Username $Username -Password $Password
