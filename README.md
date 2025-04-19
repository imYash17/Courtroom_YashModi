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

### 🔹 Judge
- Gives the **final verdict**
- Reviews all arguments and witness testimonies
- Speaks only when prompted by the Supervisor

### 🔹 Prosecutor
- Presents the case **against** the defendant
- Refers to relevant facts from the case document
- Cross-examines witnesses (if any)

### 🔹 Defense
- Defends the accused based on case facts
- Challenges the prosecutor’s arguments
- Can also question witnesses

### 🔹 Witnesses
- Provide evidence or personal testimony
- Respond to questions from both lawyers
- Their statements influence the final judgment

---

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

The input CSV contains rows of case data. Each row includes:
- `id`: Unique identifier for the case
- `summary`: A high-level description of the situation
- `context`: Factual case details
- `witness_1` to `witness_3`: Statements from witnesses
- `expected_verdict`: (Optional) Ground-truth label for evaluation

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
