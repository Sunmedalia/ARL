# Integration tests

These tests require one or more real services, network access, credentials, or
bundled scanner executables. They are deliberately named `integration_*.py`, so
the default offline unit command does not collect them.

Run them only in a prepared, authorized environment:

```bash
python -m unittest discover -s test/integration -p 'integration_*.py'
```

The default deterministic suite remains:

```bash
python -m unittest discover -s test -p 'test_*.py'
```
