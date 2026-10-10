// Match admin: live calculation of points fields from odds using normalized probabilities.
// For Football and Hockey (3-way with Draw):
//   Normalized prob P(A), P(Draw), P(B).
//   Win points = Math.round(100 - P), Lose points = -Math.round(P).
// For Tennis, Badminton and Cricket (2-way without Draw):
//   Normalized prob P(A), P(B).
//   Win points = Math.round(100 - P), Lose points = -Math.round(P).
//   Draw win and lose points are set to 0.
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

    function floatValue(input) {
      if (!input) return null;
      var val = parseFloat(input.value.trim());
      return (!isNaN(val) && isFinite(val) && val > 1.0) ? val : null;
    }

    function intValue(input) {
      var value = input.value.trim();
      return /^-?\d+$/.test(value) ? parseInt(value, 10) : null;
    }

    function recalculateFromOdds() {
      var oa = floatValue(aOdds);
      var ob = floatValue(bOdds);
      var od = floatValue(drawOdds);
      var isDrawSport = (loseFromWinSports.indexOf(sportSelect.value) !== -1);

      // 3-way sport (Football, Hockey): if all 3 odds available, normalize across all 3
      if (isDrawSport && oa && ob && od) {
        var invA = 1.0 / oa;
        var invD = 1.0 / od;
        var invB = 1.0 / ob;
        var total = invA + invD + invB;
        var pa = (invA / total) * 100.0;
        var pd = (invD / total) * 100.0;
        var pb = (invB / total) * 100.0;
        aWin.value = Math.round(100.0 - pa);
        aLose.value = -Math.round(pa);
        bWin.value = Math.round(100.0 - pb);
        bLose.value = -Math.round(pb);
        drawWin.value = Math.round(100.0 - pd);
        drawLose.value = -Math.round(pd);
        return;
      }

      // 2-way sport (Tennis, Badminton, Cricket): normalize across A and B, set Draw to 0
      if (!isDrawSport && oa && ob) {
        var invA2 = 1.0 / oa;
        var invB2 = 1.0 / ob;
        var total2 = invA2 + invB2;
        var pa2 = (invA2 / total2) * 100.0;
        var pb2 = (invB2 / total2) * 100.0;
        aWin.value = Math.round(100.0 - pa2);
        aLose.value = -Math.round(pa2);
        bWin.value = Math.round(100.0 - pb2);
        bLose.value = -Math.round(pb2);
        drawWin.value = 0;
        drawLose.value = 0;
        return;
      }
    }

    [aOdds, bOdds, drawOdds].forEach(function (inp) {
      if (inp) {
        inp.addEventListener("input", recalculateFromOdds);
      }
    });

    sportSelect.addEventListener("change", recalculateFromOdds);

    // Manual typing into Team A win points for 2-way sports
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

    // 3-way sports: typing into win points fills lose points as win - 100
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
