---
name: answer-buttons-complete
description: Reply buttons under a question send their text at once, so each must be a complete answer; never a half-sentence for the user to finish
metadata:
  type: feedback
---

A reply button in the next-step box sends its message the moment it is clicked; the user gets no chance to add to it.
So **every button's message must be a complete answer on its own.** Never end one with a colon or a gap for the user to
fill in ("Here's what I'd change: ", "What I saw: ").

**Why:** a half-finished button sends the empty start of a sentence. The user loses what they meant to say, and Claude
acts on a message that says nothing.

**How to apply:**
- Make each button one whole choice: "Yes, build it", "Keep the current layout", "Read the log".
- When the answer needs the user's own words (what they saw, what to change, a value), ask the question in the box with
  no button for it, or with buttons for the likely whole answers only; the user types the rest in the prompt.
- A button may carry detail in its message, but only detail Claude already knows the user would mean.
