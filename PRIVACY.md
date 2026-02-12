# Privacy Policy

**langlearn-tts** version 0.5.1

## Data We Collect

None. langlearn-tts does not collect or store any user data. It transmits text only to the TTS provider you configure when you initiate synthesis. All other processing happens locally on your machine.

## Local Logging

langlearn-tts writes local log files to `~/.langlearn-tts/logs/` (primary: `langlearn-tts.log`, up to 5 rotated backups). These logs record:

- Provider name, voice name, and character count per API call
- File paths of generated audio

The log does **not** contain the text you synthesize. Log files rotate at 5 MB with 5 backups and never leave your machine.

## Third-Party Services

When you use langlearn-tts, the text you provide is sent to the TTS provider you select. Each provider has its own privacy policy:

- **ElevenLabs**: [Privacy Policy](https://elevenlabs.io/privacy-policy)
- **OpenAI**: [Privacy Policy](https://openai.com/policies/privacy-policy)
- **AWS (Amazon Polly)**: [Privacy Notice](https://aws.amazon.com/privacy/)

You are responsible for reviewing and agreeing to your chosen provider's terms before use. langlearn-tts acts as a local client to these services and does not intermediate, cache, or re-transmit your data beyond the direct API call.

## API Keys

API keys you configure are stored locally by the Claude Desktop application using OS-level secure storage (macOS Keychain / Windows Credential Manager) when installed as a Desktop Extension. langlearn-tts itself does not persist API keys.

## Contact

Questions or concerns: [GitHub Issues](https://github.com/jmf-pobox/langlearn-tts-mcp/issues)
