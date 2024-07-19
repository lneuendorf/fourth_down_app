from typing import List
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import re

# Sleep for 3 hours for less internet traffic
import time
time.sleep(3 * 60 * 60)

# Initialize tqdm with pandas
tqdm.pandas()

def get_response(season:int, game_type:str, week:int, away_teams:List[str], home_teams:List[str], recursive_call:bool=False):
    game_type_dict = {
        'REG': [f'week-{week}',f'week-{week}-2'],
        'WC': ['wildcard-weekend','wildcard-weekend-2'],
        'DIV': ['divisional-playoffs','divisional-playoffs-2'], 
        'CON': ['conf-championships','%20conf-championships','conf-championships-2'],
        'SB': ['superbowl','superbowl-2']
    }
        
    for game_type_full in game_type_dict[game_type]:
        for home_team in home_teams:
            for away_team in away_teams:
                url = f'https://www.nflweather.com/games/{season}/{game_type_full}/{away_team}-at-{home_team}'
                response = requests.get(url)
                if "404 Page Not Found" not in response.text:
                    return response
        
    # retry with home and away team names flipped
    if not recursive_call:
        response = get_response(season, game_type, week, home_teams, away_teams, recursive_call=True)

    if response is not None and "404 Page Not Found" not in response.text:
        return response

    return None
                        
def get_weather_descriptions(season:int, game_type:str, week:int, away_team:List[str], home_team:List[str]):        
    
    response = get_response(season, game_type, week, away_team, home_team)

    if response is None:
        return None, None, None, None, None, None, None, None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    weather_titles = soup.find_all('h3', class_='text-center my-2 weather-title')

    data = dict(kickoff_weather=None, q2_weather=None, q3_weather=None, q4_weather=None, 
                kickoff_visibility=None, q2_visibility=None, q3_visibility=None, q4_visibility=None)
    
    for weather_title in weather_titles:
        if 'Kickoff' in weather_title.text:
            quarter = 'kickoff'
        elif 'Q2' in weather_title.text:
            quarter = 'q2'
        elif 'Q3' in weather_title.text:
            quarter = 'q3'
        elif 'Q4' in weather_title.text:
            quarter = 'q4'

        # Find the weather description
        weather_div = weather_title.find_parent('div', class_='col-6 col-xl-12 col-xxl-6 text-center')
        weather_span = weather_div.find('span') if weather_div else None
        weather = weather_span.text.strip() if weather_span else None
        data[quarter + '_weather'] = weather

        # Find the visibility description
        parent_weather_div = weather_div.find_parent('div', class_='d-flex flex-xl-column flex-xxl-row my-3')
        next_weather_div = parent_weather_div.find_next_sibling('div', class_='d-flex flex-wrap mt-auto weather-data-container')
        for p_tag in next_weather_div.find_all('p', class_='weather-data'):
            if 'Visibility' in p_tag.text:
                visibility = re.search(r'\d+', p_tag.find('span').next_sibling.strip())
                if visibility:
                    visibility = int(visibility.group())
                data[quarter + '_visibility'] = visibility

    return data.get('kickoff_weather'), data.get('q2_weather'), data.get('q3_weather'), data.get('q4_weather'), \
            data.get('kickoff_visibility'), data.get('q2_visibility'), data.get('q3_visibility'), data.get('q4_visibility')

df_weather = pd.read_pickle('../data/df_weather.pkl')

cols = ['kickoff_weather','q2_weather','q3_weather','q4_weather','kickoff_visibility','q2_visibility','q3_visibility','q4_visibility']
df_weather[cols] = df_weather.progress_apply(
    lambda x: pd.Series(get_weather_descriptions(x['season'],x['game_type'] , x['week'], x['away_team_name'], x['home_team_name'])),
    axis=1
)

df_weather.to_pickle('../data/df_weather_updtd.pkl')