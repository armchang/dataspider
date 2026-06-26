# tradrpro.ai Dataspider Settings

This document describes the simple integration pattern for controlling Dataspider from the `tradrpro.ai` .NET website.

Goal:

```text
User clicks a button in tradrpro.ai
-> tradrpro.ai backend reads the configured Dataspider URL
-> tradrpro.ai backend calls Dataspider API
-> Dataspider starts, stops, or reports scanner status
```

Keep the browser away from Dataspider directly. Let the .NET backend call Dataspider.

## 1. Run Dataspider

Dataspider must be running somewhere before `tradrpro.ai` can control it.

Local development:

```bash
python3 -m scripts.api_server
```

Default URL:

```text
http://127.0.0.1:8000
```

Remote server example:

```bash
DATASPIDER_API_HOST=0.0.0.0 DATASPIDER_API_PORT=8000 python3 -m scripts.api_server
```

Do not expose Dataspider publicly without firewall, VPN, reverse proxy auth, or an API token. Dataspider currently has no built-in authentication.

## 2. Create A Settings Table

In the `tradrpro.ai` database, add one simple settings table.

```sql
CREATE TABLE AppSettings (
    Id INT PRIMARY KEY,
    DataspiderBaseUrl NVARCHAR(500) NOT NULL
);

INSERT INTO AppSettings (Id, DataspiderBaseUrl)
VALUES (1, 'http://127.0.0.1:8000');
```

Use one row with `Id = 1`. Keep it boring.

## 3. Add The Model

```csharp
public class AppSettings
{
    public int Id { get; set; }
    public string DataspiderBaseUrl { get; set; } = "";
}
```

Add it to the EF Core `DbContext`:

```csharp
public DbSet<AppSettings> AppSettings { get; set; }
```

## 4. Add The Settings Service

This service reads and updates the Dataspider URL.

```csharp
public class AppSettingsService
{
    private readonly ApplicationDbContext _db;

    public AppSettingsService(ApplicationDbContext db)
    {
        _db = db;
    }

    public async Task<string> GetDataspiderBaseUrlAsync()
    {
        var settings = await _db.AppSettings.FindAsync(1);

        if (settings == null || string.IsNullOrWhiteSpace(settings.DataspiderBaseUrl))
        {
            throw new InvalidOperationException("Dataspider URL is not configured.");
        }

        return settings.DataspiderBaseUrl.TrimEnd('/');
    }

    public async Task UpdateDataspiderBaseUrlAsync(string baseUrl)
    {
        if (string.IsNullOrWhiteSpace(baseUrl))
        {
            throw new InvalidOperationException("Dataspider URL cannot be empty.");
        }

        if (!Uri.TryCreate(baseUrl, UriKind.Absolute, out var uri) ||
            (uri.Scheme != Uri.UriSchemeHttp && uri.Scheme != Uri.UriSchemeHttps))
        {
            throw new InvalidOperationException("Dataspider URL must be an absolute HTTP or HTTPS URL.");
        }

        var settings = await _db.AppSettings.FindAsync(1);

        if (settings == null)
        {
            settings = new AppSettings
            {
                Id = 1,
                DataspiderBaseUrl = baseUrl.TrimEnd('/')
            };

            _db.AppSettings.Add(settings);
        }
        else
        {
            settings.DataspiderBaseUrl = baseUrl.TrimEnd('/');
        }

        await _db.SaveChangesAsync();
    }
}
```

Register it in `Program.cs`:

```csharp
builder.Services.AddScoped<AppSettingsService>();
```

## 5. Add The Dataspider Client

Register `HttpClient` without a fixed base URL:

```csharp
builder.Services.AddHttpClient<DataspiderClient>();
```

Client:

```csharp
public class DataspiderClient
{
    private readonly HttpClient _http;
    private readonly AppSettingsService _settings;

    public DataspiderClient(HttpClient http, AppSettingsService settings)
    {
        _http = http;
        _settings = settings;
    }

    public async Task StartScannerAsync(string symbol)
    {
        var baseUrl = await _settings.GetDataspiderBaseUrlAsync();

        var response = await _http.PostAsJsonAsync($"{baseUrl}/scanner/start", new
        {
            symbol,
            scan_interval_seconds = 60
        });

        response.EnsureSuccessStatusCode();
    }

    public async Task StopScannerAsync(string symbol)
    {
        var baseUrl = await _settings.GetDataspiderBaseUrlAsync();

        var response = await _http.PostAsJsonAsync($"{baseUrl}/scanner/stop", new
        {
            symbol
        });

        response.EnsureSuccessStatusCode();
    }

    public async Task<string> GetStatusAsync()
    {
        var baseUrl = await _settings.GetDataspiderBaseUrlAsync();
        return await _http.GetStringAsync($"{baseUrl}/scanner/status");
    }

    public async Task<string> HealthAsync()
    {
        var baseUrl = await _settings.GetDataspiderBaseUrlAsync();
        return await _http.GetStringAsync($"{baseUrl}/health");
    }
}
```

## 6. Add A Settings Page

Controller:

```csharp
public class SettingsController : Controller
{
    private readonly AppSettingsService _settings;

    public SettingsController(AppSettingsService settings)
    {
        _settings = settings;
    }

    [HttpGet]
    public async Task<IActionResult> Dataspider()
    {
        var url = await _settings.GetDataspiderBaseUrlAsync();
        return View(model: url);
    }

    [HttpPost]
    public async Task<IActionResult> Dataspider(string dataspiderBaseUrl)
    {
        await _settings.UpdateDataspiderBaseUrlAsync(dataspiderBaseUrl);
        return RedirectToAction(nameof(Dataspider));
    }
}
```

Razor view:

```html
@model string

<form method="post">
    <label for="dataspiderBaseUrl">Dataspider API URL</label>
    <input
        id="dataspiderBaseUrl"
        name="dataspiderBaseUrl"
        value="@Model"
        placeholder="http://127.0.0.1:8000" />

    <button type="submit">Save</button>
</form>
```

This page is where an admin changes the Dataspider URL.

## 7. Add Backend Endpoints For Buttons

The browser should call the .NET website. The .NET website calls Dataspider.

```csharp
[ApiController]
[Route("dataspider")]
public class DataspiderController : ControllerBase
{
    private readonly DataspiderClient _dataspider;

    public DataspiderController(DataspiderClient dataspider)
    {
        _dataspider = dataspider;
    }

    [HttpPost("start")]
    public async Task<IActionResult> Start([FromBody] DataspiderSymbolRequest request)
    {
        await _dataspider.StartScannerAsync(request.Symbol);
        return Ok();
    }

    [HttpPost("stop")]
    public async Task<IActionResult> Stop([FromBody] DataspiderSymbolRequest request)
    {
        await _dataspider.StopScannerAsync(request.Symbol);
        return Ok();
    }

    [HttpGet("status")]
    public async Task<IActionResult> Status()
    {
        var status = await _dataspider.GetStatusAsync();
        return Content(status, "application/json");
    }

    [HttpGet("health")]
    public async Task<IActionResult> Health()
    {
        var health = await _dataspider.HealthAsync();
        return Content(health, "application/json");
    }
}

public record DataspiderSymbolRequest(string Symbol);
```

## 8. Add Page Buttons

Example button markup:

```html
<button type="button" onclick="startScanner('ETHUSDT')">Start ETHUSDT</button>
<button type="button" onclick="stopScanner('ETHUSDT')">Stop ETHUSDT</button>
<button type="button" onclick="loadScannerStatus()">Status</button>

<pre id="dataspiderStatus"></pre>

<script>
async function startScanner(symbol) {
  const response = await fetch('/dataspider/start', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ symbol })
  });

  if (!response.ok) {
    alert('Failed to start scanner.');
  }
}

async function stopScanner(symbol) {
  const response = await fetch('/dataspider/stop', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ symbol })
  });

  if (!response.ok) {
    alert('Failed to stop scanner.');
  }
}

async function loadScannerStatus() {
  const response = await fetch('/dataspider/status');
  const text = await response.text();
  document.getElementById('dataspiderStatus').textContent = text;
}
</script>
```

## 9. Normal Workflow

1. Start Dataspider:

```bash
python3 -m scripts.api_server
```

2. Open `tradrpro.ai` settings page.
3. Save the Dataspider API URL:

```text
http://127.0.0.1:8000
```

4. Click `Start ETHUSDT`.
5. Click `Status` and verify `last_run_at`, `last_open_time`, and `saved_rows`.

## 10. Important Notes

- `python3 -m scripts.api_server` starts the Dataspider listener.
- `/scanner/start` starts the actual background scanner job.
- `curl` or the .NET client talks to the already-running listener.
- Use `POST` for start and stop.
- `GET /health` only means the HTTP server is alive.
- `GET /scanner/status` shows whether the scanner is running and whether it has errors.
- If Dataspider runs on a different server, save that server URL in the settings page.
- If Dataspider runs inside Docker or behind Nginx, save the reachable URL from the .NET server's point of view.
