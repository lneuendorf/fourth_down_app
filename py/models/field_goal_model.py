from typing import List
import os

import pandas as pd
import numpy as np

import nfl_data_py as nfl

def probabalistic_oversampling(df_fg, year: int) -> pd.DataFrame:
    """ Oversample field goal attempts to create a binomial distribution
    
    Parameters
        df_fg: pbp dataframe with only field goal attempts
            cols: 'season', 'kick_distance', 'field_goal_made' 
        year: inclusive upper bound on the seasons to include
        
    Returns
        df_fg_oversampled: pbp dataframe with individual field goal attempts
            cols: 'kick_distance', 'field_goal_made'
    """

    df_fg = df_fg[df_fg['season'] <= year]

    df_fg['field_goal_attempt'] = 1

    df_binom = df_fg.groupby('kick_distance').agg({'field_goal_attempt':'count',
                                                   'field_goal_made':'sum'}).reset_index()
    df_binom = (df_binom.sort_values(by='kick_distance', ascending=True)
                        .rename({'field_goal_attempt':'n_attempts',
                                 'field_goal_made':'n_makes'}, axis=1))
    
    df_binom['p'] = df_binom['n_makes'] / df_binom['n_attempts']

    max_attempts = df_binom['n_attempts'].max()

    # Unravel the binomial distribution
    unraveled_rows = None
    for row in df_binom.itertuples(index=False):
        makes = np.tile((row.kick_distance, 1), (int(row.n_makes),1))
        misses = np.tile((row.kick_distance, 0), (int(row.n_attempts - row.n_makes),1))
        if unraveled_rows is None:
            unraveled_rows = np.vstack((makes,misses))
        else:
            unraveled_rows = np.vstack((unraveled_rows, makes,misses))

    df_fg_oversampled = pd.DataFrame(unraveled_rows, columns=['kick_distance','field_goal_made'])

    kick_distances = df_binom['kick_distance'].values


    rows = None
    for dist in range(18,77): # shortest fg is 18 yards, longest is 76
        if dist in kick_distances:
            n_attempts = (df_binom.loc[df_binom['kick_distance'] == dist, 'n_attempts']
                                .reset_index(drop=True).values[0])
        else:
            n_attempts = 0
        n_samples_to_add = max_attempts - n_attempts

        for i in range(n_samples_to_add):
            added_dist = False
            while(not added_dist): #TODO: at something to make sure you dont get stuck here
                dist_to_add = int(np.random.normal(0, 3))
                new_dist = dist + dist_to_add
                if new_dist in kick_distances:
                    added_dist = True
                    df_binom_new_dist = (df_binom.loc[df_binom['kick_distance'] == new_dist]
                                                .reset_index(drop=True))
                    n_attempts = df_binom_new_dist.n_attempts.values[0]
                    p = df_binom_new_dist.p.values[0]
                    field_goal_made = np.random.binomial(1, p)
                    if rows is None:
                        rows = np.array([dist, field_goal_made])
                    else:
                        rows = np.vstack((rows, [dist, field_goal_made]))
        
    df_fg_oversampled = pd.concat([df_fg_oversampled, 
                                   pd.DataFrame(rows, columns=['kick_distance','field_goal_made'])])
    breakpoint()

    df_b = df_fg_oversampled.groupby('kick_distance').agg({'kick_distance':'count','field_goal_made':'sum'}).rename({'kick_distance':'n_attempts'},axis=1).reset_index()

    df_b['p'] = df_b['field_goal_made'] / df_b['n_attempts']
    return df_fg_oversampled

def load_field_goal_pbp_data(years: List, include_enviorment: bool = False) -> pd.DataFrame:
    """ Load field goal data from the nfl_data_py package
    
    Parameters
        years: list of years to load data for
        include_enviorment: boolean to include enviorment data ('roof','surface','temp','wind',
            'stadium')
        
    Returns
        df_fg: pbp dataframe with only field goal attempts
            cols: 'season', 'kick_distance', 'field_goal_made' 
    """

    for year in years:
        if not os.path.exists(f'../../.cache/pbp/season={year}'):
            nfl.cache_pbp(years=[year], alt_path='../../.cache/pbp', downcast=True)

    df_fg = nfl.import_pbp_data(years=years, cache=True, alt_path='../../.cache/pbp', downcast=False)
    df_fg = df_fg[df_fg['field_goal_attempt'] == True]

    df_fg['field_goal_made'] = df_fg['field_goal_result'].apply(lambda x: 1 if x == 'made' else 0)

    cols = ['season','game_id','kicker_player_name','kicker_player_id','kick_distance','field_goal_made']
    df_fg = df_fg[cols]

    if include_enviorment:
        df_schedules = nfl.import_schedules(years=years)
        sched_cols = ['game_id','roof','surface','wind','temp','stadium_id','stadium']
        df_fg = df_fg.merge(df_schedules[sched_cols], on='game_id', how='left')
    
    return df_fg

# if __name__ == '__main__':
#     years = range(2000, 2004)

#     df_fg = load_field_goal_pbp_data(years)

#     probabalistic_oversampling(df_fg, 2004)