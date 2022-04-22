from flask import Flask, make_response, render_template, request
from io import BytesIO
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import japanize_matplotlib

app= Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html', \
		title = '総年俸と順位', \
		message = '何年を調べますか？')



@app.route('/result', methods=['POST'])
def result_post():
    year = request.form.get('radio')
    salary_dict = {'2021':1,'2020':2,'2019':4,'2018':5,'2017':6}
    rank_dict = {'2021':1,'2020':2,'2019':3,'2018':4,'2017':5}
   

# 年俸のデータをWEBサイトからとってくる
    url0 ='https://baseball-sokuho.com/nenpoumatome-2018'
    tables0 = pd.read_html(url0)

    df0 = tables0[salary_dict[year]]

# 年俸データ加工
    if salary_dict[year] <= 2:
        year_salary = '総額（万円）'
    elif salary_dict[year] == 4:
        year_salary = '2019年俸総額（億円）'
        df0.loc[9, '球団']= 'オリックス'
    elif salary_dict[year] == 5:
        year_salary = '2018年推定総額'
    elif salary_dict[year] == 6:
        year_salary = '推定'
        df0.columns = df0.columns.droplevel(0)
        df0.loc[3, '球団']= 'ヤクルト'
        df0.loc[4, '球団']= '日本ハム'
        df0.loc[5, '球団']= 'ロッテ'
        df0.loc[6, '球団']= 'オリックス'
        df0.loc[11, '球団']= 'DeNA'
    
        
    df0 = df0.set_index('球団')
    df0.rename(index={'SB': 'ソフトバンク'}, inplace=True)

    # セ・リーグ順位をWEBサイトからとってくる
    url1 ='https://nipponbaseball.web.fc2.com/standings_ce.html'
    tables1 = pd.read_html(url1)
    df1 = tables1[0]

    # パ・リーグ順位をWEBサイトからとってくる
    url2 ='https://nipponbaseball.web.fc2.com/standings_pa.html'
    tables2 = pd.read_html(url2)
    df2 = tables2[0]

    # 球団順位データ加工
    labels_se = []
    juni =  df1.iloc[rank_dict[year], 1:]
    for i in juni:
        if i[0] == '巨':
            labels_se.append('巨人')
        elif i[0] == '阪':
            labels_se.append('阪神')
        elif i[0] == '広':
            labels_se.append('広島')
        elif i[0] == 'ヤ':
            labels_se.append('ヤクルト')
        elif i[0] == 'D':
            labels_se.append('DeNA')
        elif i[0] == '中':
            labels_se.append('中日')
            
    labels_pa = []
    juni =  df2.iloc[rank_dict[year], 1:]
    for i in juni:
        if i[0] == 'ソ':
            labels_pa.append('ソフトバンク')
        elif i[0] == 'オ':
            labels_pa.append('オリックス')
        elif i[0] == '日':
            labels_pa.append('日本ハム')
        elif i[0] == '楽':
            labels_pa.append('楽天')
        elif i[0] == '西':
            labels_pa.append('西武')
        elif i[0] == 'ロ':
            labels_pa.append('ロッテ')


    # 球団順位と総年俸を掛け合わせる
    if salary_dict[year] == 4:
        y_se = [df0.loc[i, year_salary] for i in labels_se]
    else:
        nenpo_kanji_se = [df0.loc[i, year_salary] for i in labels_se]
        y_se = []
        for i in nenpo_kanji_se:
            count = 0
            y1 = ''
            for j in i:
                if count <= 1 :
                    y1 += j
                elif count == 2:
                    j = '.'
                    y1 += j
                else:
                    y1 += j
                    break        
            
                count += 1
            
            y1 = float(y1)     
            y_se.append(y1)
            
    if salary_dict[year] == 4:
        y_pa = [df0.loc[i, year_salary] for i in labels_pa]
    else:
        nenpo_kanji_pa = [df0.loc[i, year_salary] for i in labels_pa]
        y_pa = []
        for i in nenpo_kanji_pa:
            count = 0
            y2 = ''
            for j in i:
                if count <= 1 :
                    y2 += j
                elif count == 2:
                    j = '.'
                    y2 += j
                else:
                    y2 += j
                    break        
            
                count += 1
            
            y2 = float(y2)     
            y_pa.append(y2)
    
    # データを図にする       
    fig, ax = plt.subplots()
    x = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    xlabel = '総年俸(億円)'
    ylabel = '順位(上から1位)'
    y_sepa = y_se + y_pa
    
    ax.barh(x, y_sepa, tick_label=(labels_se+labels_pa))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    fig.suptitle(year+'年')
  

    canvas = FigureCanvasAgg(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    data = png_output.getvalue()

    response = make_response(data)
    response.headers['Content-Type'] = 'image/png'

    return response

if __name__ == '__main__':
    app.debug = False
    app.run()