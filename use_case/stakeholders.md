# Stakeholders

Everyone you talk to about this project, from the first "where would this even
run?" to the final readout.

> **Week 10's technical challenge is a report to the people in this file.**
> You cannot write it later from memory. Add a row the day you have the
> conversation.

Use roles, not names. This is a public repo.

| Week | Who (role) | What you asked | What you learned | Follow-up |
| --- | --- | --- | --- | --- |
| 1 | The Principal Software Engineer of my team | where would a container run here? | The container would run on the internal k8s platform | no follow-up was necessary |
| 2 | Principal engineer of my team | Showed 20 synthetic rows and the datasheet, and asked: (1) which of these would never actually happen? (2) what comes in that is not here at all? (3) if this were public, what would worry you? | They felt that at this point I am not required to have any more context on the problem | If this tool gets picked for a production cycle, at that point necessary redesigns and data related conversations will be made|

---

## Not everyone is an infrastructure contact

The useful list is wider than it first looks, and Week 10's report goes to all of
them:

- **The person with the problem** — the one from your charter. Have you shown
  them anything yet?
- **Whoever owns the data** you would need.
- **Whoever runs the platform** your app would deploy onto.
- **Whoever approves** a deployment, a spend, or a vendor.
- **Your own manager**, who will be asked whether this was worth the ten weeks.

If a week goes by with no conversation, add a row saying so and why. A visible
gap is more useful than a silent one.
