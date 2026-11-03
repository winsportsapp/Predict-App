"""
Evergreen Sports Insights Data Catalog
=======================================
Static, original sports analysis, rules, and tactical guides for WinSports.
Requires zero database models, tables, or migrations.
"""

from typing import Any, Dict, List, Optional

ARTICLES_DATA: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. CRICKET: Powerplay, Middle, Death Overs
    # -------------------------------------------------------------------------
    {
        "slug": "cricket-powerplay-middle-death-overs",
        "sport": "cricket",
        "sport_display": "Cricket",
        "sport_icon": "🏏",
        "title": "Understanding Powerplay, Middle Overs, and Death Overs in Limited-Overs Cricket",
        "summary": "An analytical breakdown of the three distinct phases in 20-over and 50-over cricket, fielding restrictions, run rate dynamics, and phase-specific bowling execution.",
        "read_time": "6 min read",
        "published_date": "October 2026",
        "updated_date": "November 2026",
        "author": "WinSports Editorial Team",
        "key_takeaways": [
            "The Powerplay (overs 1-6 in T20) provides an offensive window where only two fielders are outside the circle, heavily rewarding aerial lofted drives.",
            "Middle overs (overs 7-15) are won through low dot-ball percentages, smart 1s and 2s, and spin bowling control rather than reckless boundary hunting.",
            "Death overs (overs 16-20) require millimeter bowling precision—wide yorkers, slower-ball bouncers, and boundary-arc protection against high-intent finishers.",
        ],
        "content_html": """
<p class="lead text-secondary">
  Limited-overs cricket is often viewed as a continuous race against the scoreboard, but successful teams treat every innings as three distinct tactical phases: the Powerplay, the Middle Overs, and the Death Overs. Each phase operates under unique fielding constraints, mathematical leverage, and specialist player roles.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">1. The Powerplay (Overs 1 to 6 in T20s / 1 to 10 in ODIs)</h2>
<p>
  The initial phase of an innings is governed by strict fielding restrictions designed to encourage boundary hitting. In a T20 match, only two fielders are permitted outside the 30-yard fielding circle during the first six overs.
</p>
<ul>
  <li><strong>Batting Objectives:</strong> Batters seek to exploit the vacant outfield by lofting the ball over the infield. Statistical studies indicate that teams posting 50 or more runs for the loss of one wicket or fewer in the Powerplay secure a decisive win probability advantage.</li>
  <li><strong>Bowling Countermeasures:</strong> Captains deploy swing bowlers who attack the stumps and slip cordons. Securing two or more wickets in the Powerplay forces the batting side to play defensively in the subsequent phase.</li>
  <li><strong>Pacing:</strong> Modern opening batters aim for strike rates exceeding 140 immediately, departing from older doctrines that encouraged conservative sighting overs.</li>
</ul>

<div class="table-responsive my-4">
  <table class="table table-bordered table-sm align-middle bg-white">
    <thead class="table-light">
      <tr>
        <th>Phase</th>
        <th>Overs (T20)</th>
        <th>Fielders Outside Circle</th>
        <th>Primary Tactical Focus</th>
      </tr>
    </thead>
    <tbody class="small">
      <tr>
        <td><strong>Powerplay</strong></td>
        <td>1 – 6</td>
        <td>Maximum 2</td>
        <td>Aerial exploitation of vacant outfield; early wicket-taking swing bowling.</td>
      </tr>
      <tr>
        <td><strong>Middle Overs</strong></td>
        <td>7 – 15</td>
        <td>Maximum 5</td>
        <td>Strike rotation (1s &amp; 2s), spin control, and boundary-to-dot ratio containment.</td>
      </tr>
      <tr>
        <td><strong>Death Overs</strong></td>
        <td>16 – 20</td>
        <td>Maximum 5</td>
        <td>Maximum boundary intent, yorker precision, slower variations, and boundary protection.</td>
      </tr>
    </tbody>
  </table>
</div>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">2. The Middle Overs: Strike Rotation and Dot-Ball Pressure</h2>
<p>
  Once five fielders retreat to the boundary cushions, finding the boundary rope becomes statistically harder. Attempting to hit boundaries every delivery against deep boundary riders carries heightened risk.
</p>
<ul>
  <li><strong>The Value of Spin:</strong> Wrist-spinners and finger-spinners dominate this window. By varying trajectories, arm speeds, and spin directions, they deny batters the pace needed to clear long boundaries.</li>
  <li><strong>Eliminating Dot Balls:</strong> Elite batting pairs focus on keeping the dot-ball percentage below 30%. Converting singles into twos and rotating the strike forces bowlers to continually alter their line and field settings.</li>
  <li><strong>Favorable Match-ups:</strong> Batting units strategically target specific bowler-batter match-ups, such as positioning a left-handed batter against off-spin to hit with the natural turning arc.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">3. The Death Overs: High-Leverage Execution</h2>
<p>
  The final 30 deliveries of a T20 innings represent the most intense mathematical segment of the game. Scoring rates regularly exceed 11 to 14 runs per over as batting sides commit to full attacking intent.
</p>
<ul>
  <li><strong>Batting Mechanics:</strong> Batters clear their front leg, utilize scoops, reverse-laps, and pre-meditated boundary arcs to defeat defensive field placements.</li>
  <li><strong>Bowling Precision:</strong> Death-bowling specialists rely on millimeter accuracy:
    <ul>
      <li><strong>Wide Yorkers:</strong> Delivered just inside the tramline outside off stump, denying batters leverage to hit across the line toward the leg side.</li>
      <li><strong>Change of Pace:</strong> Back-of-the-hand slower balls and knuckleballs that disrupt the batter's swing timing.</li>
      <li><strong>Defensive Boundary Angles:</strong> Setting deep point, long-off, long-on, deep mid-wicket, and deep square leg to protect against the batter's strongest hitting zones.</li>
    </ul>
  </li>
</ul>

<div class="card card-body bg-light-subtle border rounded-3 my-4">
  <h3 class="h6 fw-bold text-dark mb-2">💡 Practical Analytical Takeaway</h3>
  <p class="small text-muted mb-0">
    When evaluating an upcoming cricket fixture, check team rosters for genuine phase specialists. A team with world-class top-order batters but mediocre death bowlers frequently surrenders matches in the final four overs, regardless of their early lead.
  </p>
</div>
""",
        "related_slugs": [
            "cricket-format-strategies-t20-odi-test",
            "football-tactics-pressing-possession-counterattack",
        ],
    },

    # -------------------------------------------------------------------------
    # 2. CRICKET: Format Strategies Across T20, ODI, and Test
    # -------------------------------------------------------------------------
    {
        "slug": "cricket-format-strategies-t20-odi-test",
        "sport": "cricket",
        "sport_display": "Cricket",
        "sport_icon": "🏏",
        "title": "How Batting and Bowling Strategies Change Across T20, ODI, and Test Formats",
        "summary": "Contrasting the patient attrition of red-ball cricket with the aggressive boundary hunting of T20s and the paced progression of ODIs, including pitch wear and field geometry.",
        "read_time": "7 min read",
        "published_date": "October 2026",
        "updated_date": "November 2026",
        "author": "WinSports Editorial Team",
        "key_takeaways": [
            "Test cricket tests defensive technique, stamina, and patience over five days, where wickets are prioritized over run rates.",
            "One Day Internationals (ODIs) balance consolidation with acceleration, demanding steady partnerships and an explosive final 10-over surge.",
            "T20 cricket is governed by boundary percentages and risk-adjusted strike rates, where preserving wickets is secondary to maintaining run velocity.",
        ],
        "content_html": """
<p class="lead text-secondary">
  Cricket is unique among global sports in featuring three distinct official international formats: five-day Test matches, 50-over One Day Internationals (ODIs), and 20-over Twenty20 (T20) contests. While the fundamental equipment and pitch dimensions remain identical, the tactical principles required to win differ radically across formats.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">1. Test Cricket: The War of Attrition (Red Ball)</h2>
<p>
  Test cricket is played over five days with up to 450 overs of potential play. Because there are no limits on overs per bowler and no fielding restrictions, defensive stamina and psychological discipline are paramount.
</p>
<ul>
  <li><strong>Batting Philosophy:</strong> Batters prioritize survival and leaving deliveries outside off stump to wear down the opposition bowling attack. Scoring at 3 to 4 runs per over is fully acceptable if wickets remain intact.</li>
  <li><strong>Bowling Field Placements:</strong> Captains employ multiple slip catchers, gullies, and short legs. Bowlers bowl a consistent "corridor of uncertainty" on fourth-stump line for hours, waiting for a single lapse in concentration.</li>
  <li><strong>Pitch Deterioration:</strong> Test pitches undergo continuous mechanical wear. Surfaces that offer true bounce on Day 1 often break up, crack, and offer uneven bounce or sharp spin on Days 4 and 5.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">2. ODI Cricket: The 50-Over Narrative Arc (White Ball)</h2>
<p>
  With 300 deliveries per side, ODIs require structured pacing. A premature collapse can end a contest early, yet batting too conservatively leaves teams well below modern par scores (300+ runs).
</p>
<ul>
  <li><strong>Phase Progression:</strong> Teams generally divide 50 overs into three acts: building a stable platform during the first 10 overs (Powerplay 1), steadily accumulating at 5.5 to 6 runs per over through overs 11–40 (Powerplay 2), and launching an aggressive assault during overs 41–50 (Powerplay 3).</li>
  <li><strong>The Middle-Overs Balancing Act:</strong> Wickets in hand are vital. Losing 4 or 5 wickets before the 35th over prevents the lower order from launching a high-risk finish at the death.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">3. T20 Cricket: Velocity Over Preservation</h2>
<p>
  With only 120 deliveries available, the opportunity cost of facing a dot ball is severe. Batters are expected to attack from their opening deliveries, and consuming balls without scoring is statistically penalized.
</p>
<ul>
  <li><strong>Wicket Value:</strong> A lost wicket in T20 cricket is rarely fatal if the incoming batter maintains the team's scoring momentum. Modern analytics value a 30-run innings off 16 balls far higher than a 50-run innings off 45 balls.</li>
  <li><strong>Bowling Tactics:</strong> Defensive bowling (denying boundaries through cutters and wide lines) is just as valuable as taking wickets, as stringing together 2 or 3 quiet overs creates unbearable scoreboard pressure.</li>
</ul>

<div class="table-responsive my-4">
  <table class="table table-bordered table-sm align-middle bg-white">
    <thead class="table-light">
      <tr>
        <th>Attribute</th>
        <th>Test Cricket</th>
        <th>ODI Cricket</th>
        <th>T20 Cricket</th>
      </tr>
    </thead>
    <tbody class="small">
      <tr>
        <td><strong>Ball Color</strong></td>
        <td>Red (or Pink for Day/Night)</td>
        <td>White (two balls per innings)</td>
        <td>White (one ball per innings)</td>
      </tr>
      <tr>
        <td><strong>Primary Objective</strong></td>
        <td>Take 20 opponent wickets</td>
        <td>Score higher across 50 overs</td>
        <td>Maximize runs across 120 balls</td>
      </tr>
      <tr>
        <td><strong>Target Strike Rate</strong></td>
        <td>45 – 65</td>
        <td>85 – 115</td>
        <td>140 – 180+</td>
      </tr>
      <tr>
        <td><strong>Field Aggression</strong></td>
        <td>Attacking catchers in close</td>
        <td>Balanced ring &amp; boundary</td>
        <td>Deep boundary protection</td>
      </tr>
    </tbody>
  </table>
</div>
""",
        "related_slugs": [
            "cricket-powerplay-middle-death-overs",
            "tennis-court-surfaces-clay-grass-hard-court-styles",
        ],
    },

    # -------------------------------------------------------------------------
    # 3. FOOTBALL: Formations 4-3-3, 4-4-2, 3-5-2
    # -------------------------------------------------------------------------
    {
        "slug": "football-formations-433-442-352-tactics",
        "sport": "football",
        "sport_display": "Football",
        "sport_icon": "⚽",
        "title": "Understanding Football Formations: The Tactical Dynamics of 4-3-3, 4-4-2, and 3-5-2",
        "summary": "A detailed guide to structural strengths, transitional shapes in possession vs out of possession, and how modern football managers exploit half-spaces.",
        "read_time": "6 min read",
        "published_date": "October 2026",
        "updated_date": "November 2026",
        "author": "WinSports Editorial Team",
        "key_takeaways": [
            "Formations represent starting defensive positions rather than rigid molds; modern teams transform dynamically when attacking.",
            "The 4-3-3 provides natural triangular passing lanes and wide overloads, but relies heavily on a disciplined central defensive pivot.",
            "The 4-4-2 creates a compact two-bank defensive block, while the 3-5-2 relies on high-stamina wing-backs to supply width at both ends.",
        ],
        "content_html": """
<p class="lead text-secondary">
  In modern football, formations are often summarized as simple numbers on television graphics: 4-3-3, 4-4-2, or 3-5-2. In elite match play, however, formations are fluid frameworks that adapt depending on whether a team possesses the ball or is defending without it.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">1. The 4-3-3: Geometric Triangles and Wide Dominance</h2>
<p>
  Popularized by modern European heavyweights and tactical systems prioritizing positional play, the 4-3-3 uses a back four, a three-man midfield (typically one holding pivot and two attacking eights), and three forwards.
</p>
<ul>
  <li><strong>Strengths:</strong> Creates natural passing triangles across every sector of the pitch, allowing teams to circulate possession effortlessly. Wingers can stay wide to stretch opponent defenses or cut inside to shoot.</li>
  <li><strong>Tactical Transformation:</strong> In possession, one full-back often steps into midfield ("inverted full-back") to create a 3-2-4-1 attacking structure, guarding against counter-attacks while overloading central channels.</li>
  <li><strong>Vulnerabilities:</strong> If the central defensive midfielder is isolated or caught out of position, large pockets of space appear in front of the central defenders.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">2. The 4-4-2: Compact Defense and Dual Strikers</h2>
<p>
  The traditional staple of British and continental football, the 4-4-2 features two banks of four players with two central strikers.
</p>
<ul>
  <li><strong>Strengths:</strong> Outstanding horizontal and vertical defensive compactness. When defending in a mid or low block, two flat lines of four deny passing lanes through the middle, forcing attackers out wide into harmless crossing areas.</li>
  <li><strong>Striker Dynamics:</strong> Two forwards allow direct hold-up play, flick-ons, and channel running without requiring heavy midfield runners.</li>
  <li><strong>Vulnerabilities:</strong> With only two central midfielders, a 4-4-2 can be numerically overrun (3 versus 2) by teams playing a three-man midfield.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">3. The 3-5-2 (or 5-3-2 in Defense): Central Fortress and Wing-Back Engine</h2>
<p>
  Featuring three central defenders and two wing-backs who roam the entire length of the flanks, the 3-5-2 provides tremendous defensive resilience combined with central midfield presence.
</p>
<ul>
  <li><strong>Strengths:</strong> Three central defenders provide absolute aerial dominance in the penalty box and nullify two-striker systems. In midfield, three central players matched with two forwards ensure numerical parity everywhere.</li>
  <li><strong>The Wing-Back Requirement:</strong> Wing-backs must possess world-class stamina. In attack, they provide all the team's width; in defense, they tuck in alongside the center-backs to form a five-man wall.</li>
  <li><strong>Vulnerabilities:</strong> If an opponent breaks quickly into the wide channels before the wing-backs can recover, the space behind them is severely exposed.</li>
</ul>

<div class="table-responsive my-4">
  <table class="table table-bordered table-sm align-middle bg-white">
    <thead class="table-light">
      <tr>
        <th>Formation</th>
        <th>Primary Strength</th>
        <th>Primary Weakness</th>
        <th>Key Specialist Role</th>
      </tr>
    </thead>
    <tbody class="small">
      <tr>
        <td><strong>4-3-3</strong></td>
        <td>Wide passing triangles, wing overloads</td>
        <td>Space behind fullbacks on transition</td>
        <td>Single defensive midfield pivot (No. 6)</td>
      </tr>
      <tr>
        <td><strong>4-4-2</strong></td>
        <td>Zonal compactness, twin forward threat</td>
        <td>Numerical inferiority in central midfield</td>
        <td>Box-to-box central midfielders</td>
      </tr>
      <tr>
        <td><strong>3-5-2</strong></td>
        <td>Central defensive security, dual strikers</td>
        <td>Wide channels vulnerable on quick counters</td>
        <td>High-stamina dynamic wing-backs</td>
      </tr>
    </tbody>
  </table>
</div>
""",
        "related_slugs": [
            "football-tactics-pressing-possession-counterattack",
            "hockey-positions-formations-team-roles",
        ],
    },

    # -------------------------------------------------------------------------
    # 4. FOOTBALL: Pressing, Possession, Counter-Attack
    # -------------------------------------------------------------------------
    {
        "slug": "football-tactics-pressing-possession-counterattack",
        "sport": "football",
        "sport_display": "Football",
        "sport_icon": "⚽",
        "title": "Pressing, Possession, and Counter-Attacking: How Modern Football Tactics Differ",
        "summary": "Deconstructing high gegenpressing, mid-block traps, low compact blocks, passes per defensive action (PPDA), and the crucial concept of rest defense.",
        "read_time": "6 min read",
        "published_date": "October 2026",
        "updated_date": "November 2026",
        "author": "WinSports Editorial Team",
        "key_takeaways": [
            "High pressing aims to win the ball within 5 to 7 seconds of turnover, forcing errors close to the opponent's goal.",
            "Possession percentage is a misleading metric; possession without vertical penetration often exposes a team to sudden transition goals.",
            "Rest defense—the structural positioning of non-attacking defenders while their team is on the attack—determines counter-attack vulnerability.",
        ],
        "content_html": """
<p class="lead text-secondary">
  A common misconception in casual football analysis is equating high possession statistics directly with match dominance. In reality, modern football is determined by transitional speed, pressing efficiency, and spatial control rather than raw ball retention.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">1. Pressing Systems: High Press vs. Mid Block vs. Low Block</h2>
<p>
  How a team acts when the opponent has the ball sets the entire tempo of a match:
</p>
<ul>
  <li><strong>Gegenpressing (Counter-Pressing):</strong> The instant a team loses possession, nearby players aggressively swarm the ball carrier for 5 to 7 seconds. The rationale is simple: the opponent has just won the ball, has not yet organized their attacking shape, and is at their most vulnerable. Winning the ball back high creates immediate high-xG scoring chances.</li>
  <li><strong>Mid-Block Traps:</strong> Rather than chasing defenders near the opposing penalty box, the team sets up a disciplined shape around the halfway line. They intentionally leave passing lanes open to specific opposing players, then spring a coordinated trap to win possession in midfield.</li>
  <li><strong>Low Block:</strong> Teams position all outfield players deep within their own defensive third, creating congested layers in front of their goal. Space in behind is completely denied, forcing opponents into low-percentage long-range shots or crosses against physical central defenders.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">2. Quantifying Pressing with PPDA</h2>
<p>
  Tactical analysts measure pressing intensity using <strong>PPDA (Passes Per Defensive Action)</strong>. It calculates how many passes an opponent makes in their defensive and middle thirds before the defending team makes a tackle, interception, challenge, or foul.
</p>
<ul>
  <li><strong>Low PPDA (Under 8–10):</strong> Represents relentless, suffocating pressing high up the pitch.</li>
  <li><strong>High PPDA (Above 15–18):</strong> Represents a patient, passive defensive block that prefers holding shape over individual ball challenges.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">3. The Decisive Concept of "Rest Defense"</h2>
<p>
  When a team commits 6 or 7 players forward during sustained possession, what happens to the remaining players?
</p>
<p>
  <strong>Rest Defense</strong> describes the positioning of the center-backs and defensive midfielder while their own team attacks. Elite sides maintain a 3-2 or 2-3 rest defense shape behind the ball. If their positioning is careless, a single turnover allows a quick counter-attacking team with rapid wingers to score in two passes.
</p>

<div class="card card-body bg-light-subtle border rounded-3 my-4">
  <h3 class="h6 fw-bold text-dark mb-2">💡 Match Analysis Rule</h3>
  <p class="small text-muted mb-0">
    Never evaluate a match pick purely on possession percentages. A team with 38% possession that generates 4 high-speed counter-attacks against an unorganized rest defense will consistently generate higher quality chances than a team circulating 65% sterile possession around the perimeter.
  </p>
</div>
""",
        "related_slugs": [
            "football-formations-433-442-352-tactics",
            "cricket-powerplay-middle-death-overs",
        ],
    },

    # -------------------------------------------------------------------------
    # 5. TENNIS: Court Surfaces and Playing Styles
    # -------------------------------------------------------------------------
    {
        "slug": "tennis-court-surfaces-clay-grass-hard-court-styles",
        "sport": "tennis",
        "sport_display": "Tennis",
        "sport_icon": "🎾",
        "title": "How Tennis Court Surfaces Influence Playing Style: Grass, Clay, and Hard Courts",
        "summary": "Comparing ball bounce, friction coefficients, sliding mechanics, rally lengths, and why surface specialists dominate on clay vs fast grass or neutral hard courts.",
        "read_time": "6 min read",
        "published_date": "October 2026",
        "updated_date": "November 2026",
        "author": "WinSports Editorial Team",
        "key_takeaways": [
            "Clay courts produce high friction that slows ball speed while generating steep, heavy top-spin bounce, rewarding patient baseline attrition.",
            "Grass courts offer low friction and low skid, heavily rewarding big serves, slice shots, and attacking first strikes.",
            "Hard courts provide a standardized, true bounce that balances aggressive serving with baseline defense, reflected in the Court Pace Index (CPI).",
        ],
        "content_html": """
<p class="lead text-secondary">
  In tennis, no external variable shapes player performance more than the court surface beneath their shoes. A player capable of reaching the finals on Wimbledon's fast grass can struggle to survive early rounds on the grinding red clay of Roland Garros. Understanding court surfaces is the cornerstone of tennis sports analysis.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">1. Red Clay Courts: High Bounce and Physical Attrition</h2>
<p>
  Constructed from crushed brick layered over limestone, clay courts feature high surface friction and loose top dressing.
</p>
<ul>
  <li><strong>Ball Aerodynamics &amp; Bounce:</strong> When a tennis ball strikes red clay, the rough surface absorbs significant horizontal velocity while kicking the ball high into the air. Flat, hard serves lose much of their bite, whereas heavy top-spin forehands leap well above a player's shoulder height.</li>
  <li><strong>Movement Mechanics:</strong> Players slide into their groundstrokes before contacting the ball. Mastering the controlled slide requires specialized footwork, lower-body balance, and patience.</li>
  <li><strong>Rally Duration:</strong> Rallies average 6 to 10 shots, demanding exceptional cardiovascular endurance and mental stamina. Direct winners are rare, making unforced errors the primary decider of points.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">2. Grass Courts: Low Skid and First-Strike Speed</h2>
<p>
  Grass courts (such as Wimbledon) represent the traditional, fastest surface in tennis, constructed with perennial ryegrass on firm soil.
</p>
<ul>
  <li><strong>Ball Aerodynamics &amp; Bounce:</strong> Grass blades provide low friction. The ball skids off the turf with minimal loss of horizontal pace, staying low to the ground. Slice backhands stay ankle-height, making them difficult to lift over the net.</li>
  <li><strong>Movement Mechanics:</strong> Sliding on grass is dangerous due to traction loss. Players must maintain small, balanced footsteps and a lower center of gravity.</li>
  <li><strong>Tactical Premium:</strong> First-serve efficiency and aggressive net rushes are rewarded. Points frequently finish within 1 to 3 shots, making a single service break enough to decide a set.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">3. Hard Courts: True Bounce and Universal Balance</h2>
<p>
  Featuring asphalt or concrete bases coated with layered acrylic and silica sand, hard courts (such as the Australian Open and US Open) provide a neutral benchmark.
</p>
<ul>
  <li><strong>Consistency:</strong> Hard courts produce the most uniform, predictable bounce in the sport. There are no bad bounces from surface divots or sliding clay mounds.</li>
  <li><strong>Court Pace Index (CPI):</strong> Hard courts can be customized by altering the quantity of sand mixed into the acrylic finish. Faster hard courts (high CPI) favor aggressive servers, while medium-slow hard courts (medium CPI) allow baseline counter-punchers to track down every ball.</li>
</ul>

<div class="table-responsive my-4">
  <table class="table table-bordered table-sm align-middle bg-white">
    <thead class="table-light">
      <tr>
        <th>Surface</th>
        <th>Ball Speed</th>
        <th>Bounce Height</th>
        <th>Favored Playing Style</th>
        <th>Flagship Tournament</th>
      </tr>
    </thead>
    <tbody class="small">
      <tr>
        <td><strong>Clay</strong></td>
        <td>Slow</td>
        <td>High &amp; Heavy</td>
        <td>Baseline counter-punchers, heavy top-spin</td>
        <td>Roland Garros (French Open)</td>
      </tr>
      <tr>
        <td><strong>Grass</strong></td>
        <td>Fast</td>
        <td>Low &amp; Skidding</td>
        <td>Big servers, serve-and-volley, slice masters</td>
        <td>Wimbledon</td>
      </tr>
      <tr>
        <td><strong>Hard</strong></td>
        <td>Medium to Fast</td>
        <td>Medium &amp; True</td>
        <td>All-court players, aggressive baseliners</td>
        <td>US Open / Australian Open</td>
      </tr>
    </tbody>
  </table>
</div>
""",
        "related_slugs": [
            "tennis-rules-scoring-tiebreak-match-formats",
            "badminton-singles-vs-doubles-tactics-rules",
        ],
    },

    # -------------------------------------------------------------------------
    # 6. TENNIS: Scoring, Tiebreaks, and Match Formats
    # -------------------------------------------------------------------------
    {
        "slug": "tennis-rules-scoring-tiebreak-match-formats",
        "sport": "tennis",
        "sport_display": "Tennis",
        "sport_icon": "🎾",
        "title": "Understanding Tennis Scoring, Deuce, Tiebreaks, and Match Formats",
        "summary": "An explanation of tennis scoring mechanics from 15-love to advantage, standard 7-point tiebreaks, 10-point champions tiebreaks, and Grand Slam match formats.",
        "read_time": "5 min read",
        "published_date": "October 2026",
        "updated_date": "November 2026",
        "author": "WinSports Editorial Team",
        "key_takeaways": [
            "Game scoring operates on a non-linear 15, 30, 40 system, requiring a 2-point margin after Deuce (Advantage).",
            "A standard tiebreak is played at 6-6 in a set, won by the first player to reach 7 points with a 2-point margin.",
            "All four Grand Slams now use a decisive 10-point Champions Tiebreak when sets reach 6-6 in the final deciding set.",
        ],
        "content_html": """
<p class="lead text-secondary">
  Tennis possesses one of the most distinctive scoring architectures in international sport. Unlike continuous clock-based sports or simple point tallies, tennis matches are divided into a hierarchical ladder of Points, Games, and Sets. Understanding this structure reveals why momentum shifts so dramatically in tight contests.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">1. Game Scoring: From Love to Deuce</h2>
<p>
  A single game is scored with historical terminology:
</p>
<ul>
  <li><strong>0 Points:</strong> Love</li>
  <li><strong>1st Point:</strong> 15</li>
  <li><strong>2nd Point:</strong> 30</li>
  <li><strong>3rd Point:</strong> 40</li>
  <li><strong>4th Point:</strong> Game (unless tied 40-40)</li>
</ul>
<p>
  When both players reach 40-40, the score is called <strong>Deuce</strong>. From Deuce, a player must win two consecutive points to secure the game: the first point confers <strong>Advantage (Ad)</strong>, and winning the subsequent point closes the game. If the opposing player wins the point, the score returns to Deuce.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">2. Sets and Breaks of Serve</h2>
<p>
  To win a standard set, a player must win at least 6 games while maintaining a 2-game advantage (e.g., 6-4 or 7-5). Because serving confers an inherent offensive advantage, each player is expected to hold their own service games. Winning an opponent's service game is known as a <strong>Service Break</strong>, which usually decides the set.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">3. The Standard 7-Point Tiebreak</h2>
<p>
  If both players win 6 games each (6-6), a tiebreak is played to prevent endless sets:
</p>
<ul>
  <li>Points are scored numerically: 1, 2, 3, etc.</li>
  <li>The player whose turn it was to serve starts the tiebreak by serving <strong>one point</strong> from the deuce court.</li>
  <li>Thereafter, each player serves <strong>two consecutive points</strong>, alternating ends of the court every 6 points.</li>
  <li>The first player to reach <strong>7 points</strong> with a minimum lead of 2 points wins the tiebreak (e.g., 7-4 or 9-7) and takes the set 7-6.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">4. The 10-Point Deciding Set Tiebreak</h2>
<p>
  Historically, deciding sets at Grand Slams (Set 5 in men's, Set 3 in women's) continued indefinitely until someone won by two clear games (e.g., 12-10). To protect player health and television schedules, all four Grand Slams (Australian Open, Roland Garros, Wimbledon, US Open) unified under a <strong>10-point Champions Tiebreak</strong> at 6-6 in the final set. The first player to 10 points with a 2-point margin wins the match.
</p>

<div class="card card-body bg-light-subtle border rounded-3 my-4">
  <h3 class="h6 fw-bold text-dark mb-2">💡 Statistical Insight: Break Point Conversion</h3>
  <p class="small text-muted mb-0">
    A tennis player can win more total points than their opponent across a three-set match and still lose the contest. Tennis rewards clutch execution on high-leverage points: break points saved and break points converted are the ultimate analytical metrics.
  </p>
</div>
""",
        "related_slugs": [
            "tennis-court-surfaces-clay-grass-hard-court-styles",
            "badminton-singles-vs-doubles-tactics-rules",
        ],
    },

    # -------------------------------------------------------------------------
    # 7. BADMINTON: Singles vs Doubles Tactics and Rules
    # -------------------------------------------------------------------------
    {
        "slug": "badminton-singles-vs-doubles-tactics-rules",
        "sport": "badminton",
        "sport_display": "Badminton",
        "sport_icon": "🏸",
        "title": "Singles vs Doubles Badminton: Key Tactical Differences and Court Movement",
        "summary": "Why singles demands deep lunges, baseline clears, and endurance while doubles revolves around service line domination, flat driving, and rear-court smashes.",
        "read_time": "5 min read",
        "published_date": "October 2026",
        "updated_date": "November 2026",
        "author": "WinSports Editorial Team",
        "key_takeaways": [
            "Singles courts are long and narrow, placing a premium on corner-to-corner stamina, deceptive drop shots, and recovery to the central base.",
            "Doubles courts use the wider tramlines, prioritizing rapid flat exchanges, net dominance, and front-and-back attacking formations.",
            "Service dynamics differ fundamentally: high defensive clears rule singles, while low tight spinning serves dominate doubles.",
        ],
        "content_html": """
<p class="lead text-secondary">
  Badminton is officially the fastest racket sport in the world, with shuttlecock smash speeds clocked in excess of 400 km/h. While singles and doubles share the same net height and basic scoring (best of 3 sets to 21 points), they are tactical polar opposites.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">1. Court Geometry and Boundary Differences</h2>
<p>
  The badminton court incorporates two sets of lines:
</p>
<ul>
  <li><strong>Singles:</strong> Played on the narrower inner sideline ("long and narrow"). The back boundary line is in play during both serve and open rallies.</li>
  <li><strong>Doubles:</strong> Uses the wider outer tramlines for the entire rally. However, on the serve, the rear service court is shortened by the inner back line ("short and wide").</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">2. Service Dynamics: High Clears vs. Flat Tape Serves</h2>
<ul>
  <li><strong>Singles Serving:</strong> Servers frequently deliver deep, high service clears targeting the back boundary line. This pushes the receiver back, preventing an immediate offensive smash and allowing the server to settle into their base position.</li>
  <li><strong>Doubles Serving:</strong> High serves are almost never used in professional doubles because an opposing attacker will immediately smash down from the rear court. Instead, servers deliver razor-sharp low serves skimming millimeters above the tape into the front service line, initiating an immediate flat battle.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">3. Movement and Formations: Center Base vs. Rotational System</h2>
<ul>
  <li><strong>Singles Movement:</strong> A singles player must guard all four court corners alone (covering approximately 35 square meters). After every stroke, the player immediately recovers to the "T" base position in the center of the court. Movement relies on deep lunges and scissor kicks.</li>
  <li><strong>Doubles Rotational Formations:</strong>
    <ul>
      <li><strong>Attack (Front-and-Back):</strong> When attacking, one player controls the front net area to intercept weak lifts, while the partner stays in the rear court to unleash continuous downward smashes.</li>
      <li><strong>Defense (Side-by-Side):</strong> When forced to lift the shuttle defensively, the pair splits side-by-side, each guarding half the court to defend incoming smashes.</li>
    </ul>
  </li>
</ul>

<div class="table-responsive my-4">
  <table class="table table-bordered table-sm align-middle bg-white">
    <thead class="table-light">
      <tr>
        <th>Attribute</th>
        <th>Singles Badminton</th>
        <th>Doubles Badminton</th>
      </tr>
    </thead>
    <tbody class="small">
      <tr>
        <td><strong>Court Width</strong></td>
        <td>Narrow (inner sidelines)</td>
        <td>Wide (outer sidelines)</td>
      </tr>
      <tr>
        <td><strong>Primary Serve</strong></td>
        <td>High defensive clear to rear</td>
        <td>Low spinning flick to service T</td>
      </tr>
      <tr>
        <td><strong>Tactical Rhythm</strong></td>
        <td>Patience, construction, endurance</td>
        <td>Aggressive speed, flat drives, net kills</td>
      </tr>
      <tr>
        <td><strong>Formation</strong></td>
        <td>Individual central base recovery</td>
        <td>Front-and-back attack / Side-by-side defense</td>
      </tr>
    </tbody>
  </table>
</div>
""",
        "related_slugs": [
            "badminton-shots-court-positioning-footwork",
            "tennis-rules-scoring-tiebreak-match-formats",
        ],
    },

    # -------------------------------------------------------------------------
    # 8. BADMINTON: Shots and Court Positioning
    # -------------------------------------------------------------------------
    {
        "slug": "badminton-shots-court-positioning-footwork",
        "sport": "badminton",
        "sport_display": "Badminton",
        "sport_icon": "🏸",
        "title": "Understanding Badminton Shots and Court Positioning: Clears, Drops, Smashes, and Net Kills",
        "summary": "The essential anatomy of offensive and defensive badminton strokes, base position recovery, split-step timing, and anticipating opponent angles.",
        "read_time": "5 min read",
        "published_date": "October 2026",
        "updated_date": "November 2026",
        "author": "WinSports Editorial Team",
        "key_takeaways": [
            "The smash provides the ultimate offensive finish, but relying on smashes without setting up the rally leads to exhaustion and unforced errors.",
            "Drop shots and net slices change shuttle momentum and force opponents into desperate upward lifts.",
            "The split-step is the fundamental biomechanical secret of elite footwork, resetting balance a millisecond before the opponent strikes.",
        ],
        "content_html": """
<p class="lead text-secondary">
  At the professional level, a feather shuttlecock responds dynamically to racket face angles, racket-head velocity, and slice. A player who masters stroke variation can manipulate their opponent like a puppet on a string, creating openings to terminate rallies with surgical precision.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">1. The Primary Stroke Repertoire</h2>
<ul>
  <li><strong>The Clear (High &amp; Attacking):</strong> Delivered from the rear court high and deep to the opponent's baseline. A defensive clear buys recovery time; an attacking clear travels with a flatter, faster trajectory over an opponent's reach.</li>
  <li><strong>The Drop Shot (Fast &amp; Sliced):</strong> Struck with identical body mechanics to a smash, but contact is softened or sliced to make the shuttle die immediately after clearing the net tape. This forces an opponent to lunge forward from the rear court.</li>
  <li><strong>The Smash:</strong> The primary point-finishing stroke, hit with maximum downward velocity. Top players use jump smashes to generate steeper angles that bounce before the receiver can position their racket.</li>
  <li><strong>The Net Tumbler / Hairpin:</strong> Struck close to the tape, inducing the shuttle to tumble end-over-end across the net cord. If executed with spin, the shuttle is impossible to attack downward.</li>
  <li><strong>The Net Kill / Tap:</strong> Intercepting a loose, high shuttlecock directly at the tape with a sharp wrist flick, terminating the point instantly.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">2. Footwork: The Biomechanics of the Split-Step</h2>
<p>
  Exceptional shot-making is meaningless without elite footwork. The cornerstone of court movement is the <strong>Split-Step</strong>:
</p>
<p>
  Just as an opponent is about to make contact with the shuttle, the defending player performs a tiny hop, landing with feet slightly wider than shoulder-width and weight on the balls of the feet. This pre-stretches the leg muscles like springs, allowing instant explosive acceleration in any of the four directional vectors.
</p>

<div class="card card-body bg-light-subtle border rounded-3 my-4">
  <h3 class="h6 fw-bold text-dark mb-2">💡 Strategic Principle</h3>
  <p class="small text-muted mb-0">
    Badminton rallies are won by creating diagonal distance. If an opponent plays a drop shot to your front-left corner, return with a cross-court lift to their rear-right corner, forcing them to cover the maximum 8.4-meter diagonal expanse of the court.
  </p>
</div>
""",
        "related_slugs": [
            "badminton-singles-vs-doubles-tactics-rules",
            "tennis-court-surfaces-clay-grass-hard-court-styles",
        ],
    },

    # -------------------------------------------------------------------------
    # 9. HOCKEY: Positions, Formations, and Team Roles
    # -------------------------------------------------------------------------
    {
        "slug": "hockey-positions-formations-team-roles",
        "sport": "hockey",
        "sport_display": "Hockey",
        "sport_icon": "🏑",
        "title": "Understanding Field Hockey Positions, Formations, and Team Roles",
        "summary": "Breaking down modern 4-3-3 and 3-4-3 hockey formations, sweeper/center-back roles, midfield link play, and striker pressing angles in modern international hockey.",
        "read_time": "6 min read",
        "published_date": "October 2026",
        "updated_date": "November 2026",
        "author": "WinSports Editorial Team",
        "key_takeaways": [
            "Modern field hockey is played on water-based synthetic turf at blistering pace, making 3D stick skills and aerial scoops fundamental weapons.",
            "Rolling substitutions allow teams to maintain 100% anaerobic pressing intensity across all four 15-minute quarters.",
            "Formations like the 4-3-3 and 3-4-3 rely on central midfield pivots who link defensive ball distribution with rapid circle penetrations.",
        ],
        "content_html": """
<p class="lead text-secondary">
  Field hockey has evolved into one of the most high-octane team sports on the planet. The introduction of water-based synthetic turf pitches, the elimination of the offside rule, and the self-pass innovation have transformed hockey into a relentless display of physical conditioning, spatial awareness, and stick execution.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">1. Modern Positions and Tactical Responsibilities</h2>
<ul>
  <li><strong>Goalkeeper (GK):</strong> Equipped with lightweight foam kickers, leg guards, and hand protectors, the hockey goalkeeper is the vocal director of defense and the last line against 130 km/h drag flicks.</li>
  <li><strong>Center-Backs / Sweeper:</strong> Responsible for defensive marking inside the 23-meter area and launching attacks with pinpoint overhead aerial passes that bypass congested midfield lines.</li>
  <li><strong>Fullbacks / Wing-Backs:</strong> Provide wide passing outlets during build-up play and defend against baseline entries by opponent wingers.</li>
  <li><strong>Holding Midfield Pivot:</strong> The tactical anchor who shields the central defensive zone, breaks up transitions, and distributes the ball laterally to create overloads.</li>
  <li><strong>Attacking Midfielders (Inside Forwards):</strong> High-agility playmakers who penetrate the attacking 23-meter zone, win penalty corners, and deliver disguised slap-passes into the circle.</li>
  <li><strong>Strikers / Forwards:</strong> Operate inside the shooting circle ("the D") looking for deflections, rebounds, and shooting angles. Because goals can only be scored from inside the circle, their positional movement is critical.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">2. Common Formations: 4-3-3 vs. 3-4-3</h2>
<p>
  Modern hockey teams generally employ fluid four-line formations:
</p>
<ul>
  <li><strong>4-3-3:</strong> Provides defensive security through two central defenders and two fullbacks, allowing three midfielders to press aggressively.</li>
  <li><strong>3-4-3:</strong> Sacrifices one defender to add an extra player in midfield, ideal for teams that wish to control possession and press the opposition inside their own half.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">3. Rolling Substitutions and Anaerobic Shifts</h2>
<p>
  Unlike association football where substituted players cannot return, field hockey permits unlimited <strong>rolling substitutions</strong>. Midfielders and strikers regularly sprint for 4 to 6 minutes at full capacity before rotating off to rest, ensuring maximum pressing intensity across all four 15-minute quarters.
</p>

<div class="card card-body bg-light-subtle border rounded-3 my-4">
  <h3 class="h6 fw-bold text-dark mb-2">💡 Circle Penetration Metric</h3>
  <p class="small text-muted mb-0">
    In hockey analysis, the number of "Circle Entries" is the strongest leading indicator of goal output. Because goals cannot be scored from outside the shooting circle, teams that win the circle-entry count win approximately 78% of international matches.
  </p>
</div>
""",
        "related_slugs": [
            "hockey-rules-penalty-corners-cards-shootouts",
            "football-formations-433-442-352-tactics",
        ],
    },

    # -------------------------------------------------------------------------
    # 10. HOCKEY: Penalty Corners, Cards, and Shootouts
    # -------------------------------------------------------------------------
    {
        "slug": "hockey-rules-penalty-corners-cards-shootouts",
        "sport": "hockey",
        "sport_display": "Hockey",
        "sport_icon": "🏑",
        "title": "How Modern Field Hockey Works: Penalty Corners, Cards, Self-Pass, and Shootouts",
        "summary": "A clear guide to the most exciting rules in modern hockey—from drag flick mechanics in penalty corners to green/yellow card suspensions, self-pass speed, and 8-second 1v1 shootouts.",
        "read_time": "6 min read",
        "published_date": "October 2026",
        "updated_date": "November 2026",
        "author": "WinSports Editorial Team",
        "key_takeaways": [
            "Penalty Corners are the highest-percentage scoring set piece in hockey, executed through precise injection, stopping, and 120+ km/h drag flicks.",
            "Cards carry progressive timed sin-bin penalties: Green (2-minute suspension), Yellow (5 or 10 minutes), and Red (permanent expulsion).",
            "Tied knockout matches are decided by an exhilarating 8-second 1-on-1 penalty shootout starting from the 23-meter line rather than static strokes.",
        ],
        "content_html": """
<p class="lead text-secondary">
  Field hockey rules have undergone progressive modernisation by the International Hockey Federation (FIH) to enhance match speed, eliminate dead time, and maximize spectator excitement. From the drag flick set piece to timed sin-bin suspensions and 1-on-1 shootouts, modern hockey rules create continuous drama.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">1. The Penalty Corner (PC): Anatomy of Hockey's Deadliest Weapon</h2>
<p>
  Awarded for an unintentional foul by a defender inside the shooting circle or an intentional foul inside the 23-meter area, the Penalty Corner is the game's premier set piece:
</p>
<ul>
  <li><strong>The Setup:</strong> The attacking team positions players around the top of the shooting circle. Up to four defenders and one goalkeeper position themselves behind the back boundary line inside the goal.</li>
  <li><strong>The Execution:</strong>
    <ol>
      <li><strong>Injection:</strong> An attacker pushes the ball from a designated mark on the backline to the top of the circle.</li>
      <li><strong>Stop:</strong> A designated stopper traps the ball cleanly outside the circle before rolling it inside (a legal requirement for scoring).</li>
      <li><strong>The Drag Flick:</strong> A specialist drag-flicker scoops and slings the ball with rotational body torque toward the goal at speeds exceeding 120 km/h, aiming for the top corners where defensive runners cannot reach.</li>
    </ol>
  </li>
  <li><strong>Defensive Bravery:</strong> The four defending runners rush out wearing face masks and protective gloves to block the shot, making the PC one of the most courageous duels in world sport.</li>
</ul>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">2. Disciplinary Cards: Timed Sin-Bin Penalties</h2>
<p>
  Unlike football's two-card system, hockey uses three progressive colored cards:
</p>
<div class="table-responsive my-3">
  <table class="table table-bordered table-sm align-middle bg-white">
    <thead class="table-light">
      <tr>
        <th>Card</th>
        <th>Penalty Duration</th>
        <th>Infraction Severity</th>
      </tr>
    </thead>
    <tbody class="small">
      <tr>
        <td><span class="badge text-bg-success">Green Card</span></td>
        <td><strong>2 Minutes</strong> temporary suspension</td>
        <td>Minor tactical fouls, dissent, or failure to retreat 5 meters on free hits.</td>
      </tr>
      <tr>
        <td><span class="badge text-bg-warning text-dark">Yellow Card</span></td>
        <td><strong>5 or 10 Minutes</strong> temporary suspension</td>
        <td>Cynical fouls, dangerous physical tackles, or repeated green-card offences.</td>
      </tr>
      <tr>
        <td><span class="badge text-bg-danger">Red Card</span></td>
        <td><strong>Permanent Ejection</strong> from match</td>
        <td>Violent conduct or deliberate dangerous foul play. Team plays a man down for remainder.</td>
      </tr>
    </tbody>
  </table>
</div>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">3. The Self-Pass Innovation</h2>
<p>
  Introduced to eliminate defensive delays, the <strong>Self-Pass</strong> rule permits a player taking a free hit to tap the ball to themselves and immediately start dribbling. Defending teams cannot intentionally delay restarts, keeping ball-in-play time near 70% of match duration.
</p>

<h2 class="h4 fw-bold text-dark mt-4 mb-3">4. The 8-Second 1v1 Penalty Shootout</h2>
<p>
  When knockout tournament matches finish level at the end of regulation time, hockey uses a dynamic 1-on-1 shootout rather than static penalty strokes:
</p>
<ul>
  <li>An attacker starts with the ball on the 23-meter line.</li>
  <li>On the umpire's whistle, the attacker has exactly <strong>8 seconds</strong> to dribble, spin, and score against the opposing goalkeeper.</li>
  <li>The goalkeeper can advance off their line to dive, tackle, or slide, creating an athletic cat-and-mouse duel. Five rounds are taken per team, followed by sudden death if scores remain level.</li>
</ul>
""",
        "related_slugs": [
            "hockey-positions-formations-team-roles",
            "football-tactics-pressing-possession-counterattack",
        ],
    },
]

# Lookup dictionary by slug for O(1) access
ARTICLES_BY_SLUG: Dict[str, Dict[str, Any]] = {
    article["slug"]: article for article in ARTICLES_DATA
}


def get_all_articles() -> List[Dict[str, Any]]:
    """Return all evergreen sports insights articles."""
    return ARTICLES_DATA


def get_article_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Return a single article by its unique slug, or None if not found."""
    return ARTICLES_BY_SLUG.get(slug)


def get_articles_by_sport(sport_slug: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return articles filtered by sport slug, or all if sport_slug is empty/None."""
    if not sport_slug or sport_slug == "all":
        return ARTICLES_DATA
    return [a for a in ARTICLES_DATA if a["sport"] == sport_slug.lower()]


def get_sports_categories() -> List[Dict[str, Any]]:
    """Return a list of available sports categories with counts for tabs/filters."""
    sports = [
        {"slug": "all", "name": "All Sports", "icon": "🌐"},
        {"slug": "cricket", "name": "Cricket", "icon": "🏏"},
        {"slug": "football", "name": "Football", "icon": "⚽"},
        {"slug": "tennis", "name": "Tennis", "icon": "🎾"},
        {"slug": "badminton", "name": "Badminton", "icon": "🏸"},
        {"slug": "hockey", "name": "Hockey", "icon": "🏑"},
    ]
    for s in sports:
        if s["slug"] == "all":
            s["count"] = len(ARTICLES_DATA)
        else:
            s["count"] = len([a for a in ARTICLES_DATA if a["sport"] == s["slug"]])
    return sports
