
# Table of Contents

1.  [On Cards Dashboard Add a Total Cards Progress Widget under preset tags](#orgc5a0440)
2.  [On Battle History Dashboard](#orgf4432fa)


<a id="orgc5a0440"></a>

# TODO On Cards Dashboard Add a Total Cards Progress Widget under preset tags

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<tbody>
<tr>
<td class="org-left">Cards Remaining:</td>
<td class="org-left">{#}</td>
<td class="org-left">Total Cards:</td>
<td class="org-left">{#}</td>
</tr>


<tr>
<td class="org-left">Maxed Cards</td>
<td class="org-left">{#}</td>
<td class="org-left">Progress:</td>
<td class="org-left">{%}</td>
</tr>


<tr>
<td class="org-left">Gems Needed</td>
<td class="org-left">{#}</td>
<td class="org-left">Events:</td>
<td class="org-left">{#}</td>
</tr>
</tbody>
</table>

{#} represents calculated values based on app data
{%} represents precentage calculations

Currently there are 31 Cards and you need to collect 80 copies to max level 7, so Total Cards will equal 2480. Cards Remaining will be calculated by Total Cards minus Card Copies collected.

Maxed Cards will be a count of how many cards are 32/32 Collected

Progress will be calculated by Total Cards minus Cards Remaing divided by Total Cards

Gems Needed will be calculated by Cards Remaining divided by 10 (round up) times 200. Cards are typically purchased 10 at a time for 200 gems.

Events will be calculated by Gems Needed divided by 1600. There is a standard Event Mission to buy 80 Cards, so 200 gems times 8 gives us 1600.


<a id="orgf4432fa"></a>

# TODO On Battle History Dashboard

Add a Highest Wave table under Filters.

Shows Each Tier with a run logged and the highest wave reached. Below that show the top 3 Tournament Logs.

Note: Currently Tier 21 is the Highest possible. But to avoid clutter we'll base the table on Tiers logged in this app. 

