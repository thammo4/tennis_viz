# -*- coding: utf-8 -*-
import altair as alt
import altair_viewer
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

## path to repo with relevant data
## ( https://github.com/JeffSackmann/tennis_atp )
data_prefix = 'https://github.com/JeffSackmann/tennis_atp/'

player = 'Roger Federer';
player = 'Andy Roddick';


# 'https://github.com/JeffSackmann/tennis_atp/blob/master/atp_matches_' + str(y) + '.csv'



player_slams = []
for y in range(2003,2022):
    ## load matches and reduce to the target player, in first four rounds at slams
    # matches = pd.read_csv(data_prefix + 'atp_matches_' + str(y) + '.csv')
    matches = pd.read_csv("https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_" + str(y) + ".csv");

    pmatches =  matches.loc[(matches['winner_name'] == player) | (matches['loser_name'] == player)]
    first_rounds = ['R128', 'R64', 'R32', 'R16']
    tmatches = pmatches.loc[(pmatches['tourney_level'] == 'G') & (pmatches['round'].isin(first_rounds))]
    
    ## get DR (dominance ratio: RPW / SPL) components for each match for the target player
    tmatches['pSvPt'] = tmatches.apply(lambda row: row.w_svpt 
                                       if row.winner_name == player else row.l_svpt, axis=1)
    tmatches['pSPW'] = tmatches.apply(lambda row: row['w_1stWon'] + row['w_2ndWon']
                                       if row.winner_name == player else row['l_1stWon'] + row['l_2ndWon'], axis=1)
    tmatches['pRetPt'] = tmatches.apply(lambda row: row.l_svpt 
                                       if row.winner_name == player else row.w_svpt, axis=1)
    tmatches['pRPW'] = tmatches.apply(lambda row: (row['l_svpt'] - row['l_1stWon'] - row['l_2ndWon'])
                                       if row.winner_name == player 
                                       else (row['w_svpt'] - row['w_1stWon'] - row['w_2ndWon']), axis=1)
    
    ## list of slams from that year:
    slams = set(tmatches['tourney_id'].tolist())

    for slam in slams:
        ## check if player won this tournament (not [yet] using in this viz)
        titles = pmatches.loc[(pmatches['winner_name'] == player) & (pmatches['round'] == 'F') & (pmatches['tourney_id'] == slam)]
        won_tourney = 1 if len(titles) == 1 else 0
        ## get matches from this tournament and calculate aggregate DR
        smatches = tmatches.loc[pmatches['tourney_id'] == slam]
        slam_total = smatches.sum(axis=0)
        rpw = slam_total['pRPW'].item() / slam_total['pRetPt'].item()
        spw = slam_total['pSPW'].item() / slam_total['pSvPt'].item()
        dr = rpw / (1 - spw)
        row = [smatches.tail(1)['tourney_name'].item(), smatches.tail(1)['tourney_date'].item(), dr, won_tourney] 
        player_slams.append(row)                                                             
    
## add 2021 wimbledon, not yet in the tennis_atp data
player_slams.append(['Wimbledon', 20210628, 1.38, 0])

## sort slams ascending by date
player_slams = sorted(player_slams, key=lambda x: x[1])
    
df = pd.DataFrame(player_slams, columns=['Tourney', 'Date', 'DR', 'Title'])

df.astype({'DR': 'float',
           'Title': 'int'
                }).dtypes

slam_abvs = {'Wimbledon': 'Wimb',
             'US Open': 'USO',
             'Us Open': 'USO',
             'Australian Open': 'AO',
             'Roland Garros': 'RG'
             }
df['FullName'] = df.apply(lambda row: str(row['Date'])[:4] + ' ' + slam_abvs[row['Tourney']], axis=1)

## store list in *date* order for the chart to use:
x_sort = df['FullName'].tolist()

## subset of the data with only tournaments where he won the title, for second layer
titles = df.loc[df['Title'] == 1]

## line chart with all tournaments
line = alt.Chart(df).mark_line(point=True).encode(
    alt.X('FullName',
          sort=x_sort,
          axis=alt.Axis(title='Tournament (first four rounds)')),
    alt.Y('DR',
          axis=alt.Axis(title='Dominance Ratio'),
          scale=alt.Scale(domain=(0.8,2.5))),
)
    
## mark larger, different-colored points for tournaments that he won
points = alt.Chart(titles).mark_point(filled=True, size=200, color='orange').encode(
    alt.X('FullName',
          sort=x_sort),
    alt.Y('DR')
)
    
# (line + points).save('output/federer_slam34343434_dr.html')
(line+points).show();
(line + points).save('output/roddick.html')