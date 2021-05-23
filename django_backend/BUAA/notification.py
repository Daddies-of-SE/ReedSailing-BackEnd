from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
import json
import time
import BUAA.utils as utils
# from BUAA.global_var import OnlineClientPool

# clients = OnlineClientPool()
clients = {}

def send_notif(p_id):
    with open('log', 'a') as f :
        f.write('send_botif function: online clients:' + str(clients.keys()) + '\n')
    if p_id in clients :
        p_ws = clients[p_id]
        # p_ws.send(json.dumps([notif], ensure_ascii=False))
        utils.push_all_notif(p_id, p_ws)

class NotificationConsumer(WebsocketConsumer):
    def websocket_connect(self, message) :
        """
        客户端请求链接之后自动触发
        :param message: 消息数据
        """
        # print('请求链接')
        self.accept()  # 建立链接
        self.user_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        # print(f'client user id is {self.user_id}')

        # clients.add(self.user_id, self)
        clients[self.user_id] = self
        # 客户登录时无条件push新通知
        utils.push_all_notif(self.user_id, self)

        with open('log', 'a') as f :
            f.write('In NOtificationConsumer connect, online client is '
                    + str(clients.keys()) + '\n')


    def websocket_receive(self, message) :
        """
        客户端浏览器发送消息来的时候自动触发
        """
        print(message['text'])
        # for test
        # INTERVAL = 5
        # for i in range(3):
        #     text = f'The {i+1}th notification from server'
        #     self.send(text_data=text)
        #     time.sleep(INTERVAL)

        with open('log', 'a') as f :
            f.write('In NOtificationConsumer receive, online client is ' +
                    str(clients.keys()) + '\n')


    def websocket_disconnect(self, message) :
        """
        客户端断开链接之后自动触发
        :param message:
        """
        with open('log', 'a') as f :
            f.write('In NOtificationConsumer disconnect, online client is '
                    + str(clients.keys()) + '\n')
        
        # 客户端断开链接之后 应该将当前客户端对象从列表中移除
        # clients.remove(self.user_id)
        clients.pop(self.user_id)
        raise StopConsumer()  # 主动报异常 无需做处理 内部自动捕获

