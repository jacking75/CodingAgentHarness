$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
$drivers = @(Get-CimInstance Win32_PnPSignedDriver | Where-Object { $_.DeviceName -match 'ViGEm|Virtual Gamepad Emulation' } | ForEach-Object {
    [ordered]@{ name=$_.DeviceName; version=$_.DriverVersion; signed=$_.IsSigned; signer=$_.Signer; inf=$_.InfName }
})
$bus = Get-CimInstance Win32_SystemDriver -Filter "Name='ViGEmBus'"
$devices = @(Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match 'ViGEm|Virtual Gamepad Emulation' } | ForEach-Object {
    [ordered]@{ name=$_.Name; status=$_.Status; problem_code=$_.ConfigManagerErrorCode }
})
$pendingRename = (Get-ItemProperty -LiteralPath 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager' -Name PendingFileRenameOperations -ErrorAction SilentlyContinue).PendingFileRenameOperations
$reboot = [ordered]@{
    component_servicing=(Test-Path -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending')
    windows_update=(Test-Path -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired')
    pending_file_rename=[bool]$pendingRename
}
[ordered]@{
    administrator=$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    os_architecture=[Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
    os_version=[Environment]::OSVersion.Version.ToString()
    driver_file_present=(Test-Path -LiteralPath (Join-Path $env:WINDIR 'System32\drivers\ViGEmBus.sys'))
    bus_state=if ($bus) { $bus.State } else { $null }
    signed_drivers=$drivers
    pnp_devices=$devices
    reboot_indicators=$reboot
    reboot_indicator_note='System-wide hints; these do not prove that this driver needs a reboot.'
} | ConvertTo-Json -Depth 6
