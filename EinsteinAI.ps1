Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class WinApi {
    [DllImport("kernel32.dll")]
    public static extern IntPtr GetConsoleWindow();

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    public const int SW_HIDE = 0;
    public const int SW_SHOW = 5;
}
"@

function Hide-Console {
    $consoleHandle = [WinApi]::GetConsoleWindow()
    if ($consoleHandle -ne [IntPtr]::Zero) {
        [WinApi]::ShowWindow($consoleHandle, [WinApi]::SW_HIDE)
    }
}

Hide-Console

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName Microsoft.VisualBasic

# Main Form
$form = New-Object System.Windows.Forms.Form
$form.Text = "Einstein AI - Powered by SherwoodSource"
$form.Size = New-Object System.Drawing.Size(900, 600)
$form.StartPosition = "CenterScreen"
$form.BackColor = [System.Drawing.Color]::FromArgb(240, 240, 240)
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

# Fonts
$titleFont = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
$labelFont = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$textFont = New-Object System.Drawing.Font("Consolas", 10)

# Branding Label
$brandLabel = New-Object System.Windows.Forms.Label
$brandLabel.Text = "SherwoodSource"
$brandLabel.Location = New-Object System.Drawing.Point(750, 10)
$brandLabel.Size = New-Object System.Drawing.Size(130, 30)
$brandLabel.ForeColor = [System.Drawing.Color]::Gray
$brandLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Italic)
$form.Controls.Add($brandLabel)

# Chat Area
$chatLabel = New-Object System.Windows.Forms.Label
$chatLabel.Text = "Conversation"
$chatLabel.Location = New-Object System.Drawing.Point(10, 10)
$chatLabel.Font = $labelFont
$form.Controls.Add($chatLabel)

$outputBox = New-Object System.Windows.Forms.RichTextBox
$outputBox.Location = New-Object System.Drawing.Point(10, 35)
$outputBox.Size = New-Object System.Drawing.Size(600, 400)
$outputBox.ReadOnly = $true
$outputBox.BackColor = [System.Drawing.Color]::White
$outputBox.Font = $textFont
$form.Controls.Add($outputBox)

$inputBox = New-Object System.Windows.Forms.TextBox
$inputBox.Location = New-Object System.Drawing.Point(10, 450)
$inputBox.Size = New-Object System.Drawing.Size(500, 30)
$inputBox.Font = $textFont
$form.Controls.Add($inputBox)

$sendButton = New-Object System.Windows.Forms.Button
$sendButton.Location = New-Object System.Drawing.Point(520, 448)
$sendButton.Size = New-Object System.Drawing.Size(90, 32)
$sendButton.Text = "Send"
$sendButton.BackColor = [System.Drawing.Color]::FromArgb(0, 120, 215)
$sendButton.ForeColor = [System.Drawing.Color]::White
$form.Controls.Add($sendButton)

# Sources Area
$sourcesLabel = New-Object System.Windows.Forms.Label
$sourcesLabel.Text = "Reference Sources"
$sourcesLabel.Location = New-Object System.Drawing.Point(630, 10)
$sourcesLabel.Font = $labelFont
$form.Controls.Add($sourcesLabel)

$sourcesList = New-Object System.Windows.Forms.ListBox
$sourcesList.Location = New-Object System.Drawing.Point(630, 35)
$sourcesList.Size = New-Object System.Drawing.Size(240, 400)
$sourcesList.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$form.Controls.Add($sourcesList)

# Buttons Row
$importButton = New-Object System.Windows.Forms.Button
$importButton.Location = New-Object System.Drawing.Point(10, 500)
$importButton.Size = New-Object System.Drawing.Size(120, 35)
$importButton.Text = "Import File"
$form.Controls.Add($importButton)

$urlButton = New-Object System.Windows.Forms.Button
$urlButton.Location = New-Object System.Drawing.Point(140, 500)
$urlButton.Size = New-Object System.Drawing.Size(120, 35)
$urlButton.Text = "Import URL"
$form.Controls.Add($urlButton)

$refreshButton = New-Object System.Windows.Forms.Button
$refreshButton.Location = New-Object System.Drawing.Point(270, 500)
$refreshButton.Size = New-Object System.Drawing.Size(120, 35)
$refreshButton.Text = "Refresh Memory"
$form.Controls.Add($refreshButton)

$outputBox.AppendText("Einstein AI System Initialized.`n")

# Global variable to store source URLs
$Global:SourceUrls = @{}

# Function to update the sources list from SOURCES.env
function Update-SourcesList {
    $sourcesList.Items.Clear()
    $Global:SourceUrls = @{}
    if (Test-Path "SOURCES.env") {
        Get-Content "SOURCES.env" | ForEach-Object {
            if ($_ -match "^\s*#") { return } # Skip comments
            if ($_ -match "^([^=]+)=([^|]+)\|?(.*)") {
                $name = $Matches[1].Trim()
                $url = $Matches[2].Trim()
                $sourcesList.Items.Add($name) | Out-Null
                $Global:SourceUrls[$name] = $url
            }
        }
    }
}

# Initial update
Update-SourcesList

# Function to run Python and get response
function Get-EinsteinResponse($query) {
    $escapedQuery = $query -replace "'", "\'"
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo.FileName = "python"
    $process.StartInfo.Arguments = "-m einstein_ai.einstein_bot `"$escapedQuery`""
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.RedirectStandardError = $true
    $process.StartInfo.CreateNoWindow = $true
    $process.Start() | Out-Null
    $result = $process.StandardOutput.ReadToEnd()
    $err = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    $cleanResult = $result -replace "(?s).*Einstein AI\.\.\.`n", ""
    if ($cleanResult.Trim() -eq "") {
        return "Error: " + $err
    }
    return $cleanResult.Trim()
}

$sendButton.Add_Click({
    $query = $inputBox.Text
    if ($query -ne "") {
        $outputBox.AppendText("You: $query`n")
        $inputBox.Text = ""
        $outputBox.AppendText("Einstein is thinking...`n")
        $form.Refresh()
        $response = Get-EinsteinResponse $query
        $outputBox.AppendText("Einstein: $response`n`n")
        $outputBox.ScrollToCaret()

        $pythonCmd = "from einstein_ai.utils import log_interaction; log_interaction(r'''$query''', r'''$response''')"
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo.FileName = "python"
        $process.StartInfo.Arguments = "-c `"$pythonCmd`""
        $process.StartInfo.UseShellExecute = $false
        $process.StartInfo.CreateNoWindow = $true
        $process.Start() | Out-Null
        $process.WaitForExit()
    }
})

$sourcesList.Add_DoubleClick({
    if ($sourcesList.SelectedItem -ne $null) {
        $url = $Global:SourceUrls[$sourcesList.SelectedItem]
        [System.Diagnostics.Process]::Start($url)
    }
})

$importButton.Add_Click({
    $openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
    $openFileDialog.Filter = "Supported Files (*.txt, *.pdf)|*.txt;*.pdf|All Files (*.*)|*.*"
    if ($openFileDialog.ShowDialog() -eq "OK") {
        $filePath = $openFileDialog.FileName
        $outputBox.AppendText("Importing $filePath...`n")
        $form.Refresh()

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo.FileName = "python"
        $process.StartInfo.Arguments = "-m einstein_ai.ingest `"$filePath`""
        $process.StartInfo.UseShellExecute = $false
        $process.StartInfo.RedirectStandardOutput = $true
        $process.StartInfo.CreateNoWindow = $true
        $process.Start() | Out-Null
        $process.WaitForExit()

        $outputBox.AppendText("Import complete. Memory refreshed.`n`n")
        $outputBox.ScrollToCaret()
    }
})

$urlButton.Add_Click({
    $url = [Microsoft.VisualBasic.Interaction]::InputBox("Enter URL to Einstein source:", "Import URL", "https://")
    if ($url -ne "" -and $url -ne "https://") {
        $triggers = [Microsoft.VisualBasic.Interaction]::InputBox("Enter trigger keywords (comma-separated):", "Trigger Words", "einstein, physics")

        $outputBox.AppendText("Adding URL to sources: $url...`n")
        $form.Refresh()

        # Add to SOURCES.env first
        $pythonCmd = "from einstein_ai.utils import add_online_source; add_online_source(r'''$url''', r'''$triggers''')"
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo.FileName = "python"
        $process.StartInfo.Arguments = "-c `"$pythonCmd`""
        $process.StartInfo.UseShellExecute = $false
        $process.StartInfo.CreateNoWindow = $true
        $process.Start() | Out-Null
        $process.WaitForExit()

        # Then ingest (which will cache it and rebuild index)
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo.FileName = "python"
        $process.StartInfo.Arguments = "-m einstein_ai.ingest"
        $process.StartInfo.UseShellExecute = $false
        $process.StartInfo.CreateNoWindow = $true
        $process.Start() | Out-Null
        $process.WaitForExit()

        Update-SourcesList
        $outputBox.AppendText("Import complete. Source list and memory updated.`n`n")
        $outputBox.ScrollToCaret()
    }
})

$refreshButton.Add_Click({
    $outputBox.AppendText("Refreshing memory from history and sources...`n")
    $form.Refresh()
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo.FileName = "python"
    $process.StartInfo.Arguments = "-m einstein_ai.ingest"
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.CreateNoWindow = $true
    $process.Start() | Out-Null
    $process.WaitForExit()
    $outputBox.AppendText("Memory refresh complete.`n`n")
    $outputBox.ScrollToCaret()
})

$form.ShowDialog()
