# SahiTol

An offline-capable Hindi/Marathi Android platform connecting informal scrap collectors with suitable formal destinations through transparent indicative prices, documented handovers and payment records, with recycler/admin web consoles.

**This repository currently contains the project documentation and execution system. The application has not been built.**

- [Start here: documentation guide](docs/00_README.md)
- [Whole project and settled choices](MASTER_CONTENT.md)
- [Implementation tracker](docs/08_TRACKER.md) and [requirements](docs/15_REQUIREMENTS.md)
- [AI agent instructions](AGENTS.md)
- [Session-start command](commands/session-start.md) and [session-continue command](commands/session-continue.md)
- [Mandatory owner-generated Stitch workflow](docs/05_DESIGN_STITCH.md)
- [Documentation coverage audit](docs/DOCUMENTATION_AUDIT.md)

To validate the documentation (Python 3.10+, standard library):

```text
python scripts/render_docs.py
python scripts/check_docs.py
```

Command files are ready to register as custom commands in your chosen IDE; they are not automatically installed. Keep this whole folder together so relative links and the shared catalog work. Read the guide before implementation: all six selected features are required, and primary collector fieldwork is explicitly recorded as an unmet external obligation under the desk-research choice.
