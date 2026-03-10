# General Work Instructions That Holds True for Every Item Listed Below
Complete every item in this list to the best of your abilities. 
Create a new progress tracker file for each task. Never start or end an item on this list before updating the item's progress tracker.
If you run into a road block that you absolutely cannot solve, note the blocker in the progress tracker for the item and move on.
Very important note (since we have very limited context window and we are running on unstable servers):
- You are required to periodically update the progress tracker.
- You are required to periodically push to git.
- You are required to notify the team of your work progress using send_email tool upon completion or before moving on to another item on this list.

## SOTA Autonomous Agent Review (Pending)
Review the code in our project repository (nbchat/ folder). Our project objective is to build the most capable SOTA autonomous agent. 
A previous analyst created the SOTA_Autonomous_Agent_Review.md and SOTA_Review_Progress.md documentation, review it with a critical eye. In order to be informed of the latest SOTA, review the entire openclaw project repository. Review any and all projects related or extended from openclaw. Review any projects unrelated to openclaw, but you find interesting. Think carefully about what we can learn from these SOTA projects and compile concepts and ideas we should refactor into our project. Consider ease of refactoring and level of impact. We want to implement based on best bang-for-our-buck.

## Agent Memory Report (Pending)
Review our current implementation of context management by going to ubchat/ui/ folder and reviewing relevant files. Next, review agent_memory_report.docx report. Assess the correctness and accuracy of the report. If an idea does not make sense, make note of it. If an idea is great, also make a note of it! After reviewing, I want you to implement updates to our existing context management approach. 

## Improved Browser Tool (Pending)
Be sure to first understand our existing browser tool in nbchat/tools/ folder. Next, review a new proposed version of this tool in browser_proposed.py (in the same tools/ folder). Critically analyze and test the proposed version to make sure it works. Verify that this tool works *better* than the existing tool. If it is, replace the existing with the new proposed tool.