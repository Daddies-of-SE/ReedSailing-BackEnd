from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
import json

clients = {}

class ChatConsumer(WebsocketConsumer):
    def websocket_connect(self, message) :
        """
        客户端请求链接之后自动触发
        :param message: 消息数据
        """
        # print('请求链接')
        self.accept()  # 建立链接
        self.user_id = message
        clients[self.user_id] = self

    def websocket_receive(self, message) :
        """
        客户端浏览器发送消息来的时候自动触发
        :param message: 消息数据  {'type': 'websocket.receive', 'text': '你好啊 美女'}
        """
        print(message)
        text = 'The server received: ' + message.get('text')
        self.send(text_data=text)

    def websocket_disconnect(self, message) :
        """
        客户端断开链接之后自动触发
        :param message:
        """
        # 客户端断开链接之后 应该将当前客户端对象从列表中移除
        clients.pop(self.user_id)
        raise StopConsumer()  # 主动报异常 无需做处理 内部自动捕获