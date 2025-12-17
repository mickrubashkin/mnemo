# mnemo | Local Notes Indexer

`mnemo` is a local CLI tool for indexing and searching personal notes.

It builds a searchable index of your notes and lets you quickly find and open relevant entries from the terminal.

Everything works locally.

### Why mnemo

I keep notes in multiple apps over many years. Searching them efficiently became harder than writing new ones.

mnemo is a small CLI tool that solves this problem locally and predictab.

It works just fine for me.

### Supported sources

- Apple Notes
- Bear (macOS)

### Installation

Run without installation (via uv):

```bash
uvx mnemo
```

Install as a CLI tool:

```bash
uv tool install mnemo
```

### Usage

Initialize a project and build the index:

```bash
mnemo init
```

Search notes:

```bash
mnemo search python ai
```

Open a note from search results:

```bash
mnemo open 1
```

Rebuild the index:

```bash
mnemo rebuild
```

### Notes

- Index is stored locally in the project directory (`.mnemo`)
- Designed for personal knowledge bases
- Optimized for fast iteration and extensibility

### Status

Early-stage MVP.

### Possible next steps

- Improved search ranking
- Improved result snippets with highlighted matches
- Additional note sources (Notion, Google Docs)
- Indexing local folders (`txt`, `md`)
