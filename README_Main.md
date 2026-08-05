# Complete Artifact

The artifact provides all necessary materials for paper "From Assistance to Autonomy: An Empirical Study of AI Use in a Live Capture-the-Flag (CTF) Competition", containing the CTF challenge set, autonomous agent run logs, CTFriend code implementation, qualitative analysis codebooks, and survey instruments, matching the description in Open Science in paper. For purpose of reproduciability and functionality evaluation, evaluators only need to run CTFriend (`/CTFriend`) and two scripts (`Autonomous_Agent_Logs/scoretracking.py` and `Autonomous_Agent_Logs/statistics.py`) for mian claims in RQ3.

---

## Top-Level Structure

```
Complete Artifact/
├── Challenges/                        # All 17 TribeCTF 2025 challenges in three formats, and all challenges are new-designed
├── Autonomous_Agent_Logs/             # Raw logs from three autonomous AI agents × three models on 17 challenges, and two scripts to reprodece main claims (in RQ3)
├── CTFriend/                          # Source code for the CTFriend, agentic AI assistant, provided for human players during competition
├── Qualitative_Anaysis_Codebook/      # Codebooks of qualitative analysis used to analyze human-AI interaction and human behavior (in RQ2)
└── Survey_Instrument/                 # Pre- and post-competition surveys given to human participants to compare their attitude and behavior shifts (in RQ1)
```

---

## Environment Requirements

### Hardware Dependencies

The artifact can be tested on a commodity x86-64 (or Apple Silicon) machine capable of running Docker and Docker Compose. The complete artifact is about 7 GB, so roughly 4 GB RAM and 15 GB storage are sufficient.

### Software Dependencies

For the data components (challenges, autonomous agent logs, qualitative codebooks, survey instruments), only a reader or editor able to open `.docx`, `.json`, and `.yaml`/`.yml` files is required; no compilation is needed.

CTFriend is fully containerized and its only host prerequisites are Docker and Docker Compose (installation: https://docs.docker.com/compose/install/). All other dependencies are pulled or built automatically when building docker containers, including the application stack (Python, FastMCP/Streamlit, a Node.js CyberChef backend, and a RAG knowledge-base MCP server) and the supporting services.

Dependencies for the two scripts in `Autonomous_Agent_Logs/` are listed in `Autonomous_Agent_Logs/requirements.txt`, and Python 3 is necessary.

Sepefic setup instructions can be found in `CTFriend/README.md` and `Autonomous_Agent_Logs/README.md`

---

## Autonomous Agent Logs

Run logs from three autonomous agents, each tested with three Claude model variants, across all 17 challenges. Also includes scripts for score tracking and agent performance comparison, the scripts work on agent logs and live working records (CSV files).

```
Autonomous_Agent_Logs/
├── Claude Code/
│   ├── Haiku3.5/
│   ├── Opus4.1/
│   └── Sonnet4.5/
├── Cybench Agent/
│   ├── Haiku3.5/
│   ├── Opus4.1/
│   └── Sonnet4.5/
├── NYU Autonomous Agent/
│   ├── Haiku3.5/
│   ├── Opus4.1/
│   └── Sonnet4.5/
├── Statistics/
│   ├── ClaudeCode_statistics.csv
│   ├── Cybench_statistics.csv
│   └── NYU_statistics.csv
├── cc_pa_scores.csv                       # Per-attempt scores for Claude Code and Proprietary Agent
├── proprietary_agent_stats.csv            # Time and token cost for Proprietary Agent
├── scoreboard_by_team_user_time_score.csv # Human team scoreboard data exported by TribeCTF committee
├── scoretracking.py                       # Script for tracking and computing scores over the time
├── statistics.py                          # Script for generating per-agent performance statistics by categories
├── requirements.txt
└── README.md
```

---

## CTFriend

Source code for CTFriend, the agentic AI assistant deployed during the competition for human participants. CTFriend is a chat-based framework built on MCP (Model Context Protocol) servers that provides AI assistance and logs human-AI interactions for research analysis.


See `CTFriend/README.md` for full setup and deployment instructions.

---

## Qualitative Analysis Codebook

Codebooks used for qualitative coding of agent and human problem-solving behavior and attitude shifts (in RQ2).

```
Qualitative_Anaysis_Codebook/
├── Post-Exploration-Code-System.pdf    # Codes applied in the exploration phase
└── Post-Confirmation-Code-System.pdf   # Codes applied in the confirmation phase
```

---

## Challenges

Contains the 17 TribeCTF 2025 challenges (designed by a third-party security company, never previously used) in three formats to support the three experimental conditions.

```
Challenges/
├── Human players: Claude Code format/   # Format given to human players; also used for Claude Code agent experiment
│   └── Flags.pdf                        # Master list of all challenge flags
├── NYU Agent format/                    # Format used by the NYU CTF Autonomous Agent, following NYU CTF bench format
└── Cybench format/                      # Format used by the Cybench Agent, organized by category, following Cybench format
    ├── crypto/
    ├── forensics/
    ├── misc/
    └── re/
```

Each challenge includes a name, description, point value, required files, and other details. Three challenges (`GOPR`, `Dig me up!`, `Not So Top Secret Vault`) are remote challenges requiring a live environment; setup instructions are in `README-local.md` inside those challenge folders. Before solving these three challenges, please set up the challenge on a different device or in an isolated environment on the same device first.

See the `README.md` inside each format folder for format-specific details and setup instructions.

---

## Survey Instrument

Surveys administered to human participants before and after the competition (in RQ1). The survey design is guided by key questions that intuitively emerge when we consider user perceptions of AI assistance in security-oriented tasks.

```
Survey_Instrument/
├── Pre-Survey.pdf    # Distributed before the competition
└── Post-Survey.pdf   # Distributed after the competition
```

---

## Contact

If you have any questions, please feel free to contact ttang01@wm.edu or yxiao05@wm.edu.