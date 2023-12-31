# Owl Data Tools

Owl Data Tools is a collection of tools designed to handle the log data generated by [Watchful Owl](https://github.com/Lutfi221/watchful-owl).

Owl Data Tools can consolidate log data from multiple files into a single managable file, and generate a report regarding the data.

- [Owl Data Tools](#owl-data-tools)
  - [Guides](#guides)
    - [Consolidating/Merging log files](#consolidatingmerging-log-files)
  - [Consolidated Owl Logs Format](#consolidated-owl-logs-format)

## Guides

### Consolidating/Merging log files

Use `-i` to add input files to be consolidated. The supported input files are `.json.log` (files generated by [Watchful Owl](https://github.com/Lutfi221/watchful-owl)), and [COLF](#consolidated-owl-logs-format) files in `.json`. GLOB patterns are supported.

Use `-o` to specify an output file. The output file will be in [Consolidated Owl Logs Format](#consolidated-owl-logs-format) in json.

```bash
owlts -i 20230912.json.log -i *.json.log -o consolidated.colf.json
```

You can also merge [COLF](#consolidated-owl-logs-format) files together.

```bash
owlts -i january.colf.json -i february.colf.json -o fin.colf.json
```

## Consolidated Owl Logs Format

Consolidated Owl Logs Format (COLF) is a file format designed to hold large amounts of owl logs data efficiently.

Here is an example of a basic COLF file structure.

```json
{
  "version": "0.0.0",
  "dictionaries": [
    {
      "name": "windows[].path",
      "set": ["c:/programs/chrome.exe ", "c:/programs/code.exe"]
    },
    {
      "name": "windows[].title",
      "set": ["Chrome", "VS Code"]
    }
  ],
  "entries": [
    {
      "time": 1676257718,
      "windows": [
        {
          "path": 0,
          "title": 0,
          "isActive": true
        },
        {
          "path": 1,
          "title": 1,
          "isActive": true
        }
      ]
    }
  ]
}
```
