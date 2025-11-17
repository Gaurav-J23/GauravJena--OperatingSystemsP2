# Devlog – Operating Systems Project 2

## 2025-11-16 14:00 – Initial Planning

### Thoughts so far

- This project is a bank simulation using threads in `main.py`.

- There are 3 teller threads and 50 customer threads.

- I have to control access to the door, manager, and safe with semaphores.

- The output format for customers and tellers has to match the spec exactly.

### Plan for this session

- Set up git and connect the local repo to GitHub.

- Create `devlog.md` and write this initial entry.

- Make sure `main.py` runs and compiles.

- Start wiring up the teller and customer threads with basic print statements.

## 2025-11-16 17:00 – Before Session

### Thoughts so far

- Yesterday I got the basic structure working with teller and customer threads.

- The program prints output, but I need to make sure the safe and manager limits are always correct.

- The current output order is different each run because of threading, which is expected.

- I've implemented semaphores for the door (2 customers), manager (1 teller), and safe (2 tellers).

- The bank opening coordination using an Event seems to be working correctly.

### Plan for this session

- Review semaphores for manager and safe to ensure they're properly enforced.

- Run the program multiple times and check that at most 2 tellers are in the safe at once.

- Verify that only 1 teller can talk to the manager at a time.

- Clean up the print format and make sure it matches the examples in the spec.

- Test the closing sequence to make sure all tellers leave properly after customers are done.

- Commit working changes.

## 2025-11-16 19:00 – After Session

### What happened this session

- Fixed the manager semaphore so only one teller can talk to the manager at a time.

- Verified through the output that at most 2 tellers are in the safe at the same time.

- Ran the simulation multiple times; the order changes but the rules are always followed.

- Confirmed that the door semaphore correctly limits to 2 customers in the bank.

- Tested the bank opening sequence - all tellers must be ready before customers can enter.

- Verified the closing sequence works correctly - all customers finish, then tellers leave, then bank closes.

- Cleaned up unnecessary comments in the code, keeping only the important ones that explain synchronization logic.

### Problems or things to improve

- Some of the log messages are still a little messy; I want to refactor them to be more consistent.

- The code structure is good, but I want to make sure all the synchronization is bulletproof.

- Need to double-check that exactly 50 customers are being processed.

### Plan for next session

- Clean up all print statements to ensure they match the spec format exactly.

- Double-check that the number of customers is exactly 50.

- Add more thorough testing to catch any edge cases.

- Review the code one more time for any potential race conditions.

- Add final polish before submitting the project.
