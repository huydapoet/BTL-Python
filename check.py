import pandas as pd
import random
import time
from bs4 import BeautifulSoup as bs
from seleniumbase import SB


def random_delay(min_seconds=5, max_seconds=15):
    time.sleep(random.uniform(min_seconds, max_seconds))


def get(player, stat, extra=False):
    tmp = player.find('td', attrs={'data-stat': stat})
    try:
        tmp = tmp.text
        if extra:
            tmp = tmp.split()[1]
        tmp = tmp.strip()
        if not tmp:
            return None
        return tmp
    except:
        return None


def main():
    all_cols = ['player', 'nationality', 'position', 'team', 'age', 'games', 'games_starts', 'minutes', 'minutes_90s',
                'goals', 'assists', 'goals_assists', 'goals_pens', 'pens_made', 'pens_att', 'cards_yellow', 'cards_red',
                'goals_per90', 'assists_per90', 'goals_assists_per90', 'goals_pens_per90', 'goals_assists_pens_per90',
                'gk_goals_against', 'gk_goals_against_per90', 'gk_shots_on_target_against', 'gk_saves', 'gk_save_pct',
                'gk_wins', 'gk_ties', 'gk_losses', 'gk_clean_sheets', 'gk_clean_sheets_pct', 'gk_pens_att',
                'gk_pens_allowed', 'gk_pens_saved', 'gk_pens_missed', 'gk_pens_save_pct', 'shots', 'shots_on_target',
                'shots_on_target_pct', 'shots_per90', 'shots_on_target_per90', 'goals_per_shot',
                'goals_per_shot_on_target', 'minutes_per_game', 'minutes_pct', 'minutes_per_start', 'games_complete',
                'games_subs', 'minutes_per_sub', 'unused_subs', 'points_per_game', 'on_goals_for', 'on_goals_against',
                'plus_minus', 'plus_minus_per90', 'plus_minus_wowy', 'cards_yellow_red', 'fouls', 'fouled', 'offsides',
                'crosses', 'interceptions', 'tackles_won', 'pens_won', 'pens_conceded', 'own_goals']

    all_url = []
    auto_rename_map = {}

    with SB(uc=True) as sb:
        url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        sb.uc_open_with_reconnect(url)
        sb.uc_gui_click_captcha()
        random_delay(3, 7)

        html = sb.get_page_source()
        soup = bs(html, 'html.parser')

        try:
            container = soup.find('li', attrs={'class': 'full hasmore'})
            for link in container.find_all('a'):
                all_url.append(link.get('href'))
        except Exception as e:
            print(f"cant not take the urls due to {e}")
            return

        rows = []
        for url in all_url:
            random_delay()
            sb.uc_open_with_reconnect(f'https://fbref.com{url}')
            sb.uc_gui_click_captcha()

            random_delay(3, 7)
            html = sb.get_page_source()
            soup = bs(html, "html.parser")

            tables = soup.find_all("table")
            player_table = None
            for tbl in tables:
                if tbl.find("th", attrs={"data-stat": "player"}):
                    player_table = tbl
                    break

            if not player_table:
                continue

            table_head = player_table.find('thead')
            if table_head:
                rows_head = table_head.find_all('tr')
                print(len(rows_head))
                if len(rows_head) == 1:
                    for th in rows_head[0].find_all('th', attrs={'data-stat': True}):
                        stat_code = th.get('data-stat')
                        display_name = th.text.strip()
                        if stat_code not in auto_rename_map or len(display_name) > len(auto_rename_map[stat_code]):
                            auto_rename_map[stat_code] = display_name

                elif len(rows_head) >= 2:
                    top_row = rows_head[0].find_all('th')
                    bottom_row = rows_head[1].find_all('th')
                    bottom_idx = 0

                    for th in top_row:
                        prefix = th.text.strip()
                        colspan = int(th.get('colspan', 1))

                        for i in range(colspan):
                            if bottom_idx < len(bottom_row):
                                bot_th = bottom_row[bottom_idx]
                                bot_stat = bot_th.get('data-stat')
                                bot_text = bot_th.text.strip()

                                if bot_stat:
                                    full_name = f"{prefix} {bot_text}".strip() if prefix else bot_text

                                    if bot_stat not in auto_rename_map:
                                        auto_rename_map[bot_stat] = full_name
                                    elif len(full_name) > len(auto_rename_map[bot_stat]):
                                        auto_rename_map[bot_stat] = full_name
                            bottom_idx += 1

            players = player_table.find_all('tr')
            for player in players:
                try:
                    time_val = player.find('td', attrs={'data-stat': 'minutes_90s'}).text.split('.')
                    if int(time_val[0]) >= 1:
                        rows.append({i: get(player, i, True if i == 'nationality' else False) for i in all_cols})
                except:
                    continue

    if rows:
        data_all = pd.DataFrame(rows, columns=all_cols)
        data_all = data_all.groupby('player').first().reset_index()

        if auto_rename_map:
            data_all = data_all.rename(columns=auto_rename_map)

        data_all.fillna("N/a").to_csv('data.csv', index=False, encoding='utf-8-sig')
        print('DONE')
    else:
        print('No data collected')


if __name__ == "__main__":
    main()