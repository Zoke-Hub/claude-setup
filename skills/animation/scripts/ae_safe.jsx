// Runs one script in After Effects so that nothing can stop on a dialog and wait for a person: AE's own errors and warnings
// are suppressed and any error is caught and written to the log for Claude to read. alert(), confirm() and prompt() can't be
// suppressed or replaced, so the runner (ae_run.sh, or ae_run.ps1 on Windows) refuses scripts that call them unguarded.
// Started by the runner, which sets $.global.__AE_TARGET (the script) and __AE_LOG (the log file).
(function () {
  var target = $.global.__AE_TARGET, logFile = new File($.global.__AE_LOG);
  function log(s) { logFile.encoding = "UTF-8"; logFile.lineFeed = "Unix"; if (logFile.open("a")) { logFile.write(s + "\n"); logFile.close(); } }
  $.global.__AE_LOG_LINE = log;
  $.global.__AE_QUIET = true; $.global.__MAPS_QUIET = true;      // the builders' own end-of-build messages
  // A fresh project with no Save box, ever: app.newProject() on unsaved work opens one. Only a project that is empty, saved, or
  // recognised as this job's own test (mine = a pattern for its comp names) is closed; anything else stops the script.
  $.global.__AE_NEW_PROJECT = function (mine) {
    var P = app.project, own = !P.dirty || P.numItems === 0;
    if (!own && !P.file && mine) for (var i = 1; i <= P.numItems; i++) if (P.item(i) instanceof CompItem && mine.test(P.item(i).name)) own = true;
    if (!own) throw new Error("the open project has unsaved work that isn't this test's: nothing was closed");
    P.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    return app.newProject();
  };
  var level = $.level; $.level = 0;                              // no debugger stop on an error
  app.beginSuppressDialogs();
  try {
    $.evalFile(new File(target));
    log("FINISHED");
  } catch (e) {
    log("ERROR " + e.toString() + " | line " + e.line + " | " + (e.fileName || target));
  }
  app.endSuppressDialogs(false);                                 // false: drop what was suppressed, show nothing
  $.level = level;
  if ($.global.__AE_LOCK) new File($.global.__AE_LOCK).remove();  // AE free again: the runner refuses to send anything until this is gone
})();
