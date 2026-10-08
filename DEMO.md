# Three-minute demo outline

Use the running application, record your screen, and explain in English. Suggested wording should be adapted to your actual implementation and findings.

## 0:00–0:25 — Problem

Students often have a limited lunch break. A short walk does not necessarily mean a short lunch: table occupancy, group size and queues affect whether they can return before class.

## 0:25–1:10 — Student flow

Show departure at 12:00, class at 13:00 and a two-person group. Calculate the three restaurant options. Explain the outbound, waiting, dining and return components. Expand table estimates and point out that a group needs a table large enough to seat everyone.

## 1:10–1:50 — Changing conditions

Use Restaurant controls to free a table or lengthen a queue. Show the updated estimates. Change travel modes or the class deadline. Explain that the status also reserves a five-minute buffer.

## 1:50–2:20 — What actually runs

The local Python server runs an empirical conditional duration model and a table scheduling algorithm. The demo uses synthetic records, not live restaurant data. The cautious scenario is not a calibrated probability of arriving on time.

## 2:20–2:50 — Hardware plan and validation

The planned restaurant-side deployment uses local vision inference on the selected accelerator to produce anonymous table occupancy events. The current prototype does not include that hardware integration. Next steps are collecting real seating sessions, evaluating wait-time errors, and measuring performance on the target device.

## 2:50–3:00 — Close

Show the GitHub repository and the prototype's current capabilities. Do not claim measured real-world improvement before conducting an evaluation.

# Course submission checklist

- [ ] Competition registration and Stage I submission completed, with confirmation retained.
- [ ] English slides; main content no more than 20 pages.
- [ ] Team members' names and student IDs included.
- [ ] Final slide contains working GitHub and demo-video links.
- [ ] Every member individually uploads `{Student_ID}_CN_league.pdf` to the course page.
- [ ] Course deadline: 2026-10-14, per the supplied assignment; verify exact cutoff time.
- [ ] Check the official competition rules and disclose prototype limitations and AI assistance accurately.

Creating a repository alone does not complete competition or course submission.
