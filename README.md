# CS4348 Project 2 – Bank Simulation

## Overview

This project implements the bank simulation described in the Project 2 specification for CS4348 (Fall 2024).

- The bank has **3 teller threads**.
- There are **50 customer threads**.
- Each customer randomly chooses to perform either a **deposit** or a **withdrawal**.
- The **bank opens** only after all three tellers are ready.
- At most **2 customers may be inside the bank** at a time (door constraint).
- At most **2 tellers may be inside the safe** at the same time.
- At most **1 teller may interact with the manager** at any time.
- The program prints a detailed log of what each teller and customer does.
- After all 50 customers are served and have left, all tellers leave and **the bank closes for the day**.

Because this is a multithreaded simulation, the **exact order of the log lines may change between runs**, but all synchronization constraints are always respected.

---

## Files

- `main.py`  
  Main program. Creates and starts teller and customer threads, sets up semaphores, and prints all log messages. All project logic is here.

- `devlog.md`  
  Development log for the project. Contains dated entries before and after each coding session, including plans, progress, problems, and reflections, as required by the assignment.

- `project2.pdf`  
  Copy of the project specification provided by the instructor (included for reference).

- `README.md`  
  This file. Explains the project, how to run it, and any notes for the grader.
---

## How to Run

### Requirements

- **Python 3** (3.x – tested with Python 3.10+)
- No external libraries are required; only the Python standard library is used (`threading`, `time`, `random`).

### Running from the command line

From the project directory (the one containing `main.py`):

On **Linux / macOS**:

```bash
python3 main.py
