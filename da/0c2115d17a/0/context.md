# Session Context

## User Prompts

### Prompt 1

Implement the following plan:

# Release v0.6.3

## Context

The output directory consolidation fix (PR #29, lltts-612) is merged to main. Users on `0.6.2` may get files written to cwd instead of `~/langlearn-audio`. We need to release `0.6.3` to PyPI and build a new `.mcpb` Desktop Extension bundle.

## Version bump: 0.6.2 → 0.6.3

Three files to update:
- `pyproject.toml:3` — `version = "0.6.2"` → `"0.6.3"`
- `src/langlearn_tts/__init__.py:7` — `__version__ = "0.6.2"` → `"0.6.3"`
- `...

### Prompt 2

OK, we were waiting on punt labs to be approved by PyPI as an org, but there is a transfer function so we can publish in my personal account and then go from there. So you can switch to work on PyPI publishing for langlearn-types.  However ** you need to prefix it with punt- and you need to migrate langlearn-tts to punt- as well. This is been part of our plan.

### Prompt 3

OK, make sure the beads are correct in both projects.

### Prompt 4

Can we run an experiment? I'd like to register langlearn-tts as an MCP service with our claude code session.

### Prompt 5

project-local this is just a quick test.

### Prompt 6

OK, can you use synthesize to say something to me in English?

### Prompt 7

This is f*cking awesome. We are going to be famous.

### Prompt 8

First, we have a small bug.  The rachel voice is somewhere in our prompts and it is wrong.  I have seen that elsewhere.

### Prompt 9

Not sure how to map those to the ones I see in the dashboard, such as https://elevenlabs.io/app/voice-library?voiceId=1t1EeRixsJrKbiF1zwM6

### Prompt 10

Matilda

### Prompt 11

yes

### Prompt 12

check for the feedback

### Prompt 13

merge it

### Prompt 14

release v0.6.4

### Prompt 15

# Reconcile Project with Punt Labs Standards

Analyze a project against Punt Labs standards and surgically apply fixes. This command
handles files that need **contextual judgment** — workflow customizations, CLAUDE.md
quality, pyproject.toml drift — where a deterministic tool would be too blunt.

## Input

Project path:  (defaults to `.` if empty)

## Process

### 0. Detect Project

Read the project's `pyproject.toml` or `package.json` to determine:

- Language (python, node, swift, or none)...

### Prompt 16

commit this on a branch and open a PR

### Prompt 17

check the CI status in 5m, address valid points of concern, then merge.

### Prompt 18

This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Analysis:
Let me trace through the conversation chronologically:

1. **Release v0.6.3**: User provided a detailed plan to release v0.6.3. I executed all steps:
   - Bumped version in pyproject.toml, __init__.py, manifest.json (0.6.2 → 0.6.3)
   - Updated CHANGELOG.md with [0.6.3] - 2026-02-22 section
   - Ran quality gates (241 tests pass)
   ...

### Prompt 19

great, synthesize your voice and tell me bead you recommend we work on next.

### Prompt 20

<!-- markdownlint-disable MD041 -->

## Input

Arguments: .

Determine the ingestion method:

1. If it starts with `http://` or `https://`: **URL** (auto-discovers sitemaps)
2. If it's a local directory path (ends with `/` or is a known directory): **Directory** (register + sync)
3. Otherwise: **File** (single file ingestion)

Expand `~` to the user's home directory before calling any tool.

## Task

Call the appropriate tool(s):

- **URL**: `mcp__plugin_quarry_quarry__ingest_auto` with `url` se...

### Prompt 21

Thanks, good idea. But I am going to blow your mind - read the punt-kit standards and also the ../public-website. We are going to generalize langlearn-tts beyond tts. I want to create the claude code plugin to give you a voice. We can have commands like /speak y n or /voice y n and we can use strategies like hooks and other proven integration points from other punt-lab projects to help you start vocalizing when appropriate. I want to do some "vision" work to establish what this could look like. ...

### Prompt 22

1. Generalize langlearn-tts. Just did something similiar with quarry where we made the Claude Code integration points, did not require any new MCP tools over what was used in Claude Desktop.  2. TBD.  I was thinking that biff would call this MCP server for commands like /wall or /talk or anything written to the status bar. Yes, suppress output hook yes. We cannot have some huge blob of json all of the time, either for what we synthesize or what the response is.   Short-version, I'd like to see a...

### Prompt 23

3. Output should become non-persistent in some cases. if the MCP is being used in claude code the files would need to be .tts/* or something and then removed after being played. For the langlearn case, you would want the user to be able to replay them. On the name, I think it has to be punt-tts - there is a complication though in that langlearn-tts uses types that are shared between langlearn packages. Maybe we have to have an bridge package (very thin) called langlearn-tts that glues punt-tts a...

### Prompt 24

1. tts 2. yes, 3. delete after playback. If you are worried about blocking, you can delete all files other than the one being played, which means there should be at most one file and then delete that one on session end.

### Prompt 25

create beads for this, however the wire up biff should be written from the other perspective wire up tts in the biff beads repo.  Also, you may want to consider create the punt-tts beads in a new bd in that new repo. Anyway, you get the idea.  If possible, put the beads in the repo where the work happens.

### Prompt 26

OK, create a plan and ask for my approval.

### Prompt 27

[Request interrupted by user for tool use]

