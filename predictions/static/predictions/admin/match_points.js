// Match admin: for Tennis, Badminton and Cricket, typing Team A win points fills the
// other points fields as a 100-point split. Example: A win 60 gives
// A lose -40, B win 40, B lose -60, Draw win 0 and Draw lose 0.
// The sport ids are embedded on the Sport <select> as
// data-autofill-points-sports (see MatchAdminForm in predictions/admin.py).
// For Football (data-lose-from-win-sports), each win points field fills its
// own lose points as win - 100: Team A, Team B and Draw.
// Only typing into a win points field triggers it, so saved values are never
// overwritten on page load, and every field stays editable afterwards.
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var sportSelect = document.getElementById("id_sport");
    var aWin = document.getElementById("id_team_a_win_points");
    var aLose = document.getElementById("id_team_a_lose_points");
    var bWin = document.getElementById("id_team_b_win_points");
    var bLose = document.getElementById("id_team_b_lose_points");
    var drawWin = document.getElementById("id_draw_win_points");
    var drawLose = document.getElementById("id_draw_lose_points");
    var aOdds = document.getElementById("id_team_a_odds");
    var bOdds = document.getElementById("id_team_b_odds");
    var drawOdds = document.getElementById("id_draw_odds");
    if (!sportSelect || !aWin || !aLose || !bWin || !bLose || !drawWin || !drawLose) {
      return;
    }

    function calcWinLose(oddVal) {
      if (oddVal === null || oddVal <= 1.0) return null;
      var win = Math.round(100.0 - (100.0 / oddVal));
      var lose = win - 100;
      return [win, lose];
    }

    function floatValue(input) {
      if (!input) return null;
      var val = parseFloat(input.value.trim());
      return (!isNaN(val) && isFinite(val) && val > 1.0) ? val : null;
    }

    if (aOdds) {
      aOdds.addEventListener("input", function () {
        var pts = calcWinLose(floatValue(aOdds));
        if (pts) {
          aWin.value = pts[0];
          aLose.value = pts[1];
        }
      });
    }

    if (bOdds) {
      bOdds.addEventListener("input", function () {
        var pts = calcWinLose(floatValue(bOdds));
        if (pts) {
          bWin.value = pts[0];
          bLose.value = pts[1];
        }
      });
    }

    if (drawOdds) {
      drawOdds.addEventListener("input", function () {
        var pts = calcWinLose(floatValue(drawOdds));
        if (pts) {
          drawWin.value = pts[0];
          drawLose.value = pts[1];
        }
      });
    }

    var autofillSports = [];
    var loseFromWinSports = [];
    try {
      autofillSports = JSON.parse(sportSelect.dataset.autofillPointsSports || "[]")
        .map(String);
      loseFromWinSports = JSON.parse(sportSelect.dataset.loseFromWinSports || "[]")
        .map(String);
    } catch (e) {
      return;
    }

    function intValue(input) {
      var value = input.value.trim();
      return /^-?\d+$/.test(value) ? parseInt(value, 10) : null;
    }

    aWin.addEventListener("input", function () {
      if (autofillSports.indexOf(sportSelect.value) === -1) {
        return;
      }
      var win = intValue(aWin);
      if (win === null) {
        return;
      }
      var rest = 100 - win;
      aLose.value = -rest;
      bWin.value = rest;
      bLose.value = -win;
      drawWin.value = 0;
      drawLose.value = 0;
    });

    // Football: each win points field fills its own lose points as
    // win - 100, e.g. Team B win 60 gives Team B lose -40.
    [[aWin, aLose], [bWin, bLose], [drawWin, drawLose]].forEach(function (pair) {
      pair[0].addEventListener("input", function () {
        if (loseFromWinSports.indexOf(sportSelect.value) === -1) {
          return;
        }
        var win = intValue(pair[0]);
        if (win !== null) {
          pair[1].value = win - 100;
        }
      });
    });
  });
})();
