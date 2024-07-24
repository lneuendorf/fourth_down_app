# TODO
- define pressure situations

- do we just predict win probability added or win probability after play?
- make website and post some articles? (hugo)

# Plots/Tables
- plot of fgpoe of last 100 or 50 over time
1. Expectation model
    - Table showing kickers with highest fgoe
3. Kicker Specific Model (for fourth down decision model)
    - probabily plots demonstrating difference in probability against distance
    - Table showing the teams that were most aggressive in going for low probability field goals
    - curve of drafted verse undrafted kickers
3. Win Probability Model
    - plot win probab verse win probability added, and then lines of run verse pass on first down play, when is it more optimal to run

# Process:
1. Logistic regression trained for each kick, (or maybe bagged and trained on every 100 kicks) for temporal split
2. Calculate FGPOE at the time of each kick
3. Feed FGPOE, environmental factors, and situational factors into heirachical baysian logistic regression
