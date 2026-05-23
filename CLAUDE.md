# CLAUDE.md — Python Repository

This workspace has **gbrain** installed for persistent agent memory and knowledge management.

## GBrain Setup

- **Version:** 0.40.6.0
- **Engine:** PGLite (local, embedded Postgres via WASM — no server needed)
- **Brain location:** `~/.gbrain/brain.pglite`
- **Skills:** 46 skills scaffolded into `skills/`

### Quick start

```bash
export PATH="$HOME/.bun/bin:$PATH"
gbrain doctor          # verify health
gbrain stats           # show page/link counts
gbrain search "query"  # search the brain
```

### Install (if gbrain is not found)

```bash
bun install -g github:garrytan/gbrain
gbrain init --pglite --no-embedding   # or add an embedding key below
```

### Adding an embedding provider (optional but recommended)

```bash
# ZeroEntropy (default, fastest+cheapest) — get key at https://dashboard.zeroentropy.dev
export ZEROENTROPY_API_KEY=ze-...

# OR OpenAI
export OPENAI_API_KEY=sk-...

# Then reinit with the key
gbrain reinit-pglite --embedding-model zeroentropyai:zembed-1 --embedding-dimensions 1280
```

### Importing files into the brain

```bash
gbrain import ~/brain/          # import your markdown brain repo
gbrain embed --stale            # generate embeddings (requires API key)
```

## Skills

Read `skills/_AGENT_README.md` for the agent operating contract.

Skills are discovered by walking `skills/*/SKILL.md` and reading `triggers:` frontmatter.
Key skills available: `query`, `ingest`, `enrich`, `brain-ops`, `signal-detector`, `reports`, and more.

## Search Modes

Current mode: **conservative** (4K budget, no LLM expansion, 10 chunks max).

```bash
gbrain config set search.mode balanced    # 12K budget, 25 chunks
gbrain config set search.mode tokenmax   # no budget, LLM expansion, 50 chunks
gbrain search modes                       # see current config
```
