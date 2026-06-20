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

# Hide the console window
$consoleHandle = [WinApi]::GetConsoleWindow()
[WinApi]::ShowWindow($consoleHandle, [WinApi]::SW_HIDE)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName Microsoft.VisualBasic

$form = New-Object System.Windows.Forms.Form
$form.Text = "Einstein AI"
$form.Size = New-Object System.Drawing.Size(600, 500)
$form.StartPosition = "CenterScreen"

$outputBox = New-Object System.Windows.Forms.RichTextBox
$outputBox.Location = New-Object System.Drawing.Point(10, 10)
$outputBox.Size = New-Object System.Drawing.Size(560, 300)
$outputBox.ReadOnly = $true
$form.Controls.Add($outputBox)

$inputBox = New-Object System.Windows.Forms.TextBox
$inputBox.Location = New-Object System.Drawing.Point(10, 320)
$inputBox.Size = New-Object System.Drawing.Size(460, 30)
$form.Controls.Add($inputBox)

$sendButton = New-Object System.Windows.Forms.Button
$sendButton.Location = New-Object System.Drawing.Point(480, 320)
$sendButton.Size = New-Object System.Drawing.Size(90, 30)
$sendButton.Text = "Send"
$form.Controls.Add($sendButton)

$importButton = New-Object System.Windows.Forms.Button
$importButton.Location = New-Object System.Drawing.Point(10, 360)
$importButton.Size = New-Object System.Drawing.Size(120, 30)
$importButton.Text = "Import File"
$form.Controls.Add($importButton)

$urlButton = New-Object System.Windows.Forms.Button
$urlButton.Location = New-Object System.Drawing.Point(140, 360)
$urlButton.Size = New-Object System.Drawing.Size(120, 30)
$urlButton.Text = "Import URL"
$form.Controls.Add($urlButton)

# Function to run Python and get response
function Get-EinsteinResponse($query) {
    # Escape single quotes for Python command line
    $escapedQuery = $query -replace "'", "\'"
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo.FileName = "python"
    $process.StartInfo.Arguments = "-m einstein_ai.einstein_bot `"$escapedQuery`""
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.CreateNoWindow = $true
    $process.Start() | Out-Null
    $result = $process.StandardOutput.ReadToEnd()
    $process.WaitForExit()

    # Filter out initialization messages
    $cleanResult = $result -replace "(?s).*Einstein AI\.\.\.`n", ""
    return $cleanResult.Trim()
}

$sendButton.Add_Click({
    $query = $inputBox.Text
    if ($query -ne "") {
        $outputBox.AppendText("You: $query`n")
        $inputBox.Text = ""
        $outputBox.AppendText("Einstein is thinking (Initial loading take ~30s)...`n")
        $form.Refresh()
        $response = Get-EinsteinResponse $query
        $outputBox.AppendText("Einstein: $response`n`n")
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

        $outputBox.AppendText("Import complete.`n`n")
    }
})

$urlButton.Add_Click({
    $url = [Microsoft.VisualBasic.Interaction]::InputBox("Enter URL to Einstein source:", "Import URL", "https://")
    if ($url -ne "") {
        $outputBox.AppendText("Importing from URL: $url...`n")
        $form.Refresh()

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo.FileName = "python"
        $process.StartInfo.Arguments = "-m einstein_ai.ingest `"$url`""
        $process.StartInfo.UseShellExecute = $false
        $process.StartInfo.RedirectStandardOutput = $true
        $process.StartInfo.CreateNoWindow = $true
        $process.Start() | Out-Null
        $process.WaitForExit()

        $outputBox.AppendText("Import complete.`n`n")
    }
})

$form.ShowDialog()
