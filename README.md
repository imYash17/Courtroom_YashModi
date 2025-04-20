# Courtroom_YashModi
It is an intelligent courtroom simulation system using Large Language Model (LLM) agents. 

# 🏛️ Courtroom Simulation with LLaMA 3 & Autonomous Agents

This project simulates courtroom trials using autonomous agents powered by LLaMA 3. It uses structured case data (CSV format) and a Supervisor Agent to dynamically conduct trials with Judges, Lawyers, and Witnesses. The goal is to evaluate the outcome (verdict) of each case through intelligent interaction and legal reasoning.

---

## 🎭 Agents Overview

### 🔹 CourtAgent
A base class for all role-playing agents. Each agent has:
- A **role** (e.g., Judge, Prosecutor, Defense, Witness)
- A **history** of previous interactions
- A **prompting method** for generating context-specific messages

## 🎭 General Structure
Each agent receives structured prompts and operates under clear responsibilities, ensuring realistic and role-consistent courtroom behavior.

---

## 👨‍⚖️ Judge

**Role:** Presides over the trial with neutrality and authority.

**Responsibilities:**
- Opens and moderates the trial
- Maintains order and discipline (especially when the audience reacts)
- Evaluates arguments, witnesses, and expert testimony
- Delivers the final verdict based on evidence and logic

**Reference:** `summary`, `facts`, and `final`

---

## ⚖️ Prosecution Lawyer

**Role:** Argues the case against the defendant.

**Responsibilities:**
- Presents claims, evidence, and witnesses to support the plaintiff
- Cross-examines the defense
- Challenges inconsistencies
- Delivers logical, ethical, and structured arguments

**Reference:** `prosecution_proof`

---

## 🛡️ Defense Lawyer

**Role:** Defends the accused party.

**Responsibilities:**
- Counters prosecution claims with logic and evidence
- Cross-examines prosecution witnesses
- Raises objections when procedures are violated

**Reference:** `defense_proof`

---

## 👨‍💼 Plaintiff

**Role:** Brings the case forward with a clear grievance.

**Responsibilities:**
- Explains the issue and supports their argument with facts
- Responds to legal questioning

**Reference:** `prosecution_proof`

---

## 👨‍💼 Defendant

**Role:** Responds to accusations and defends their position.

**Responsibilities:**
- Shares personal account and counters plaintiff's claims
- Replies to both legal teams

**Reference:** `defense_proof`

---

## 👁️‍🗨️ Witness 1

**Role:** Supports the Plaintiff.

**Responsibilities:**
- Shares firsthand account favoring the plaintiff
- Shows emotional nuance (e.g., confidence, hesitation)

**Reference:** `w1`

---

## 👁️‍🗨️ Witness 2

**Role:** Supports the Defendant.

**Responsibilities:**
- Provides testimony defending the accused
- Reacts to aggressive questioning with emotional realism

**Reference:** `w2`

---

## 👨‍🔬 Expert Consultant

**Role:** Neutral third-party expert on a domain relevant to the case (e.g., forensics, psychology).

**Responsibilities:**
- Provides clear, technical, unbiased analysis
- Can be questioned by both legal sides

**Reference:** `facts`

---

## 🎭 Audience

**Role:** Adds emotional atmosphere and realism.

**Responsibilities:**
- Reacts with whispers, gasps, or boos
- Can disrupt proceedings and trigger judge intervention
- Does not participate in arguments


## 🧠 SupervisorAgent

The **Supervisor Agent** acts as the orchestrator of the trial. It:
1. **Loads** the case details from a CSV file
2. **Initializes all agents** (Judge, Prosecutor, Defense, Witnesses)
3. **Determines trial flow**, such as:
   - Who speaks next
   - When witnesses are called
   - When the judge is asked to deliberate
4. **Stores the full conversation log**
5. **Evaluates the trial outcome**, including:
   - Arguments presented
   - Witness testimony quality
   - Case context

The Supervisor uses a loop-based system to alternate between agents, guiding the progression of the trial until a final verdict is issued.

---

## 📦 Input Case File (CSV)

1. Load legal case from CSV.
2. Summarize into using LLM model:
   - `summary`: Case context
   - `prosecution_proof`: Prosecution arguments
   - `defense_proof`: Defense arguments
   - `facts`: Objective data (law refs, dates, events)
   - `w1`: Witness for plaintiff
   - `w2`: Witness for defense
   - `final`: Suggested verdict & punishment
3. Feed each part into respective agent prompts (Judge, Prosecutor, Defense, Witnesses, etc).

---

## 📤 Output

After each case is processed:
- The **final verdict** is saved in `courtroom_results.csv`
- Includes:
  - `Case_ID`
  - `Verdict`: Binary value (1 = Granted, 0 = Denied)
  - `Verdict_Text`: The final statement from the Judge

You can process one or multiple cases by modifying the `case_index` or using a loop.

---

## 🚀 Usage

Run the simulation with:

```bash
python courtroom_simulation.py
