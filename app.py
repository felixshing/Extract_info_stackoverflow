import datetime

from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['ekko']
col = db['stackoverflow']

app = Flask(__name__)
CORS(app, resources=r'/*')


def getview(col,times):
    result=col.aggregate([
        {
            '$match': {
                'times': times
            }
        }, {
            '$group': {
                '_id': None,
                'sum': {
                    '$sum': '$views'
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'sum': 1
            }
        }
    ])
    return result

@app.route('/')
def index():
    return "index"

@app.route('/get_data', methods=['GET'])
def get_newest():
    newest = col.find().sort("times", -1)
    votes = col.find().sort("votes", -1)
    #print(votes)
    history = col.find().sort("votes", -1)
    #print(history)
    #views=getview(col)
    #print(views)
    #view_count=col.aggregate()
    top10_newest = []
    top10_votes = []
    top10_history = []

    # The 10 newest Android-related questions
    for flag, li in enumerate(newest):
        if flag <= 9:
            newest_dict = {}
            newest_dict['url'] = li.get("url")
            newest_dict['title'] = li.get('title')
            newest_dict['times'] = li.get("times")
            newest_dict['votes'] = li.get("votes")
            top10_newest.append(newest_dict)

    # The 10 most voted Android-related questions posted in the past week
    votes_flag = 1
    for li in votes:
        current_time = int(
            str((datetime.datetime.now() + datetime.timedelta()).strftime('%Y-%m-%d').replace('-', ''))[-1:])
        # print(current_time,'--------------demo')

        if current_time < 9:
            before_count = -7 + current_time - 2
            fourteen_count = -14 + current_time - 1
        elif current_time >= 9:
            before_count = -1
            fourteen_count = -7
        else:
            before_count = current_time - 9
            fourteen_count = current_time - 14

        beforetime = int(
            (datetime.datetime.now() + datetime.timedelta(days=before_count)).strftime('%Y-%m-%d').replace('-', ''))
        fourteentime = int(
            (datetime.datetime.now() + datetime.timedelta(days=fourteen_count)).strftime('%Y-%m-%d').replace('-', ''))
        times = int(li.get('times').replace('-', ''))
        if fourteentime <= times and times <= beforetime:
            votes_dict = {}
            votes_dict['url'] = li.get("url")
            votes_dict['title'] = li.get('title')
            votes_dict['times'] = li.get("times")
            votes_dict['votes'] = li.get('votes')
            votes_dict['views'] = li.get('views')

            top10_votes.append(votes_dict)
            print(votes_dict)
            if votes_flag == 10:
                break
            votes_flag += 1

    # The 10 most voted Android-related questions posted in the past 30 days
    for flag, li in enumerate(history):
        if flag <= 9:
            onemonth = int(
                (datetime.datetime.now() + datetime.timedelta(days=-30)).strftime('%Y-%m-%d').replace('-', ''))
            history_time = int(li.get('times').replace('-', ''))
            print(history_time)
            if onemonth <= history_time:
                history_dict = {}
                history_dict['url'] = li.get("url")
                history_dict['title'] = li.get('title')
                history_dict['times'] = li.get("times")
                history_dict['votes'] = li.get('votes')
                history_dict['views'] = li.get('views')
                top10_history.append(history_dict)

    #Total views for Android-related questions in the past seven days
    view_dict = {}
    view_data=[]
    view_date=[]
    for i in range(2, 9):
        data = (datetime.datetime.now() + datetime.timedelta(days=-int(i))).strftime('%Y-%m-%d')
        result = getview(col, data)
        for view in result:
            view_dict[data] = view['sum']
    for k, v in view_dict.items():
        view_date.append(k)
        view_data.append(v)
    view_date=view_date[::-1]
    view_data = view_data[::-1]
    view_list=[view_date,view_data]
    #last7_view.append(view_dict)
    return {'code': 1, 'newest': top10_newest, 'votes': top10_votes, 'history': top10_history, 'last7_view': view_list}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port='8000', debug=True)
    get_newest()

