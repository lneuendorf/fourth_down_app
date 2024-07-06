# Plots/Tables
1. Expectation model
    - Table showing kickers with highest fgoe
3. Kicker Specific Model (for fourth down decision model)
    - probabily plots demonstrating difference in probability against distance
    - Table showing the teams that were most aggressive in going for low probability field goals
    - curve of drafted verse undrafted kickers

# Process:
1. Logistic regression trained for each kick, (or maybe bagged and trained on every 100 kicks) for temporal split
2. Calculate FGPOE at the time of each kick
3. Feed FGPOE, environmental factors, and situational factors into heirachical baysian logistic regression


1. clean up code
2. create and post table of FGPOE