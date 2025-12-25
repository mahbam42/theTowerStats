
# Table of Contents

1.  [Chart Taxonomy (Codex-friendly)](#orgc8ed4ab)
    1.  [Rebuild Chart Classifications](#orgb4d62ea)
    2.  [Chart Types](#org5cd4dee)
2.  [On Charts Dashboard, Charts should show by date or by battle log](#orgac914ff):enhancement:
3.  [Filter Charts by Event Dates](#org165404b):enhancement:
4.  [Add Damage Charts/Metrics](#org4870dfc)
5.  [% of total damage by source as stacked bar per battle report](#orgff0e3b7)
6.  [Damage vs Destroyed By stacked bar](#orgff56665)
7.  [Orb Effectiveness](#org6e28475)
8.  [Add Coins from UWs Charts/Metrics](#org2c9286c)
9.  [Add 'Enemies Destroyed' Donut to Charts/Metrics](#orgb2f03a8)
10. [Cash Charts](#org873fa28)
11. [Card Parameter description should replace placeholder unit with current level value](#org98ef99b):enhancement:


<a id="orgc8ed4ab"></a>

# TODO Chart Taxonomy (Codex-friendly)

Think in three axes:

1.  What system does this describe?

2.  What question does it answer?

3.  Is it absolute or relative?

Charts must answer one of:

-   “What did I get?”
-   “Where did damage come from?”
-   “What killed enemies?”

Charts that answer “How should I play?” are out of scope.


<a id="orgb4d62ea"></a>

## Rebuild Chart Classifications

-   Economy (What did this run produce?)
    
    -   Coins
    -   Cash
    -   Cells
    -   Reroll Shards
    
    Examples:
    
    -   Coins by Source
    -   Coins from Ultimate Weapons
    -   Cash Earned per Run
    -   Cash by Source (e.g. Golden Tower, Interest)
    -   Cells Earned per Run

Reroll Shards Earned per Run

-   Damage (Where did damage come from?)
    
    -   Damage by Source (absolute)
    -   Damage Contribution (relative / %)
    
    Examples:
    
    -   Damage by Source (stacked bar)
    -   % of Total Damage by Source (donut or stacked)
    -   Damage vs Enemies Destroyed (comparative)
-   Enemy Destruction (“What actually killed enemies?”)
    Enemy Destruction charts must compute totals from child rows, never from Battle Report totals.
    
    -   Destruction by Source
    -   Enemy Type Distribution
    
    Exanples:
    
    -   Enemies Destroyed by Source (donut + %)
    -   Enemy Type Breakdown (Basic / Fast / Tank / Ranged / Boss)
    -   Destroyed in Spotlight / Golden Bot (as sources, not enemy types)
-   Efficiency
    
    -   Time-normalized metrics
    
    Examples:
    
    -   Coins per Hour
    -   Waves per Hour
    -   Enemies Destroyed per Hour


<a id="org5cd4dee"></a>

## Chart Types

-   Distribution
    Donut, stacked bar
    → must show % explicitly

-   Contribution
    Relative share of a whole
    → requires a derived denominator

-   Absolute Totals
    Bars, timelines
    → no implied comparison

-   Comparative
    Two related metrics side-by-side
    → must share units or be clearly labeled


<a id="orgac914ff"></a>

# TODO On Charts Dashboard, Charts should show by date or by battle log     :enhancement:

Charts would be more clear if they also showed by battle report instead of only daily totals. 


<a id="org165404b"></a>

# TODO Filter Charts by Event Dates     :enhancement:

Events are 14 Days long. The previous event started on 12/09/2025 to 12/22/2025 and the current event is 12/23/2025 to 01/08/2026.

Charts should have a default date range of the current event start to end, buttons to move backward or forward (to end of current), and preserve the current manual date range fields.

Documentation should be updated to reflect this. And a note should be added to the Date Range controls that they coorispond to the 'In Game Events'


<a id="org4870dfc"></a>

# TODO Add Damage Charts/Metrics

-   Total Damage
    take 'damage dealt' as total

Use the following metrics from 'Battle Report':

-   Projectiles Damage	17.94Q

-   Thorn damage	267.27Q

-   Orb Damage	3.36s

-   Land Mine Damage	331.60q

-   Rend Armor Damage	0

-   Death Ray Damage	13.61q

-   Smart Missile Damage	1.79q

-   Inner Land Mine Damage	0

-   Chain Lightning Damage	24.00Q

-   Death Wave Damage	10.62T

-   Swamp Damage	0

-   Black Hole Damage	1.56Q

-   Electrons Damage	0

Note that 'Land Mine Damage' and 'Inner Land Mine Damage' are separate metrics, Land Mine is a defense workshop, ILM is a UW. 


<a id="orgff0e3b7"></a>

# TODO % of total damage by source as stacked bar per battle report


<a id="orgff56665"></a>

# TODO Damage vs Destroyed By stacked bar


<a id="org6e28475"></a>

# TODO Orb Effectiveness

Composite view:

-   Orb Damage

-   Enemies Hit by Orbs

-   Enemies Destroyed by Orbs


<a id="org2c9286c"></a>

# TODO Add Coins from UWs Charts/Metrics

Add a donut chart tracking the following from Battle Reports Utility section. 

-   Coins From Death Wave	165.52K

-   Coins From Golden Tower	4.61M

-   Coins From Black Hole	0

-   Coins From Spotlight	94.30K


<a id="orgb2f03a8"></a>

# TODO Add 'Enemies Destroyed' Donut to Charts/Metrics

Add the following from Battle Report Enemies Destroyed

-   Basic	150877
-   Fast	46543
-   Tank	56081
-   Ranged	38140
-   Boss	349
-   Protector	0
-   Vampires	116
-   Rays	133
-   Scatters	125
-   Saboteur	0
-   Commander	0
-   Overcharge	0

There is an asymmetry found in the game's reported 'total enemies' and 'total elites' that doesn't align with the summed totals of reported enemy types. Therefore we will ignore those metrics and roll our own to avoid misleading charts. This should be clearly stated in the docs. 


<a id="org873fa28"></a>

# TODO Cash Charts

Economy → Cash (Definition)

Cash represents in-run purchasing power.
It is not progression currency and does not persist across runs.

Cash charts answer:

“How much in-run buying power did this run generate, and from where?”

-   Cash Earned (total, absolute)
-   Interest Earned
-   Cash From Golden Tower

Optional (if already parsed):

-   Any other explicit “Cash From X” fields the game exposes later


<a id="org98ef99b"></a>

# IN PROGRESS Card Parameter description should replace placeholder unit with current level value     :enhancement:

-   State "IN PROGRESS" from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 18:59] </span></span>   
    Some work done but not complete

Instead of showing 'for [x] sec' or 'by #%' the description should reflect the current card level values

For example:

-   **Critical Coin "Increase critical chance by +#%":** Should read "Increase critical chance by +\*\*27\*\*%" for level 5
-   **Damage "Increase tower damage by x #":** Should read "Increase tower damage by ****4.00**** #" for level 7/maxed

Card descriptions must be rendered from structured parameter data, not static strings.

Any card description containing placeholder tokens ([x], #, %, sec) must be replaced at render-time with the effective value for the card’s current level. If card level is 0 placeholder is permitted.

The displayed value must be computed using:

-   base value
-   per-level scaling
-   current card level
-   max-level cap (if applicable)

No placeholder text may remain once the computation succeeds.

Completion criteria:

-   No unresolved placeholders remain anywhere in the Cards Dashboard

-   All cards render level-correct values consistently

-   Failure to meet any criterion means the task is incomplete

-   Prompt38Validation.yml accurately marked complete

