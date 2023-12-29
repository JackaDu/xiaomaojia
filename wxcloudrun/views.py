from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import hashlib, time, json, requests


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')

@app.route('/msg', methods=['POST'])
async def receive_msg():
    """
    :return:返回自定义消息
    """

    # 获取请求体参数
    params = request.get_json()
    print(params)
    if 'FromUserName' not in params:
        return ""

    from_user = params['FromUserName']
    to_user = params['ToUserName']
    content = params['Content']
    t = params['CreateTime']
    res = {
        "ToUserName": from_user,
        "FromUserName": to_user,
        "CreateTime": t,
        "MsgType": "text",
        "Content": content
    }
    # 主动回复
    extra_res = {
        "touser": from_user,
        "msgtype": "text",
        "text": {
          "content": content
        }
    }
    await make_extra_reply(extra_res)
    return json.dumps(res, ensure_ascii=False)

async def make_extra_reply(res):
    url = 'http://api.weixin.qq.com/cgi-bin/message/custom/send'
    requests.post(url, json=res)

@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)
