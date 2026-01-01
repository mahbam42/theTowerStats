
# Table of Contents

1.  [Fix Styling on Headers](#org87f18bc)
2.  [Add a metric and chart for Free Upgrades by Run](#org8f00ed5)


<a id="org87f18bc"></a>

# TODO Fix Styling on Headers

Override the rules from Foundation's \_base.scss header-color with var(&#x2013;tts-color-text)

    // Headings
      h1, .h1,
      h2, .h2,
      h3, .h3,
      h4, .h4,
      h5, .h5,
      h6, .h6 {
        font-family: $header-font-family;
        font-style: $header-font-style;
        font-weight: $header-font-weight;
        color: $header-color;
        text-rendering: $header-text-rendering;


<a id="org8f00ed5"></a>

# TODO Add a metric and chart for Free Upgrades by Run

Add to chart builder under Economy
Stacked bar chart by type (attack, defense, utility, and total) 

