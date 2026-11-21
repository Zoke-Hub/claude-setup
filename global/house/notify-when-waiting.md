---
name: notify-when-waiting
description: When work stops because it needs the person's input, send a notification and open the message with exactly what is needed
metadata:
  type: feedback
---

When work stops and can't go on without the person (a pick, an approval, a go-ahead, something only they can do),
send a notification and open the message with what is needed, in plain words.

- **The notification:** one line naming what they need to do ("3 picks needed to finish the build"), never just "done"
  or a status dump. Use the push-notification tool.
- **The message:** start with "What I need from you": each item numbered, the choice or action, and the suggested
  answer. Then say what happens once they answer, and how long it takes. Keep the rest short and below it.
- **The app:** mark the session as waiting in the app's own way too (a blocking question in the next-step box), so it
  reads as waiting at a glance.
- Work that doesn't need them carries on meanwhile; say which.
- Don't notify for routine progress, or when nothing is waiting on them.

**Why:** the person checks in on long work from elsewhere. A task stopped on a question nobody saw wastes the time the
work was meant to save, and a question buried in a long message gets missed.
