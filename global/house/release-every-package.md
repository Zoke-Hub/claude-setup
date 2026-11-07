---
name: release-every-package
description: A change to anything several packages or editions share goes into every one that carries it, in the same release, each tested the same way (a first install and an update that meets edited, deleted and added files); a package left out is named and asked about, never left behind quietly; ask when unsure
metadata:
  type: feedback
---

When a project ships in more than one package or edition (a public and a private edition, an installer and an add-on, a
download and a repository copy, a desktop and a web build), a change to anything they share (an installer or update
script, a rule file, a shared library, a template) goes into every package that carries it, in the same release.

- **Before building,** list which packages carry each changed file (for example: the shared installer goes into both
  editions; a file only one edition ships goes into that one). Rebuild every package on the list, not only the one being
  worked on. A package that already carries the change needs no rebuild; say so and why.
- **Test every rebuilt package the same way:** a first install, and an update from the version people have now, on a
  copy where files were edited, a file was deleted and a file was added by hand. Check that the update keeps each of
  those as the person left them, labels them correctly in every report or preview it gives, and writes only what is new
  or changed. A test that only edits files misses what happens to deleted or added ones.
- **A fix found while testing one package** is checked against every other package that shares the code, and goes into
  each of them too.
- **Nothing is left behind quietly.** If a package isn't rebuilt or released with the others (it waits for a go, or
  for a later round), name it, say what it is missing, and ask; never just mention it at the end as something for later.
- **Version numbers** follow what the person asked for each package; rebuilding to carry a change doesn't by itself
  mean a new number.
- **When unsure** whether a change belongs in a package, or whether a package needs a rebuild, ask before releasing.

**Why:** a fix that reached one edition but not another left a known bug in the released one, and a test that only edited
files never showed a deleted file being reported wrong. Shared code has to move together, and the tests have to cover
everything a person can do to their copy.

**How to apply:** at the start of any release, write down the packages and which changed files each carries; at the
end, check every package on that list was rebuilt, tested and released, or named and asked about.
