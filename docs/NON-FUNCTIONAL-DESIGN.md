# Non-Functional Design: Logging & Exception Handling

## Logging

### Standard

All logging follows PEP 282 and the Python `logging` module best practices.

### Logger declaration

Every module that logs declares a module-level logger:

```python
logger = logging.getLogger(__name__)
```

Modules that perform no I/O, contain only data definitions, or are pure functions
with no side effects need not declare a logger. Examples: `types.py` (data models
and voice resolution cache).

### Configuration

Logging is configured **once**, at the application entry point only:

- **CLI** (`cli.py`): `logging.basicConfig(level=logging.INFO)` inside the
  `main()` Click group; `-v` flag switches to `DEBUG`.
- **MCP server** (`server.py`): `logging.basicConfig(level=logging.INFO)` at
  module level (the module is only imported when the server starts).

Library modules never call `logging.basicConfig`. They emit via `getLogger(__name__)`
and let the application configure the handler.

### Log levels

| Level | Use |
|-------|-----|
| `DEBUG` | Internal state useful during development: variable values, branch decisions, intermediate computation results. |
| `INFO` | Operational milestones a user or operator would want to see: starting a job, completing a step, resource counts. |
| `WARNING` | Unexpected but recoverable conditions: empty input producing zero output, deprecated parameter usage. |
| `ERROR` | Failures that prevent an operation from completing but do not crash the process. Always accompanied by exception context. |

`CRITICAL` is not used. If the process must exit, it raises an exception.

### What to log

**INFO-level events (the operational narrative):**

- External service calls: Polly synthesis requests, voice API lookups.
- File writes: output MP3 paths and sizes.
- Audio stitching: segment count, output path.
- MCP server lifecycle: startup.

**DEBUG-level events (development diagnostics):**

- Voice resolution details (voice ID, text preview).
- API call parameters.
- Voice cache population count.

**WARNING-level events:**

- `afplay` not available on non-macOS (auto-play skipped).

**ERROR-level events:**

- AWS API failures — logged with `logger.exception()`.
- File I/O failures — logged with `logger.exception()`.

### What not to log

- AWS credentials, API keys, access tokens.
- Full text content for long inputs (log text preview and character count instead).
- Per-iteration progress in tight loops (log summary counts).

### Format

Log messages use `%s`-style formatting (lazy evaluation), not f-strings:

```python
logger.info("Wrote %s", output_path)                         # correct
logger.info(f"Wrote {output_path}")                           # incorrect
```

### Structured context

Include enough context to trace an operation without reading code:

```python
logger.info("Stitched %d segments → %s", len(segments), output_path)
```

Not:

```python
logger.info("Stitching complete")
```

---

## Exceptions

### Standard

Exception handling follows PEP 8 and the principle that **exceptions represent
contracts**: a function either succeeds and returns its documented type, or raises a
documented exception. There is no middle ground.

### Exception hierarchy

The codebase uses **built-in exception types** and does not define custom exceptions
unless a caller needs to distinguish between failure modes programmatically. The
current types are sufficient:

| Exception | Raised when |
|-----------|-------------|
| `ValueError` | Invalid input: unknown voice name, empty segment list, bad parameter value. |
| `FileNotFoundError` | A segment file does not exist during stitching. |
| `botocore.exceptions.ClientError` | AWS API errors (permissions, throttling). |
| `botocore.exceptions.NoCredentialsError` | AWS credentials not configured. |
| `OSError` | File I/O failures (write errors, permission denied). |

If future code needs a domain-specific exception (e.g., to distinguish provider
errors across Polly/ElevenLabs/OpenAI), define it in `types.py` as a subclass of
`Exception` with a clear docstring.

### Rules

1. **Never swallow exceptions.** Every `except` block must either:
   - Re-raise the exception (bare `raise`), or
   - Log it with `logger.exception()` and raise a different exception, or
   - Log it with `logger.exception()` and return a documented sentinel (only at
     system boundaries like MCP tool handlers).

2. **Never use bare `except:`.** Always catch a specific type.

3. **Never catch `Exception` broadly** in library code. Broad catches are permitted
   only at the outermost boundary (MCP tool handler, CLI command) where they
   produce a user-facing error message. Even then, log with `logger.exception()`.

4. **Exceptions carry context.** Every `raise` includes a message with the values
   that caused the failure:

   ```python
   msg = f"Unknown voice '{name}'. Available: {available}"
   raise ValueError(msg)
   ```

   Not:

   ```python
   raise ValueError("bad voice")
   ```

5. **Document raised exceptions** in docstrings using the `Raises:` section. Every
   public function that raises documents what and when.

6. **Use `try/finally` for cleanup**, not `try/except`. The `PollyClient` uses
   `tempfile.TemporaryDirectory()` as a context manager for temporary audio
   segments — cleanup happens automatically regardless of exceptions.

7. **Boundary handlers (MCP tools, CLI commands)** may catch exceptions to produce
   user-friendly messages. They must still log the full traceback:

   ```python
   try:
       result = client.synthesize(request, output)
   except botocore.exceptions.NoCredentialsError:
       logger.exception("Synthesis failed for %r", text)
       return "Error: AWS credentials not configured. Run `aws configure`."
   ```

8. **Do not use exceptions for flow control.** Check preconditions explicitly:

   ```python
   if not segments:
       raise ValueError("segments must not be empty")
   ```

   Not:

   ```python
   try:
       first = segments[0]
   except IndexError:
       raise ValueError("no segments")
   ```
